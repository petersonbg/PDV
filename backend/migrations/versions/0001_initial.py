"""initial schema

Revision ID: 0001
Revises: 
Create Date: 2024-01-01
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("full_name", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("is_superuser", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "permissions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sku", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("cost", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "customers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("document", sa.String(), nullable=True),
        sa.Column("phone", sa.String(), nullable=True),
        sa.Column("email", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("entity", sa.String(), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "stock_locations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("is_default", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "user_roles",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("user_id", "role_id"),
    )
    op.create_table(
        "role_permissions",
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column("permission_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["permission_id"], ["permissions.id"]),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"]),
        sa.PrimaryKeyConstraint("role_id", "permission_id"),
    )
    op.create_table(
        "stock_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("location_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Numeric(precision=12, scale=3), nullable=True),
        sa.ForeignKeyConstraint(["location_id"], ["stock_locations.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "sales",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=True),
        sa.Column("total", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("discount", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("customer_id", sa.Integer(), nullable=True),
        sa.Column("cashier_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["cashier_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_table(
        "stock_movements",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("stock_item_id", sa.Integer(), nullable=False),
        sa.Column("change", sa.Numeric(precision=12, scale=3), nullable=False),
        sa.Column("reason", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["stock_item_id"], ["stock_items.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "sale_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sale_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Numeric(precision=12, scale=3), nullable=False),
        sa.Column("unit_price", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("total_price", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(["sale_id"], ["sales.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sale_id", sa.Integer(), nullable=False),
        sa.Column("method", sa.String(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("transaction_code", sa.String(), nullable=True),
        sa.Column("paid", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["sale_id"], ["sales.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "fiscal_documents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sale_id", sa.Integer(), nullable=False),
        sa.Column("model", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=True),
        sa.Column("protocol", sa.String(), nullable=True),
        sa.Column("access_key", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["sale_id"], ["sales.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "fiscal_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("document_id", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("message", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["document_id"], ["fiscal_documents.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("fiscal_events")
    op.drop_table("fiscal_documents")
    op.drop_table("payments")
    op.drop_table("sale_items")
    op.drop_table("stock_movements")
    op.drop_table("sales")
    op.drop_table("stock_items")
    op.drop_table("role_permissions")
    op.drop_table("user_roles")
    op.drop_table("stock_locations")
    op.drop_table("audit_logs")
    op.drop_table("customers")
    op.drop_table("products")
    op.drop_table("roles")
    op.drop_table("permissions")
    op.drop_table("users")
