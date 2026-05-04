"""Initial schema with pgvector extension and all tables

Revision ID: 001
Revises:
Create Date: 2026-05-02
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')

    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("role IN ('admin', 'user')", name="ck_users_role"),
    )

    op.create_table(
        "properties",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(255), unique=True, nullable=False),
        sa.Column("type", sa.String(30), nullable=False),
        sa.Column("region", sa.String(30), nullable=False),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("latitude", sa.Numeric(10, 7), nullable=True),
        sa.Column("longitude", sa.Numeric(10, 7), nullable=True),
        sa.Column("capacity", sa.Integer(), nullable=True),
        sa.Column("bedrooms", sa.Integer(), nullable=True),
        sa.Column("bathrooms", sa.Integer(), nullable=True),
        sa.Column("guesty_listing_id", sa.String(100), unique=True, nullable=True),
        sa.Column("cloudbeds_property_id", sa.String(100), nullable=True),
        sa.Column("status", sa.String(20), server_default="active", nullable=False),
        sa.Column("tags", sa.JSON(), server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column("metadata_", sa.JSON(), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "type IN ('apartment', 'hostel_room', 'hostel_common', 'villa', 'other')",
            name="ck_properties_type",
        ),
        sa.CheckConstraint(
            "region IN ('asturias', 'madrid', 'malaga', 'costa_brava', 'ibiza', 'la_manga', 'other')",
            name="ck_properties_region",
        ),
        sa.CheckConstraint(
            "status IN ('active', 'inactive', 'maintenance')",
            name="ck_properties_status",
        ),
    )
    op.create_index("ix_properties_region", "properties", ["region"])
    op.create_index("ix_properties_status", "properties", ["status"])

    op.create_table(
        "systems",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(255), unique=True, nullable=False),
        sa.Column("category", sa.String(30), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("website_url", sa.String(500), nullable=True),
        sa.Column("has_api", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("api_docs_url", sa.String(500), nullable=True),
        sa.Column("status", sa.String(20), server_default="active", nullable=False),
        sa.Column("tags", sa.JSON(), server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column("metadata_", sa.JSON(), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "category IN ('pms', 'ai_response', 'access', 'checkin', 'pricing', 'other')",
            name="ck_systems_category",
        ),
        sa.CheckConstraint(
            "status IN ('active', 'inactive', 'testing')",
            name="ck_systems_status",
        ),
    )
    op.create_index("ix_systems_category", "systems", ["category"])

    op.create_table(
        "knowledge_blocks",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("entity_type", sa.String(20), nullable=False),
        sa.Column("entity_id", sa.Uuid(), nullable=False),
        sa.Column("block_type", sa.String(30), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("content_vector", Vector(1536), nullable=True),
        sa.Column("source", sa.String(20), server_default="manual", nullable=False),
        sa.Column("language", sa.String(10), server_default="es", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("metadata_", sa.JSON(), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "entity_type IN ('property', 'system')",
            name="ck_kb_entity_type",
        ),
        sa.CheckConstraint(
            "block_type IN ('description', 'rules', 'access_instructions', 'faq', 'sop', 'integration_guide', 'pricing_notes', 'checkin_notes', 'custom')",
            name="ck_kb_block_type",
        ),
        sa.CheckConstraint(
            "source IN ('manual', 'guesty_sync', 'cloudbeds_sync', 'import')",
            name="ck_kb_source",
        ),
        sa.CheckConstraint(
            "language IN ('es', 'en', 'both')",
            name="ck_kb_language",
        ),
    )
    op.create_index("ix_kb_entity", "knowledge_blocks", ["entity_type", "entity_id"])

    op.create_table(
        "property_system_relations",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("property_id", sa.Uuid(), sa.ForeignKey("properties.id", ondelete="CASCADE"), nullable=False),
        sa.Column("system_id", sa.Uuid(), sa.ForeignKey("systems.id", ondelete="CASCADE"), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("config", sa.JSON(), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint("property_id", "system_id", name="uq_property_system"),
    )

    op.create_table(
        "sync_logs",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("provider", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("listings_processed", sa.Integer(), server_default="0", nullable=False),
        sa.Column("blocks_created", sa.Integer(), server_default="0", nullable=False),
        sa.Column("blocks_updated", sa.Integer(), server_default="0", nullable=False),
        sa.Column("blocks_skipped", sa.Integer(), server_default="0", nullable=False),
        sa.Column("errors", sa.JSON(), server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "provider IN ('guesty', 'cloudbeds')",
            name="ck_sync_provider",
        ),
        sa.CheckConstraint(
            "status IN ('running', 'completed', 'failed')",
            name="ck_sync_status",
        ),
    )
    op.create_index("ix_sync_logs_started", "sync_logs", [sa.text("started_at DESC")])

    op.create_table(
        "chat_sessions",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(255), nullable=True),
        sa.Column("scope", sa.String(30), server_default="all", nullable=False),
        sa.Column("scope_entity_id", sa.Uuid(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "scope IN ('all', 'properties', 'systems', 'property_specific')",
            name="ck_chat_scope",
        ),
    )
    op.create_index("ix_chat_sessions_user", "chat_sessions", ["user_id", sa.text("updated_at DESC")])

    op.create_table(
        "chat_messages",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("session_id", sa.Uuid(), sa.ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("sources", sa.JSON(), nullable=True),
        sa.Column("token_count", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "role IN ('user', 'assistant')",
            name="ck_message_role",
        ),
    )
    op.create_index("ix_chat_messages_session", "chat_messages", ["session_id", sa.text("created_at")])

    op.create_table(
        "tool_api_keys",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("key_hash", sa.String(64), unique=True, nullable=False),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_by", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.create_table(
        "tool_api_logs",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("key_id", sa.Uuid(), sa.ForeignKey("tool_api_keys.id"), nullable=False),
        sa.Column("endpoint", sa.String(255), nullable=False),
        sa.Column("query_params", sa.JSON(), nullable=True),
        sa.Column("response_ms", sa.Integer(), nullable=True),
        sa.Column("results_count", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_tool_logs_key", "tool_api_logs", ["key_id", sa.text("created_at DESC")])

    op.create_table(
        "encrypted_credentials",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("service_name", sa.String(100), unique=True, nullable=False),
        sa.Column("encrypted_value", sa.LargeBinary(), nullable=False),
        sa.Column("iv", sa.LargeBinary(), nullable=False),
        sa.Column("tag", sa.LargeBinary(), nullable=False),
        sa.Column("updated_by", sa.Uuid(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.create_table(
        "automation_tasks",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("action_type", sa.String(30), nullable=False),
        sa.Column("schedule_type", sa.String(20), nullable=False),
        sa.Column("schedule_config", sa.JSON(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("last_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_status", sa.String(20), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "action_type IN ('guesty_sync', 'cloudbeds_sync', 'embed_pending')",
            name="ck_auto_action_type",
        ),
        sa.CheckConstraint(
            "schedule_type IN ('interval', 'cron')",
            name="ck_auto_schedule_type",
        ),
    )
    op.create_index("ix_auto_active_next", "automation_tasks", ["is_active", "next_run_at"])


def downgrade() -> None:
    op.drop_table("automation_tasks")
    op.drop_table("encrypted_credentials")
    op.drop_table("tool_api_logs")
    op.drop_table("tool_api_keys")
    op.drop_table("chat_messages")
    op.drop_table("chat_sessions")
    op.drop_table("sync_logs")
    op.drop_table("property_system_relations")
    op.drop_table("knowledge_blocks")
    op.drop_table("systems")
    op.drop_table("properties")
    op.drop_table("users")
    op.execute("DROP EXTENSION IF EXISTS vector;")
