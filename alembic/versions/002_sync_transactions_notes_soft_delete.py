"""Sync transactions schema with ORM (notes + soft delete)."""

from alembic import op
import sqlalchemy as sa


revision = "002_sync_transactions_notes_soft_delete"
down_revision = "001_initial_schema"
branch_labels = None
depends_on = None


def _column_names(bind, table_name: str) -> set[str]:
    inspector = sa.inspect(bind)
    return {col["name"] for col in inspector.get_columns(table_name)}


def upgrade() -> None:
    bind = op.get_bind()
    cols = _column_names(bind, "transactions")

    # Legacy schema used `description`; current ORM uses `notes`.
    if "notes" not in cols and "description" in cols:
        with op.batch_alter_table("transactions") as batch_op:
            batch_op.alter_column("description", new_column_name="notes")

    # If neither column exists, create `notes` as nullable text.
    cols = _column_names(bind, "transactions")
    if "notes" not in cols:
        with op.batch_alter_table("transactions") as batch_op:
            batch_op.add_column(sa.Column("notes", sa.Text(), nullable=True))

    # Introduce soft-delete flag expected by services.
    cols = _column_names(bind, "transactions")
    if "is_deleted" not in cols:
        with op.batch_alter_table("transactions") as batch_op:
            batch_op.add_column(
                sa.Column(
                    "is_deleted",
                    sa.Boolean(),
                    nullable=False,
                    server_default=sa.text("false"),
                )
            )


def downgrade() -> None:
    bind = op.get_bind()
    cols = _column_names(bind, "transactions")

    if "is_deleted" in cols:
        with op.batch_alter_table("transactions") as batch_op:
            batch_op.drop_column("is_deleted")

    cols = _column_names(bind, "transactions")
    if "notes" in cols and "description" not in cols:
        with op.batch_alter_table("transactions") as batch_op:
            batch_op.alter_column("notes", new_column_name="description")
