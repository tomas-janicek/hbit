from sqlalchemy.orm import Session, selectinload
from sqlmodel import func, select

from hbit_api.domain import models
from hbit_api.domain.dto import vuls as dto


def read_cwes(session: Session, skip: int = 0, limit: int = 100) -> dto.CWEsDto:
    count_statement = select(func.count()).select_from(models.CWE)
    # count statement always return 0 even if there are no cwes
    count = session.scalar(count_statement)

    statement = select(models.CWE).offset(skip).limit(limit)
    cwes = session.scalars(statement).all()

    cwes_dtos = [dto.CWEDto.from_cwe(cwe) for cwe in cwes]
    return dto.CWEsDto(data=cwes_dtos, count=count)  # type: ignore


def read_cves(
    session: Session,
    patch_build: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> dto.CVEsDto:
    statement = select(models.CVE).options(selectinload(models.CVE.cwes))
    if patch_build is not None:
        statement = statement.join(models.CVE.patches).filter(
            models.Patch.build == patch_build
        )

    count_statement = select(func.count()).select_from(statement.subquery())
    count = session.scalar(count_statement)

    statement = statement.offset(skip).limit(limit)
    cves = session.scalars(statement).all()

    cves_dtos = [dto.CVEDto.from_cve(cve) for cve in cves]
    return dto.CVEsDto(data=cves_dtos, count=count)  # type: ignore
