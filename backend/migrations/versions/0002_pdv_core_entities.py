"""Expand PDV domain with suppliers and cash registers

Revision ID: 0002
Revises: 0001
Create Date: 2024-01-02
"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "suppliers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("document", sa.String(), nullable=True),
        sa.Column("phone", sa.String(), nullable=True),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("contact_name", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "cash_registers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=True),
        sa.Column("opening_amount", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("closing_amount", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("opened_at", sa.DateTime(), nullable=True),
        sa.Column("closed_at", sa.DateTime(), nullable=True),
        sa.Column("opened_by_id", sa.Integer(), nullable=True),
        sa.Column("closed_by_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["opened_by_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["closed_by_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )

    op.add_column(
        "stock_movements",
        sa.Column("movement_type", sa.String(), nullable=False, server_default="adjustment"),
    )
    op.add_column("stock_movements", sa.Column("supplier_id", sa.Integer(), nullable=True))
    op.add_column("stock_movements", sa.Column("sale_item_id", sa.Integer(), nullable=True))
    op.add_column("stock_movements", sa.Column("created_by_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "stock_movements_supplier_id_fkey",
        "stock_movements",
        "suppliers",
        ["supplier_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "stock_movements_sale_item_id_fkey", "stock_movements", "sale_items", ["sale_item_id"], ["id"]
    )
    op.create_foreign_key(
        "stock_movements_created_by_id_fkey", "stock_movements", "users", ["created_by_id"], ["id"]
    )

    op.add_column("sales", sa.Column("cash_register_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "sales_cash_register_id_fkey", "sales", "cash_registers", ["cash_register_id"], ["id"]
    )

    op.add_column("payments", sa.Column("cash_register_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "payments_cash_register_id_fkey", "payments", "cash_registers", ["cash_register_id"], ["id"]
    )

    op.alter_column("stock_movements", "movement_type", server_default=None)


def downgrade() -> None:
    op.drop_constraint("payments_cash_register_id_fkey", "payments", type_="foreignkey")
    op.drop_column("payments", "cash_register_id")

    op.drop_constraint("sales_cash_register_id_fkey", "sales", type_="foreignkey")
    op.drop_column("sales", "cash_register_id")

    op.drop_constraint("stock_movements_created_by_id_fkey", "stock_movements", type_="foreignkey")
    op.drop_constraint("stock_movements_sale_item_id_fkey", "stock_movements", type_="foreignkey")
    op.drop_constraint("stock_movements_supplier_id_fkey", "stock_movements", type_="foreignkey")
    op.drop_column("stock_movements", "created_by_id")
    op.drop_column("stock_movements", "sale_item_id")
    op.drop_column("stock_movements", "supplier_id")
    op.drop_column("stock_movements", "movement_type")

    op.drop_table("cash_registers")
    op.drop_table("suppliers")
