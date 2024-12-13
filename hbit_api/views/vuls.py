from sqlalchemy.orm import Session
from sqlmodel import func, select

from hbit_api.domain import models
from hbit_api.domain.dto import vuls as dto


def read_cwes(session: Session, skip: int = 0, limit: int = 100) -> dto.CWEsDto:
    count_statement = select(func.count()).select_from(models.CWE)
    # count statement always return 0 even if there are no users
    count = session.scalar(count_statement)

    statement = select(models.CWE).offset(skip).limit(limit)
    cwes = session.scalars(statement).all()

    cwes_dtos = [dto.CWEDto.from_cwe(cwe) for cwe in cwes]
    return dto.CWEsDto(data=cwes_dtos, count=count)  # type: ignore
