import svcs
from fastapi import APIRouter
from sqlalchemy.orm import Session
from starlette import status

from hbit_api.api import deps
from hbit_api.domain import commands
from hbit_api.domain.dto import vuls as dto
from hbit_api.service_layer import messagebus
from hbit_api.views import vuls as views

router = APIRouter()


@router.post(
    "/cwes/batch",
)
def create_cwe_batch(
    services: svcs.fastapi.DepContainer,
    super_user: deps.CurrentSuperUser,
    cwe_batch: list[dto.CWEDto],
) -> int:
    """
    Create batch of CWEs.
    """
    bus = services.get(messagebus.MessageBus)

    create_cwes = commands.CreateCWEs(cwe_batch=cwe_batch)
    bus.handle(message=create_cwes)
    return status.HTTP_201_CREATED


@router.post(
    "/capecs/batch",
)
def create_capec_batch(
    services: svcs.fastapi.DepContainer,
    super_user: deps.CurrentSuperUser,
    capec_batch: list[dto.CAPECInDto],
) -> int:
    """
    Create batch of CAPECs.
    """
    bus = services.get(messagebus.MessageBus)

    create_capecs = commands.CreateCAPECs(capec_batch=capec_batch)
    bus.handle(message=create_capecs)
    return status.HTTP_201_CREATED


@router.post(
    "/patches/{patch_build}/cves/batch",
)
def create_cve_batch(
    services: svcs.fastapi.DepContainer,
    super_user: deps.CurrentSuperUser,
    patch_build: str,
    cve_batch: list[dto.CVEDto],
) -> int:
    """
    Create batch of CVE.
    """
    bus = services.get(messagebus.MessageBus)

    create_cves = commands.CreateCVEs(patch_build=patch_build, cve_batch=cve_batch)
    bus.handle(message=create_cves)
    return status.HTTP_201_CREATED


@router.post(
    "/patches/batch",
)
def create_patch_batch(
    services: svcs.fastapi.DepContainer,
    super_user: deps.CurrentSuperUser,
    patches_batch: list[dto.PatchDto],
) -> int:
    """
    Create batch of patches.
    """
    bus = services.get(messagebus.MessageBus)

    create_patches = commands.CreatePatches(patches_batch=patches_batch)
    bus.handle(message=create_patches)
    return status.HTTP_201_CREATED


@router.get(
    "/cwes",
    response_model=dto.CWEsDto,
)
def read_cwes(
    services: svcs.fastapi.DepContainer,
    super_user: deps.CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> dto.CWEsDto:
    """
    Retrieve CWEs.
    """
    session = services.get(Session)

    return views.read_cwes(session, skip, limit)


@router.get(
    "/cves",
    response_model=dto.CVEsDto,
)
def read_cves(
    services: svcs.fastapi.DepContainer,
    super_user: deps.CurrentUser,
    skip: int = 0,
    limit: int = 100,
    patch_build: str | None = None,
) -> dto.CVEsDto:
    """
    Retrieve CVEs.
    """
    session = services.get(Session)

    return views.read_cves(session, patch_build, skip, limit)
