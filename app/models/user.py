import enum
from sqlalchemy import String, Boolean, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin

class UserRole(str, enum.Enum):
    # String enum so the role value is human-readable in both the DB and the JWT.
    # This also means comparisons like user.role == "admin" work as expected.
    viewer  = "viewer"   # read-only access to their own data and dashboard
    analyst = "analyst"  # read access to all data + dashboard insights
    admin   = "admin"    # full CRUD on records + user management

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id:              Mapped[int]      = mapped_column(primary_key=True)
    email:           Mapped[str]      = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str]      = mapped_column(String(255))
    role:            Mapped[UserRole] = mapped_column(SAEnum(UserRole), default=UserRole.viewer)
    is_active:       Mapped[bool]     = mapped_column(Boolean, default=True)
    # is_active lets an admin deactivate a user without deleting them.
    # We check this on every login  inactive users get 401.
