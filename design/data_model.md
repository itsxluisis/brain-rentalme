# Data Model

Read before every user journey that touches data. Keep in sync with actual schema.

## Schema Notes
- Primary key strategy: UUID (`gen_random_uuid()`)
- Soft deletes: No (use `status` enum where applicable)
- Timestamps: `created_at`, `updated_at` TIMESTAMPTZ on all tables
- Migrations: Alembic, `backend/alembic/versions/`
- Enums: VARCHAR + CHECK constraints (NOT native PostgreSQL enums)
- Metadata: JSONB columns named `metadata_` (SQLAlchemy collision avoidance)
- Vector: pgvector extension, `vector(1536)` type, IVFFlat cosine index

## Entities

### users
| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK, default gen_random_uuid() | |
| email | VARCHAR(255) | UNIQUE, NOT NULL | |
| password_hash | VARCHAR(255) | NOT NULL | bcrypt cost 12 |
| full_name | VARCHAR(255) | NOT NULL | |
| role | VARCHAR(20) | CHECK (admin, user), NOT NULL | |
| is_active | BOOLEAN | DEFAULT true | |
| last_login_at | TIMESTAMPTZ | NULL | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |

**Relationships**: 1:N chat_sessions, 1:N tool_api_keys (created_by)
**Indexes**: UNIQUE on email

### properties
| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK | |
| name | VARCHAR(255) | NOT NULL | e.g. "Apartamento Cala Bona 3A" |
| slug | VARCHAR(255) | UNIQUE, NOT NULL | Auto-generated from name |
| type | VARCHAR(30) | CHECK (apartment, hostel_room, hostel_common, villa, other) | |
| region | VARCHAR(30) | CHECK (asturias, madrid, malaga, costa_brava, ibiza, la_manga, other) | |
| address | TEXT | NULL | Full address string |
| latitude | DECIMAL(10,7) | NULL | For map view |
| longitude | DECIMAL(10,7) | NULL | For map view |
| capacity | INTEGER | NULL | Max guests |
| bedrooms | INTEGER | NULL | |
| bathrooms | INTEGER | NULL | |
| guesty_listing_id | VARCHAR(100) | NULL, UNIQUE | FK to Guesty listing |
| cloudbeds_property_id | VARCHAR(100) | NULL | Future use |
| status | VARCHAR(20) | CHECK (active, inactive, maintenance), DEFAULT 'active' | |
| tags | JSONB | DEFAULT '[]' | e.g. ["pool", "pet-friendly"] |
| metadata_ | JSONB | DEFAULT '{}' | Flexible extra fields |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |

**Relationships**: 1:N knowledge_blocks (via entity_type='property'), M:N systems (via property_system_relations)
**Indexes**: UNIQUE on slug, UNIQUE on guesty_listing_id (where not null), INDEX on region, INDEX on status

### systems
| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK | |
| name | VARCHAR(255) | NOT NULL | e.g. "Guesty", "Nuki" |
| slug | VARCHAR(255) | UNIQUE, NOT NULL | |
| category | VARCHAR(30) | CHECK (pms, ai_response, access, checkin, pricing, other) | |
| description | TEXT | NULL | |
| website_url | VARCHAR(500) | NULL | |
| has_api | BOOLEAN | DEFAULT false | |
| api_docs_url | VARCHAR(500) | NULL | |
| status | VARCHAR(20) | CHECK (active, inactive, testing), DEFAULT 'active' | |
| tags | JSONB | DEFAULT '[]' | |
| metadata_ | JSONB | DEFAULT '{}' | |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |

**Relationships**: 1:N knowledge_blocks (via entity_type='system'), M:N properties (via property_system_relations)
**Indexes**: UNIQUE on slug, INDEX on category

### knowledge_blocks
| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK | |
| entity_type | VARCHAR(20) | CHECK (property, system), NOT NULL | Polymorphic discriminator |
| entity_id | UUID | NOT NULL | FK to properties.id or systems.id |
| block_type | VARCHAR(30) | CHECK (description, rules, access_instructions, faq, sop, integration_guide, pricing_notes, checkin_notes, custom) | |
| title | VARCHAR(255) | NOT NULL | |
| content | TEXT | NOT NULL | Plain text / markdown content |
| content_vector | vector(1536) | NULL | Populated async after save |
| source | VARCHAR(20) | CHECK (manual, guesty_sync, cloudbeds_sync, import), DEFAULT 'manual' | |
| language | VARCHAR(10) | CHECK (es, en, both), DEFAULT 'es' | |
| is_active | BOOLEAN | DEFAULT true | |
| metadata_ | JSONB | DEFAULT '{}' | |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |

**Relationships**: Belongs to one property OR one system (polymorphic via entity_type + entity_id)
**Indexes**: INDEX on (entity_type, entity_id), IVFFlat cosine on content_vector (lists=10)

### property_system_relations
| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK | |
| property_id | UUID | FK → properties.id, NOT NULL | CASCADE on delete |
| system_id | UUID | FK → systems.id, NOT NULL | CASCADE on delete |
| notes | TEXT | NULL | e.g. "Nuki lock code: 4821" |
| config | JSONB | DEFAULT '{}' | System-specific config for this property |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |

**Relationships**: Belongs to one property + one system
**Indexes**: UNIQUE on (property_id, system_id)

### sync_logs
| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK | |
| provider | VARCHAR(20) | CHECK (guesty, cloudbeds), NOT NULL | |
| status | VARCHAR(20) | CHECK (running, completed, failed), NOT NULL | |
| listings_processed | INTEGER | DEFAULT 0 | |
| blocks_created | INTEGER | DEFAULT 0 | |
| blocks_updated | INTEGER | DEFAULT 0 | |
| blocks_skipped | INTEGER | DEFAULT 0 | |
| errors | JSONB | DEFAULT '[]' | Array of error objects |
| started_at | TIMESTAMPTZ | NOT NULL | |
| completed_at | TIMESTAMPTZ | NULL | |

**Indexes**: INDEX on started_at DESC

### chat_sessions
| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK | |
| user_id | UUID | FK → users.id, NOT NULL | |
| title | VARCHAR(255) | NULL | Auto-generated from first message |
| scope | VARCHAR(30) | CHECK (all, properties, systems, property_specific), DEFAULT 'all' | |
| scope_entity_id | UUID | NULL | Property ID when scope=property_specific |
| is_active | BOOLEAN | DEFAULT true | |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |

**Relationships**: Belongs to user, 1:N chat_messages
**Indexes**: INDEX on (user_id, updated_at DESC)

### chat_messages
| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK | |
| session_id | UUID | FK → chat_sessions.id, NOT NULL | CASCADE on delete |
| role | VARCHAR(20) | CHECK (user, assistant), NOT NULL | |
| content | TEXT | NOT NULL | |
| sources | JSONB | NULL | Array of {block_id, entity_type, entity_id, title, score} |
| token_count | INTEGER | NULL | Total tokens used for this message |
| created_at | TIMESTAMPTZ | NOT NULL | |

**Indexes**: INDEX on (session_id, created_at)

### tool_api_keys
| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK | |
| name | VARCHAR(255) | NOT NULL | Descriptive name for the key |
| key_hash | VARCHAR(64) | UNIQUE, NOT NULL | SHA-256 hash of the API key |
| last_used_at | TIMESTAMPTZ | NULL | |
| is_active | BOOLEAN | DEFAULT true | |
| created_by | UUID | FK → users.id, NOT NULL | |
| created_at | TIMESTAMPTZ | NOT NULL | |

**Indexes**: UNIQUE on key_hash

### tool_api_logs
| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK | |
| key_id | UUID | FK → tool_api_keys.id, NOT NULL | |
| endpoint | VARCHAR(255) | NOT NULL | |
| query_params | JSONB | NULL | |
| response_ms | INTEGER | NULL | |
| results_count | INTEGER | NULL | |
| created_at | TIMESTAMPTZ | NOT NULL | |

**Indexes**: INDEX on (key_id, created_at DESC)

### encrypted_credentials
| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK | |
| service_name | VARCHAR(100) | UNIQUE, NOT NULL | e.g. "guesty", "openai", "anthropic" |
| encrypted_value | BYTEA | NOT NULL | AES-256-GCM ciphertext |
| iv | BYTEA | NOT NULL | 12-byte initialization vector |
| tag | BYTEA | NOT NULL | 16-byte authentication tag |
| updated_by | UUID | FK → users.id, NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |

**Indexes**: UNIQUE on service_name

### automation_tasks
| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK | |
| name | VARCHAR(255) | NOT NULL | |
| action_type | VARCHAR(30) | CHECK (guesty_sync, cloudbeds_sync, embed_pending), NOT NULL | |
| schedule_type | VARCHAR(20) | CHECK (interval, cron), NOT NULL | |
| schedule_config | JSONB | NOT NULL | e.g. {"hours": 24} or {"cron": "0 6 * * *"} |
| is_active | BOOLEAN | DEFAULT true | |
| last_run_at | TIMESTAMPTZ | NULL | |
| next_run_at | TIMESTAMPTZ | NULL | |
| last_status | VARCHAR(20) | NULL | running/completed/failed |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |

**Indexes**: INDEX on (is_active, next_run_at)
