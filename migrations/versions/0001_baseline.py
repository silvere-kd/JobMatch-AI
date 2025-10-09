# migrations/versions/0001_baseline.py
"""baseline schema

Revision ID: 0001_baseline
Revises:
Create Date: 2025-10-06 00:00:00
"""
import sqlalchemy as sa
from alembic import op

revision = "0001_baseline"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "runs",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("payload_hash", sa.String(), index=True),
        sa.Column(
            "status",
            sa.Enum("queued", "running", "succeeded", "failed", name="runstatus"),
            index=True,
        ),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("resume_text", sa.Text()),
        sa.Column("jd_text", sa.Text()),
        sa.Column("params", sa.JSON()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_runs_payload_hash_status", "runs", ["payload_hash", "status"])

    op.create_table(
        "artifacts",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("run_id", sa.String(), index=True),
        sa.Column("name", sa.String()),
        sa.Column("kind", sa.String()),
        sa.Column("mime", sa.String()),
        sa.Column("path", sa.String()),
        sa.Column("size_bytes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("sha256", sa.String(), index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_artifacts_run_name", "artifacts", ["run_id", "name"])


def downgrade() -> None:
    op.drop_index("ix_artifacts_run_name", table_name="artifacts")
    op.drop_table("artifacts")
    op.drop_index("ix_runs_payload_hash_status", table_name="runs")
    op.drop_table("runs")
    op.execute("DROP TYPE IF EXISTS runstatus")
