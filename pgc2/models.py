from typing import Any, Dict
import uuid

import datetime

import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy_utils import UUIDType, JSONType


class Base(DeclarativeBase):
    pass


class Job(Base):
    __tablename__ = "job"
    id: Mapped[uuid.UUID] = mapped_column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    created_at = mapped_column(sa.DateTime, default=datetime.datetime.utcnow)
    worker_id: Mapped[str] = mapped_column(sa.String(20), nullable=False)
    payload: Mapped[Dict[str, Any]] = mapped_column(JSONType, nullable=False)

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(id={self.id!r}, payload={self.payload!r})"


class JobResult(Base):
    __tablename__ = "job_result"
    id: Mapped[uuid.UUID] = mapped_column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(UUIDType(binary=False), nullable=False, index=True)
    created_at = mapped_column(sa.DateTime, default=datetime.datetime.utcnow)
    result: Mapped[Dict[str, Any]] = mapped_column(JSONType, nullable=False)

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(id={self.id!r}, job_id={self.job_id!r}, result={self.result!r})"
