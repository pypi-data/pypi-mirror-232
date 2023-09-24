'''
utils used for transitioning to new component-descriptor v2

see: https://github.com/gardener/component-spec
'''

import dataclasses
import enum
import hashlib
import io
import json
import logging
import os
import shutil
import tempfile
import typing
import yaml

import dacite
import deprecated

import gci.componentmodel as cm
import gci.oci

import ccc.oci
import ci.util
import oci.model as om
import version

logger = logging.getLogger(__name__)


def _normalise_component_name(component_name:str) -> str:
    return component_name.lower()  # oci-spec allows only lowercase


def ensure_is_v2(
    component_descriptor_v2: cm.ComponentDescriptor,
):
    schema_version = component_descriptor_v2.meta.schemaVersion
    if not schema_version is cm.SchemaVersion.V2:
        raise RuntimeError(f'unsupported component-descriptor-version: {schema_version=}')


def _target_oci_ref(
    component: gci.componentmodel.Component,
    component_ref: gci.componentmodel.ComponentReference=None,
    component_version: str=None,
):

    if not component_ref:
        component_ref = component
        component_name = component_ref.name
    else:
        component_name = component_ref.componentName

    component_name = _normalise_component_name(component_name)
    component_version = component_ref.version

    # last ctx-repo is target-repository
    last_ctx_repo = component.repositoryContexts[-1]

    return last_ctx_repo.component_version_oci_ref(
        name=component_name,
        version=component_version,
    )


def download_component_descriptor_v2(
    component_name: str,
    component_version: str,
    ctx_repo_base_url: str=None,
    ctx_repo: cm.RepositoryContext=None,
    absent_ok: bool=False,
    cache_dir: str=None,
    validation_mode: cm.ValidationMode=cm.ValidationMode.NONE,
):
    if not (bool(ctx_repo_base_url) ^ bool(ctx_repo)):
        raise ValueError('exactly one of ctx_repo_base_url, ctx_repo must be passed')
    if ctx_repo_base_url:
        logger.warning('passing ctx_repo_base_url is deprecated - pass ctx_repo instead!')
        ctx_repo = cm.OciRepositoryContext(baseUrl=ctx_repo_base_url)

    if not isinstance(ctx_repo, cm.OciRepositoryContext):
        raise NotImplementedError(ctx_repo)

    ctx_repo: cm.OciRepositoryContext

    target_ref = ctx_repo.component_version_oci_ref(
        name=component_name,
        version=component_version,
    )

    if cache_dir:
        descriptor_path = os.path.join(
            cache_dir,
            ctx_repo.oci_ref.replace('/', '-'),
            f'{component_name}-{component_version}',
        )
        if os.path.isfile(descriptor_path):
            return cm.ComponentDescriptor.from_dict(
                ci.util.parse_yaml_file(descriptor_path),
                validation_mode=validation_mode,
            )
        else:
            base_dir = os.path.dirname(descriptor_path)
            os.makedirs(name=base_dir, exist_ok=True)

    component_descriptor =  retrieve_component_descriptor_from_oci_ref(
        manifest_oci_image_ref=target_ref,
        absent_ok=absent_ok,
        validation_mode=validation_mode,
    )

    if absent_ok and not component_descriptor:
        return None

    if cache_dir:
        try:
            f = tempfile.NamedTemporaryFile(mode='w', delete=False)
            # write to tempfile, followed by a mv to avoid collisions through concurrent
            # processes or threads (assuming mv is an atomic operation)
            yaml.dump(
                data=dataclasses.asdict(component_descriptor),
                Dumper=cm.EnumValueYamlDumper,
                stream=f.file,
            )
            f.close() # need to close filehandle for NT
            shutil.move(f.name, descriptor_path)
        except:
            os.unlink(f.name)
            raise

    return component_descriptor


class UploadMode(enum.Enum):
    SKIP = 'skip'
    FAIL = 'fail'
    OVERWRITE = 'overwrite'


def write_component_descriptor_to_dir(
    component_descriptor: gci.componentmodel.ComponentDescriptor,
    cache_dir: str,
    on_exist=UploadMode.SKIP,
    ctx_repo_base_url: str=None, # if none, use current from component-descriptor
    ctx_repo: cm.RepositoryContext=None,
):
    if not os.path.isdir(cache_dir):
        raise ValueError(f'not a directory: {cache_dir=}')

    if ctx_repo_base_url:
        logger.warning('passing ctx_repo_base_url is deprectead - pass ctx_repo instead')

    if not ctx_repo_base_url and not ctx_repo:
        ctx_repo_base_url = component_descriptor.component.current_repository_ctx().oci_ref
    elif ctx_repo:
        if not isinstance(ctx_repo, cm.OciRepositoryContext):
            raise NotImplementedError(ctx_repo)
        ctx_repo: cm.OciRepositoryContext

        ctx_repo_base_url = ctx_repo.oci_ref

    component = component_descriptor.component
    descriptor_path = os.path.join(
        cache_dir,
        ctx_repo_base_url.replace('/', '-'),
        f'{component.name}-{component.version}',
    )

    if os.path.isfile(descriptor_path):
        if on_exist is UploadMode.SKIP:
            return component_descriptor,
        elif on_exist is UploadMode.FAIL:
            raise ValueError(f'already exists: {descriptor_path=}, but overwrite not allowed')
        elif on_exist is UploadMode.OVERWRITE:
            pass
        else:
            raise NotImplementedError(on_exist)

    if not os.path.isdir((pdir := os.path.dirname(descriptor_path))):
        os.makedirs(pdir, exist_ok=True)

    try:
        f = tempfile.NamedTemporaryFile(mode='w', delete=False)
        # write to tempfile, followed by a mv to avoid collisions through concurrent
        # processes or threads (assuming mv is an atomic operation)
        yaml.dump(
            data=dataclasses.asdict(component_descriptor),
            Dumper=cm.EnumValueYamlDumper,
            stream=f.file,
        )
        shutil.move(f.name, descriptor_path)
    except:
        os.unlink(f.name)
        raise


@deprecated.deprecated
def upload_component_descriptor_v2_to_oci_registry(
    component_descriptor_v2: cm.ComponentDescriptor|cm.Component,
    on_exist=UploadMode.SKIP,
):
    if isinstance(component_descriptor_v2, cm.Component):
        component_descriptor_v2 = cm.ComponentDescriptor(
            component=component_descriptor_v2,
            meta=cm.Metadata(),
            signatures=[],
        )

    ensure_is_v2(component_descriptor_v2)
    client = ccc.oci.oci_client()

    target_ref = _target_oci_ref(component_descriptor_v2.component)

    if on_exist in (UploadMode.SKIP, UploadMode.FAIL):
        # check whether manifest exists (head_manifest does not return None)
        if client.head_manifest(image_reference=target_ref, absent_ok=True):
            if on_exist is UploadMode.SKIP:
                return
            if on_exist is UploadMode.FAIL:
                # XXX: we might still ignore it, if the to-be-uploaded CD is equal to the existing
                # one
                raise ValueError(f'{target_ref=} already existed')
    elif on_exist is UploadMode.OVERWRITE:
        pass
    else:
        raise NotImplementedError(on_exist)

    raw_fobj = gci.oci.component_descriptor_to_tarfileobj(component_descriptor_v2)

    cd_digest = hashlib.sha256()
    while (chunk := raw_fobj.read(4096)):
        cd_digest.update(chunk)

    cd_octets = raw_fobj.tell()
    cd_digest = cd_digest.hexdigest()
    cd_digest_with_alg = f'sha256:{cd_digest}'
    raw_fobj.seek(0)

    client.put_blob(
        image_reference=target_ref,
        digest=cd_digest_with_alg,
        octets_count=cd_octets,
        data=raw_fobj,
        # mimetype=gci.oci.component_descriptor_mimetype,
    )

    cfg = gci.oci.ComponentDescriptorOciCfg(
        componentDescriptorLayer=gci.oci.ComponentDescriptorOciBlobRef(
            digest=cd_digest_with_alg,
            size=cd_octets,
        )
    )
    cfg_raw = json.dumps(dataclasses.asdict(cfg)).encode('utf-8')
    cfg_octets = len(cfg_raw)
    cfg_digest = hashlib.sha256(cfg_raw).hexdigest()
    cfg_digest_with_alg = f'sha256:{cfg_digest}'

    client.put_blob(
        image_reference=target_ref,
        digest=cfg_digest_with_alg,
        octets_count=cfg_octets,
        data=cfg_raw,
        mimetype='application/vnd.docker.container.image.v1+json',
    )

    manifest = om.OciImageManifest(
        config=gci.oci.ComponentDescriptorOciCfgBlobRef(
            digest=f'sha256:{cfg_digest}',
            size=cfg_octets,
        ),
        layers=[
            gci.oci.ComponentDescriptorOciBlobRef(
                digest=cd_digest_with_alg,
                size=cd_octets,
            ),
        ],
    )

    manifest_dict = manifest.as_dict()
    manifest_bytes = json.dumps(manifest_dict).encode('utf-8')

    client.put_manifest(
        image_reference=target_ref,
        manifest=manifest_bytes,
    )


def retrieve_component_descriptor_from_oci_ref(
    manifest_oci_image_ref: str,
    absent_ok=False,
    validation_mode: cm.ValidationMode=cm.ValidationMode.WARN,
):
    client = ccc.oci.oci_client()

    manifest = client.manifest(
        image_reference=manifest_oci_image_ref,
        absent_ok=absent_ok,
    )

    if not manifest and absent_ok:
        return None
    elif not manifest and not absent_ok:
        raise ValueError(f'did not find component-descriptor at {manifest_oci_image_ref=}')

    try:
        cfg_dict = json.loads(
            client.blob(
                image_reference=manifest_oci_image_ref,
                digest=manifest.config.digest,
            ).text
        )
        cfg = dacite.from_dict(
            data_class=gci.oci.ComponentDescriptorOciCfg,
            data=cfg_dict,
        )
        layer_digest = cfg.componentDescriptorLayer.digest
        layer_mimetype = cfg.componentDescriptorLayer.mediaType
    except Exception as e:
        logger.warning(
            f'Failed to parse or retrieve component-descriptor-cfg: {e=}. '
            'falling back to single-layer'
        )

        # by contract, there must be exactly one layer (tar w/ component-descriptor)
        if not (layers_count := len(manifest.layers) == 1):
            logger.warning(f'XXX unexpected amount of {layers_count=}')

        layer_digest = manifest.layers[0].digest
        layer_mimetype = manifest.layers[0].mediaType

    if not layer_mimetype in gci.oci.component_descriptor_mimetypes:
        logger.warning(f'{manifest_oci_image_ref=} {layer_mimetype=} was unexpected')
        # XXX: check for non-tar-variant

    blob_res = client.blob(
        image_reference=manifest_oci_image_ref,
        digest=layer_digest,
        stream=False, # manifests are typically small - do not bother w/ streaming
    )
    # wrap in fobj
    blob_fobj = io.BytesIO(blob_res.content)
    component_descriptor = gci.oci.component_descriptor_from_tarfileobj(
        fileobj=blob_fobj,
    )
    return component_descriptor


@deprecated.deprecated
def components(
    component_descriptor_v2: typing.Union[cm.ComponentDescriptor, cm.Component],
    cache_dir: str=None,
):
    if isinstance(component_descriptor_v2, cm.ComponentDescriptor):
        component = component_descriptor_v2.component
    elif isinstance(component_descriptor_v2, cm.Component):
        component = component_descriptor_v2
    else:
        raise TypeError(component_descriptor_v2)

    _visited_component_versions = [
        (component.name, component.version)
    ]

    def resolve_component_dependencies(
        component: cm.Component,
    ):
        nonlocal _visited_component_versions
        nonlocal cache_dir

        yield component

        for component_ref in component.componentReferences:
            cref = (component_ref.componentName, component_ref.version)

            if cref in _visited_component_versions:
                continue
            else:
                _visited_component_versions.append(cref)

            resolved_component_descriptor = download_component_descriptor_v2(
                cache_dir=cache_dir,
                component_name=component_ref.componentName,
                component_version=component_ref.version,
                ctx_repo=component.current_repository_ctx(),
            )

            yield from resolve_component_dependencies(
                component=resolved_component_descriptor.component,
            )

    yield from resolve_component_dependencies(
        component=component,
    )


class ResourceFilter(enum.Enum):
    LOCAL = 'local'
    EXTERNAL = 'external'
    ALL = 'all'


class ResourcePolicy(enum.Enum):
    IGNORE_NONMATCHING_ACCESS_TYPES = 'ignore_nonmatching_access_types'
    WARN_ON_NONMATCHING_ACCESS_TYPES = 'warn_on_nonmatching_access_types'
    FAIL_ON_NONMATCHING_ACCESS_TYPES = 'fail_on_nonmatching_access_types'


def resources(
    component: gci.componentmodel.Component,
    resource_access_types: typing.Iterable[gci.componentmodel.AccessType],
    resource_types: typing.Iterable[gci.componentmodel.ResourceType]=None,
    resource_filter: ResourceFilter=ResourceFilter.ALL,
    resource_policy: ResourcePolicy=ResourcePolicy.FAIL_ON_NONMATCHING_ACCESS_TYPES,
):
    if resource_filter is ResourceFilter.LOCAL:
        resources = [r for r in component.resources if r.relation is cm.ResourceRelation.LOCAL]
    elif resource_filter is ResourceFilter.EXTERNAL:
        resources = [r for r in component.resources if r.relation is cm.ResourceRelation.EXTERNAL]
    elif resource_filter is ResourceFilter.ALL:
        resources = component.resources
    else:
        raise NotImplementedError

    for resource in (r for r in resources if resource_types is None or r.type in resource_types):
        if isinstance(resource.access, dict):
            logger.warning(f'ignoring {resource=}')
            continue
        if resource.access is None and None in resource_access_types:
            yield resource
        elif resource.access and resource.access.type in resource_access_types:
            yield resource
        else:
            if resource_policy is ResourcePolicy.IGNORE_NONMATCHING_ACCESS_TYPES:
                continue
            elif resource_policy is ResourcePolicy.WARN_ON_NONMATCHING_ACCESS_TYPES:
                ci.util.warning(
                    f"Skipping resource with unhandled access type '{resource.access.type}'"
                )
                continue
            elif resource_policy is ResourcePolicy.FAIL_ON_NONMATCHING_ACCESS_TYPES:
                raise ValueError(
                    f"Found resource of matching resource type but with non-matching access type: "
                    f"{resource}. Raising error due to resource policy."
                )
            else:
                raise NotImplementedError


def enumerate_oci_resources(
    component_descriptor,
    cache_dir: str=None,
):
    for component in components(component_descriptor, cache_dir=cache_dir):
        for resource in resources(
            component=component,
            resource_types=[cm.ResourceType.OCI_IMAGE],
            resource_access_types=[cm.AccessType.OCI_REGISTRY],
        ):
            yield (component, resource)


def greatest_component_version(
    component_name: str,
    ctx_repo_base_url: str=None,
    ctx_repo: cm.RepositoryContext=None,
    ignore_prerelease_versions: bool=False,
) -> str:
    if not (bool(ctx_repo_base_url) ^ bool(ctx_repo)):
        raise ValueError('exactly one of ctx_repo_base_url, ctx_repo must be passed')
    if ctx_repo_base_url:
        logger.warning('passing ctx_repo_base_url is deprecated - pass ctx_repo instead!')
        ctx_repo = cm.OciRepositoryContext(baseUrl=ctx_repo_base_url)

    if not isinstance(ctx_repo, cm.OciRepositoryContext):
        raise NotImplementedError(ctx_repo)

    image_tags = component_versions(
        component_name=component_name,
        ctx_repo=ctx_repo,
    )
    return version.find_latest_version(image_tags, ignore_prerelease_versions)


def greatest_version_before(
    component_name: str,
    component_version: str,
    ctx_repo: cm.RepositoryContext,
):
    if not isinstance(ctx_repo, cm.OciRepositoryContext):
        raise NotImplementedError(ctx_repo)

    versions = component_versions(
        component_name=component_name,
        ctx_repo=ctx_repo,
    )
    versions = sorted(versions, key=version.parse_to_semver)
    versions = [
        v for v in versions
        if version.parse_to_semver(v) < version.parse_to_semver(component_version)
    ]
    if len(versions) == 0:
        return None # no release before current was found
    return versions[-1]


# keep for backwards-compatibility for now
latest_component_version = greatest_component_version


def component_versions(
    component_name: str,
    ctx_repo_base_url: str=None,
    ctx_repo: cm.RepositoryContext=None,
) -> typing.Sequence[str]:
    if not (bool(ctx_repo_base_url) ^ bool(ctx_repo)):
        raise ValueError('exactly one of ctx_repo_base_url, ctx_repo must be passed')
    if ctx_repo_base_url:
        logger.warning('passing ctx_repo_base_url is deprecated - pass ctx_repo instead!')
        ctx_repo = cm.OciRepositoryContext(baseUrl=ctx_repo_base_url)

    if not isinstance(ctx_repo, cm.OciRepositoryContext):
        raise NotImplementedError(ctx_repo)

    ctx_repo: cm.OciRepositoryContext

    oci_ref = ctx_repo.component_oci_ref(component_name)
    client = ccc.oci.oci_client()
    return client.tags(image_reference=oci_ref)


def greatest_component_version_with_matching_minor(
    component_name: str,
    reference_version: str,
    ctx_repo_base_url: str=None,
    ctx_repo: cm.RepositoryContext=None,
    ignore_prerelease_versions: bool=False,
) -> str:
    if not (bool(ctx_repo_base_url) ^ bool(ctx_repo)):
        raise ValueError('exactly one of ctx_repo_base_url, ctx_repo must be passed')
    if ctx_repo_base_url:
        logger.warning('passing ctx_repo_base_url is deprecated - pass ctx_repo instead!')
        ctx_repo = cm.OciRepositoryContext(baseUrl=ctx_repo_base_url)

    if not isinstance(ctx_repo, cm.OciRepositoryContext):
        raise NotImplementedError(ctx_repo)

    oci_image_repo = ctx_repo.component_oci_ref(component_name)
    client = ccc.oci.oci_client()
    image_tags = client.tags(image_reference=oci_image_repo)
    return version.find_latest_version_with_matching_minor(
        reference_version=reference_version,
        versions=image_tags,
        ignore_prerelease_versions=ignore_prerelease_versions,
    )


def greatest_component_version_by_name(
    component_name: str,
    ctx_repo_base_url: str,
    ctx_repo: cm.RepositoryContext=None,
    cache_dir: str=None,
):
    if not (bool(ctx_repo_base_url) ^ bool(ctx_repo)):
        raise ValueError('exactly one of ctx_repo_base_url, ctx_repo must be passed')
    if ctx_repo_base_url:
        logger.warning('passing ctx_repo_base_url is deprecated - pass ctx_repo instead!')
        ctx_repo = cm.OciRepositoryContext(baseUrl=ctx_repo_base_url)

    if not isinstance(ctx_repo, cm.OciRepositoryContext):
        raise NotImplementedError(ctx_repo)

    greatest_version = greatest_component_version(
        component_name=component_name,
        ctx_repo=ctx_repo,
    )
    component_descriptor = download_component_descriptor_v2(
        component_name,
        greatest_version,
        ctx_repo=ctx_repo,
        cache_dir=cache_dir,
    )
    return component_descriptor.component
