# Guía de Despliegue — BrAIn en EasyPanel

Guía completa para desplegar BrAIn (Base de Conocimiento RentalMe) en producción usando EasyPanel.

---

## 1. Prerrequisitos

### Cuentas y acceso
- **EasyPanel**: Cuenta activa en [easypanel.io](https://easypanel.io) con un servidor VPS configurado (mínimo 2 vCPU / 4 GB RAM recomendado).
- **Dominio**: Un dominio apuntando a la IP pública de tu servidor EasyPanel (por ejemplo, `brain.rentalme.es`). EasyPanel gestiona HTTPS automáticamente via Let's Encrypt.
- **Repositorio Git**: El código fuente en GitHub, GitLab o Gitea. EasyPanel construye las imágenes directamente desde el repo. Alternativamente se puede desplegar subiendo el código directamente al servidor.

### Repositorio mínimo
Asegúrate de que el repositorio tenga esta estructura en la raíz:
```
/
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── app/
├── frontend/
│   ├── Dockerfile
│   └── next.config.js       ← debe tener output: "standalone"
└── docker-compose.yml       ← solo para desarrollo local
```

> **Importante**: El `docker-compose.yml` es únicamente para desarrollo local. En EasyPanel cada servicio se configura de forma independiente.

---

## 2. Variables de entorno

### Base de datos — variables requeridas

| Variable | Descripción | Ejemplo / Formato |
|---|---|---|
| `POSTGRES_PASSWORD` | Contraseña de PostgreSQL. **Obligatorio** — no tiene valor por defecto seguro. | `openssl rand -hex 16` |
| `POSTGRES_USER` | Usuario de PostgreSQL (opcional, por defecto: `brain`) | `brain` |
| `POSTGRES_DB` | Nombre de la base de datos (opcional, por defecto: `brain`) | `brain` |

### Backend — variables requeridas

| Variable | Descripción | Ejemplo / Formato |
|---|---|---|
| `DATABASE_URL` | Cadena de conexión a PostgreSQL con asyncpg | `postgresql+asyncpg://brain:TU_PASSWORD@db:5432/brain` |
| `JWT_SECRET` | Secreto para firmar tokens JWT. Debe ser largo y aleatorio. | `s3cr3t_muy_larg0_y_r4nd0m_aqui` |
| `JWT_EXPIRY_HOURS` | Horas de validez del token de sesión | `24` |
| `ENCRYPTION_MASTER_KEY` | Clave maestra para cifrar credenciales de integraciones en la BBDD. **Exactamente 64 caracteres hexadecimales (32 bytes).** | Ver cómo generarla abajo |
| `CORS_ORIGIN` | URL exacta del frontend (sin barra final). El backend la usa para CORS. | `https://brain.rentalme.es` |
| `APP_ENV` | Entorno de ejecución | `production` |

### Frontend — variables requeridas

| Variable | Descripción | Ejemplo / Formato |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | URL pública del backend, accesible desde el navegador del usuario | `https://api.brain.rentalme.es` |

> **Nota sobre NEXT_PUBLIC_**: Las variables con este prefijo se incrustan en el bundle de JavaScript en tiempo de build. Deben estar configuradas ANTES de hacer el build del frontend.

---

### Cómo generar los secretos

**JWT_SECRET** — cualquier cadena larga aleatoria:
```bash
openssl rand -hex 32
# Ejemplo de salida: a1b2c3d4e5f6...
```

**ENCRYPTION_MASTER_KEY** — exactamente 64 caracteres hexadecimales (= 32 bytes):
```bash
openssl rand -hex 32
# La salida tiene exactamente 64 caracteres hex — úsala directamente
# Ejemplo: 0f1e2d3c4b5a69788796a5b4c3d2e1f0a1b2c3d4e5f60718293a4b5c6d7e8f9
```

> **Critico**: Guarda `ENCRYPTION_MASTER_KEY` en un lugar seguro (gestor de contraseñas). Si se pierde, todas las API keys almacenadas en el panel de admin quedarán irrecuperables y habrá que re-introducirlas.

---

## 3. Arquitectura Docker — los 3 servicios

```
┌──────────────┐     HTTP      ┌───────────────┐    asyncpg    ┌──────────────────┐
│   Frontend   │ ──────────▶  │    Backend     │ ──────────▶  │   PostgreSQL DB  │
│  Next.js 14  │              │  FastAPI/Python │              │ pgvector/pg16    │
│  Puerto 3000 │              │   Puerto 8000  │              │   Puerto 5432    │
└──────────────┘              └───────────────┘              └──────────────────┘
```

| Servicio | Imagen/Build | Puerto interno | Descripción |
|---|---|---|---|
| `db` | `pgvector/pgvector:pg16` | 5432 | PostgreSQL 16 con extensión pgvector para embeddings semánticos |
| `backend` | Dockerfile en `./backend` | 8000 | API FastAPI + Alembic migrations + APScheduler |
| `frontend` | Dockerfile en `./frontend` | 3000 | Next.js 14 en modo standalone |

> **Por qué `pgvector/pgvector:pg16` y no la imagen estándar de Postgres**: BrAIn almacena embeddings vectoriales para búsqueda semántica. La extensión `pgvector` NO viene en la imagen oficial `postgres`. Usar la imagen incorrecta produce un error al arrancar las migraciones.

---

## 4. Despliegue en EasyPanel — paso a paso

### 4.1 Crear un nuevo proyecto

1. Accede a tu instancia de EasyPanel.
2. En el panel principal, haz clic en **"Create Project"**.
3. Ponle nombre: `brain` (o `brain-production`).
4. Confirma la creación.

---

### 4.2 Servicio de Base de Datos (PostgreSQL + pgvector)

1. Dentro del proyecto, haz clic en **"Create Service"** → selecciona **"App"** (no el preset de Postgres, porque necesitamos una imagen específica).
2. Configura:
   - **Service name**: `db`
   - **Source**: Docker image
   - **Image**: `pgvector/pgvector:pg16`

3. En la sección **"Environment"**, añade:
   ```
   POSTGRES_USER=brain
   POSTGRES_PASSWORD=TU_PASSWORD_SEGURO_AQUI
   POSTGRES_DB=brain
   ```

4. En la sección **"Volumes"**, añade un volumen para persistencia:
   - Mount path: `/var/lib/postgresql/data`
   - Nombre del volumen: `brain-db-data`

5. En la sección **"Ports"**, el puerto 5432 NO necesita exponerse públicamente. Solo lo usará el backend internamente.

6. En **"Health Check"**, configura:
   - Command: `pg_isready -U brain`
   - Interval: `5s`
   - Timeout: `5s`
   - Retries: `5`

7. Despliega el servicio y espera a que el estado sea **"Running"** y el health check en verde.

---

### 4.3 Servicio Backend (FastAPI)

1. Haz clic en **"Create Service"** → **"App"**.
2. Configura:
   - **Service name**: `backend`
   - **Source**: GitHub / GitLab (conecta tu repo si no lo has hecho)
   - **Repository**: selecciona tu repositorio de BrAIn
   - **Branch**: `main`
   - **Build context**: `./backend` (o la ruta relativa a la carpeta backend dentro del repo)
   - **Dockerfile path**: `backend/Dockerfile`

3. En **"Environment"**, añade todas las variables del backend:
   ```
   DATABASE_URL=postgresql+asyncpg://brain:TU_PASSWORD_SEGURO_AQUI@db:5432/brain
   JWT_SECRET=TU_JWT_SECRET_GENERADO
   JWT_EXPIRY_HOURS=24
   ENCRYPTION_MASTER_KEY=TU_CLAVE_HEX_DE_64_CHARS
   CORS_ORIGIN=https://brain.rentalme.es
   APP_ENV=production
   ```

   > **Nota sobre DATABASE_URL**: El hostname es `db` — el nombre interno del servicio de base de datos dentro del proyecto EasyPanel. EasyPanel resuelve los nombres de servicio automáticamente dentro del mismo proyecto.

4. En **"Ports"**, el puerto 8000 tampoco necesita exponerse directamente si el frontend está en el mismo proyecto. Si necesitas acceso externo a la API (para herramientas, Postman, etc.), expón el puerto y configura un dominio.

5. Configura el dominio de la API si quieres acceso externo:
   - **Domain**: `api.brain.rentalme.es`
   - Puerto: `8000`
   - HTTPS: activar (EasyPanel gestiona el certificado automáticamente)

6. Despliega. El backend arrancará pero las migraciones aún no se han ejecutado — esto se hace en el paso 5.

---

### 4.4 Servicio Frontend (Next.js)

> **Importante**: El frontend usa `output: "standalone"` en `next.config.js`. EasyPanel construirá la imagen correctamente, pero las variables `NEXT_PUBLIC_*` deben estar presentes en tiempo de build, no solo en tiempo de ejecución.

1. Haz clic en **"Create Service"** → **"App"**.
2. Configura:
   - **Service name**: `frontend`
   - **Source**: mismo repositorio
   - **Branch**: `main`
   - **Dockerfile path**: `frontend/Dockerfile`
   - **Build context**: `./frontend`

3. En **"Environment"** (sección Build Args para variables `NEXT_PUBLIC_`):
   ```
   NEXT_PUBLIC_API_URL=https://api.brain.rentalme.es
   ```

   > Si EasyPanel no tiene sección separada de Build Args, añade la variable en el apartado de Environment normal — Next.js la leerá igualmente durante el build si está en el entorno de build.

4. Configura el dominio principal:
   - **Domain**: `brain.rentalme.es`
   - Puerto: `3000`
   - HTTPS: activar

5. Despliega el servicio.

---

### 4.5 Verificar la red interna

EasyPanel conecta automáticamente los servicios del mismo proyecto en una red interna. Para verificar que el backend puede alcanzar la base de datos:

1. Ve al servicio `backend` → **"Console"** (terminal interactiva).
2. Ejecuta:
   ```bash
   python -c "import asyncpg; import asyncio; asyncio.run(asyncpg.connect('postgresql://brain:TU_PASSWORD@db:5432/brain'))"
   ```
   Si no hay errores, la conectividad es correcta.

---

## 5. Primera puesta en marcha

### 5.1 Ejecutar migraciones de base de datos

Las migraciones crean todas las tablas necesarias (incluyendo la extensión `pgvector`).

1. En EasyPanel, ve al servicio `backend`.
2. Abre la **"Console"** (terminal interactiva del contenedor).
3. Ejecuta:
   ```bash
   alembic upgrade head
   ```
4. Deberías ver algo como:
   ```
   INFO  [alembic.runtime.migration] Running upgrade  -> 001abc..., create initial tables
   INFO  [alembic.runtime.migration] Running upgrade  001abc... -> 002def..., add pgvector extension
   ```
5. Si hay un error sobre `pgvector` no encontrado → revisa que el servicio `db` usa la imagen `pgvector/pgvector:pg16` y no `postgres:16`.

---

### 5.2 Cargar datos de demostración (seed)

El script de seed crea:
- 1 usuario administrador
- 5 propiedades de ejemplo
- Bloques de conocimiento asociados
- Sistemas (Guesty, Nuki, Pricelabs) con su documentación

Desde la consola del servicio `backend`:
```bash
python -m scripts.seed_demo
```

Salida esperada:
```
Seeding systems...
Creating admin user...
  Created property: Apartamento Cala Bona 3A
  Created property: Estudio Oviedo Centro
  ...
Seed complete!
  Admin: admin@rentalme.es / admin1234
  Properties: 5
```

> **Credenciales de demo**:
> - Email: `admin@rentalme.es`
> - Contraseña: `admin1234`
>
> **Cambia la contraseña inmediatamente** desde el panel de administración tras el primer acceso.

---

### 5.3 Verificar el acceso inicial

1. Abre `https://brain.rentalme.es` en el navegador.
2. Deberías ver la pantalla de login.
3. Accede con las credenciales de demo.
4. Confirma que aparece el dashboard con las propiedades del seed.

Si el frontend muestra pantalla en blanco o error de red, consulta la sección de Resolución de problemas.

---

## 6. Configuración post-despliegue

### 6.1 Añadir API Keys de integraciones

Las API keys de terceros se gestionan desde el panel de administración y se almacenan cifradas en la base de datos (usando `ENCRYPTION_MASTER_KEY`).

1. Accede como administrador.
2. Ve a **Configuración → Integraciones**.
3. Añade las siguientes claves según corresponda:

| Integración | Dónde obtener la API Key |
|---|---|
| **Guesty** | Guesty Dashboard → Settings → API Keys → Crear nueva key (tipo "Server") |
| **OpenAI** | [platform.openai.com](https://platform.openai.com) → API Keys |
| **Anthropic** | [console.anthropic.com](https://console.anthropic.com) → API Keys |

4. Guarda cada clave. El sistema las cifra automáticamente antes de persistirlas.

---

### 6.2 Sincronización inicial con Guesty

Una vez añadida la API Key de Guesty:

1. Ve a **Sincronización** en el menú lateral.
2. Haz clic en **"Sincronizar ahora"**.
3. Espera hasta 2 minutos. El sistema importará las propiedades y reservas activas desde Guesty.
4. Revisa la sección **"Conflictos"** si aparecen advertencias.

---

### 6.3 Verificar generación de embeddings

Los embeddings vectoriales permiten la búsqueda semántica (IA). Se generan automáticamente cuando se crean o actualizan bloques de conocimiento.

Para verificar que OpenAI está conectado y los embeddings funcionan:

1. Ve a cualquier propiedad → edita un bloque de conocimiento → guarda.
2. En los logs del backend (`EasyPanel → backend → Logs`), deberías ver:
   ```
   INFO: Generated embedding for block_id=xxx (model=text-embedding-3-small)
   ```
3. Si aparece un error de autenticación con OpenAI, revisa la API key en Integraciones.

---

## 7. Resolución de problemas comunes

### Error: `could not open extension control file ... pgvector`

**Causa**: La imagen de base de datos es `postgres:16` en lugar de `pgvector/pgvector:pg16`.

**Solución**:
1. Detén el servicio `db` en EasyPanel.
2. Cambia la imagen a `pgvector/pgvector:pg16`.
3. **Atención**: Si la base de datos ya tenía datos, asegúrate de que el volumen de datos sigue montado. El cambio de imagen no borra los volúmenes.
4. Reinicia el servicio y vuelve a ejecutar `alembic upgrade head`.

---

### Error CORS en el navegador: `Access-Control-Allow-Origin`

**Causa**: La variable `CORS_ORIGIN` en el backend no coincide exactamente con la URL del frontend.

**Diagnóstico**: Abre las herramientas de desarrollador del navegador → pestaña Red → revisa la petición fallida → busca la cabecera `Origin` que envía el navegador.

**Solución**:
- La URL en `CORS_ORIGIN` debe ser idéntica a `Origin`, incluyendo protocolo (`https://`), dominio exacto y sin barra final.
- Correcto: `CORS_ORIGIN=https://brain.rentalme.es`
- Incorrecto: `CORS_ORIGIN=https://brain.rentalme.es/` (barra final)
- Incorrecto: `CORS_ORIGIN=http://brain.rentalme.es` (http en lugar de https)

Tras corregirla, reinicia el servicio backend.

---

### La sesión no se mantiene / cookie no se envía

**Causa**: Los navegadores modernos no envían cookies `SameSite=Lax` en peticiones cross-site sobre HTTP. En producción HTTPS es obligatorio.

**Solución**:
1. Verifica que el dominio del frontend tiene certificado HTTPS activo (en EasyPanel debe aparecer el candado verde junto al dominio).
2. Si el backend y el frontend están en dominios distintos (ej. `brain.rentalme.es` y `api.brain.rentalme.es`), ambos deben ser HTTPS.
3. No uses `http://` en `NEXT_PUBLIC_API_URL` en producción.

---

### WebSocket no conecta

**Causa**: La URL del backend usa `http://` en lugar de `wss://` para conexiones WebSocket.

**Síntoma**: La funcionalidad de chat con IA o notificaciones en tiempo real no funciona. En la consola del navegador aparece `WebSocket connection failed`.

**Solución**: En las variables de entorno del frontend, si hay alguna variable específica para WebSocket, debe usar el protocolo seguro:
```
# Incorrecto
NEXT_PUBLIC_WS_URL=ws://api.brain.rentalme.es

# Correcto
NEXT_PUBLIC_WS_URL=wss://api.brain.rentalme.es
```

Si la URL del WebSocket se construye dinámicamente a partir de `NEXT_PUBLIC_API_URL`, verifica en el código que reemplaza `https://` por `wss://` correctamente.

---

### El frontend muestra pantalla en blanco tras el despliegue

**Causa más frecuente**: `NEXT_PUBLIC_API_URL` no estaba definida en tiempo de build.

**Diagnóstico**:
1. Ve a los logs del servicio `frontend` en EasyPanel.
2. Busca errores durante la fase de build (no de runtime).
3. Abre la consola del navegador — si hay errores de red a `localhost:8000`, significa que la variable `NEXT_PUBLIC_API_URL` no se incluyó en el build.

**Solución**:
1. Asegúrate de que `NEXT_PUBLIC_API_URL` está en las variables de entorno del servicio `frontend` en EasyPanel.
2. Fuerza un rebuild completo del servicio (en EasyPanel: botón "Rebuild" o "Redeploy").

---

### El backend arranca pero las migraciones fallan

**Causa**: El backend intenta conectar antes de que la base de datos esté lista.

**Solución**: Verifica el health check del servicio `db`. En EasyPanel, el servicio `backend` debe depender del `db` estando healthy. Si EasyPanel no soporta `depends_on` directamente, espera a que el servicio `db` esté en verde antes de ejecutar las migraciones manualmente desde la consola.

```bash
# Desde la consola del servicio backend:
# Verificar conectividad primero
python -c "
import asyncio, asyncpg
async def test():
    conn = await asyncpg.connect('postgresql://brain:TU_PASSWORD@db:5432/brain')
    print('Conexión OK')
    await conn.close()
asyncio.run(test())
"

# Si OK, ejecutar migraciones
alembic upgrade head
```

---

## Resumen de URLs en producción

| Servicio | URL |
|---|---|
| Frontend (app principal) | `https://brain.rentalme.es` |
| Backend API | `https://api.brain.rentalme.es` |
| API Docs (Swagger) | `https://api.brain.rentalme.es/docs` |
| Health check backend | `https://api.brain.rentalme.es/health` |

---

*Guía generada para BrAIn v1.0.0 — RentalMe Gestión*
