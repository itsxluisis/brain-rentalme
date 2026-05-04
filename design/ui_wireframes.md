# UI Wireframes

## Navigation Structure

```
/ (redirect → /login or /dashboard)
├── /auth
│   ├── /auth/login
│   └── /auth/setup              (first-run only, disabled after first user)
└── (dashboard)                   (authenticated shell with sidebar)
    ├── /dashboard               (stats, activity, quick actions, map)
    ├── /propiedades             (property list with filters)
    │   └── /propiedades/[slug]  (property detail + knowledge blocks + relations)
    ├── /sistemas                (system list with filters)
    │   └── /sistemas/[slug]    (system detail + knowledge blocks + linked properties)
    ├── /chat                    (RAG chat with session sidebar)
    ├── /sincronizacion          (sync status, trigger, logs, conflicts)
    ├── /reservas                (read-only reservations from Guesty)
    └── /configuracion           (admin panel with tabs)
        ├── tab: API Keys
        ├── tab: Integraciones
        ├── tab: IA Config
        └── tab: Usuarios
```

## Sidebar Navigation (Spanish labels)

| Icon | Label | Route | Badge |
|------|-------|-------|-------|
| LayoutDashboard | Dashboard | /dashboard | — |
| Building2 | Propiedades | /propiedades | count |
| Blocks | Sistemas | /sistemas | count |
| MessageSquare | Chat IA | /chat | — |
| RefreshCw | Sincronización | /sincronizacion | status dot |
| Calendar | Reservas | /reservas | — |
| Settings | Configuración | /configuracion | — |

## Screen Layouts

### Layout: Dashboard (`/dashboard`)
- **Access**: Authenticated
- **Components**: 4x StatCard row (properties, systems, knowledge blocks, last sync), ActivityFeed (recent edits/syncs), QuickActions (4 buttons), PropertyMap (bottom half)
- **Actions**: Click stat → navigate to section. Click quick action → navigate or trigger. Click map pin → property detail.
- **Empty State**: "Comienza sincronizando tus propiedades desde Guesty" with action button

### Layout: Propiedades (`/propiedades`)
- **Access**: Authenticated
- **Components**: PageHeader ("Propiedades" + "Nueva propiedad" button), FilterBar (region, type, status dropdowns), PropertyGrid (cards with name, region badge, status, KB count, capacity)
- **Actions**: Filter, search, click card → detail, create new
- **Empty State**: "No hay propiedades aún. Sincroniza desde Guesty o crea una manualmente."

### Layout: Propiedad Detalle (`/propiedades/[slug]`)
- **Access**: Authenticated
- **Components**: PropertyInfoCard (editable inline fields), LinkedSystemsSection (list with config/notes, "Vincular sistema" button), KnowledgeBlocksSection (list by type, add/edit buttons), SyncHistoryTab (if guesty_listing_id exists)
- **Actions**: Edit property fields inline, link/unlink systems, add/edit/delete knowledge blocks
- **Empty State per section**: "No hay sistemas vinculados" / "No hay bloques de conocimiento"

### Layout: Sistemas (`/sistemas`)
- **Access**: Authenticated
- **Components**: PageHeader + FilterBar (category, status), SystemGrid (cards with name, category badge, has_api indicator, property count)
- **Actions**: Filter, search, click → detail, create new
- **Empty State**: "No hay sistemas registrados."

### Layout: Sistema Detalle (`/sistemas/[slug]`)
- **Access**: Authenticated
- **Components**: SystemInfoCard (editable), LinkedPropertiesSection, KnowledgeBlocksSection
- **Actions**: Edit system, view linked properties, manage knowledge blocks

### Layout: Chat IA (`/chat`)
- **Access**: Authenticated
- **Components**: SessionSidebar (left, list of sessions with preview), ChatWindow (center, messages + input), ScopeSelector (top: all/properties/systems/specific property), SourceCards (below each assistant message)
- **Actions**: New session, switch session, rename/delete session, send message, change scope
- **Empty State**: "Pregunta lo que necesites sobre tus propiedades y sistemas."

### Layout: Sincronización (`/sincronizacion`)
- **Access**: Authenticated (trigger: Admin only)
- **Components**: SyncStatusCard (last run, next run, listings count), "Sincronizar ahora" button with progress bar, SyncLogTable (date, provider, status, stats), ConflictList (blocks with local/remote diff)
- **Actions**: Trigger sync, view logs, resolve conflicts
- **Empty State**: "Configura tu integración con Guesty para empezar a sincronizar."

### Layout: Reservas (`/reservas`)
- **Access**: Authenticated
- **Components**: FilterBar (property, date range, status), ReservationTable (guest, property, check-in, check-out, status, channel)
- **Actions**: Filter, expand row for details
- **Empty State**: "Configura Guesty para ver reservas."

### Layout: Configuración (`/configuracion`)
- **Access**: Admin only
- **Components**: TabNavigation (API Keys, Integraciones, IA Config, Usuarios), content per tab
- **Tab: API Keys**: Key list (masked, with last_used, revoke button), "Crear clave" button + dialog (shows key once)
- **Tab: Integraciones**: Guesty card (connection status, credential form, test button), Cloudbeds card (coming soon)
- **Tab: IA Config**: Embedding model selector, chat model selector, RAG top-K slider, temperature slider, embedding coverage stats
- **Tab: Usuarios**: User list (email, role, status, last login), invite button, role selector, deactivate toggle

## UI Conventions
- Design system: Glassmorphism dark mode default (see style_guide.md)
- All forms: React Hook Form + Zod validation
- All tables: TanStack Table (sortable, paginated)
- All lists: Framer Motion stagger animation
- Cards: hover scale 1.01 + shadow glow
- Page transitions: fade + slide-up 0.3s
- Toasts: bottom-right, auto-dismiss 5s
- Modals: centered, backdrop blur
- Responsive: sidebar collapses to hamburger on mobile
