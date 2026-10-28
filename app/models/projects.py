from typing import TYPE_CHECKING

from sqlalchemy import Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config import Base
from app.models import employee_project

if TYPE_CHECKING:
    from app.models.employee import Employee


class Projects(Base):
    __tablename__ = "Projects"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    title: Mapped[str] = mapped_column(
        String(100),
        nullable=True,
    )

    description: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    employees: Mapped[list["Employee"]] = relationship(
        "Employee",
        secondary=employee_project,
        back_populates="projects",
    )
