"""
Seed script: Knowledge blocks for all RentalMe systems.

Run: python -m scripts.seed_systems_knowledge (from backend/ directory with DB running)

Carga documentación completa + procesos RentalMe para:
- Guesty (PMS - 10 propiedades)
- Avantio (PMS - 25 unidades, principal)
- Cloudbeds (PMS - Konk Hostel)
- Vikey (Acceso + Check-in - 8 propiedades)
- Nuki (Acceso - 3 propiedades)
- Yacan (Acceso - 2 propiedades)
- UpMarket (Conserje IA - 11 propiedades)
- INTO AI (Conserje IA - 10 propiedades / Guesty)
- Pricelabs (Pricing)
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import select
from app.shared.database import async_session
from app.systems.models import System
from app.knowledge.models import KnowledgeBlock

SYSTEM_BLOCKS = {

    # ─────────────────────────────────────────
    # GUESTY
    # ─────────────────────────────────────────
    "Guesty": [
        {
            "title": "📋 Guesty — Visión general y funcionalidades",
            "block_type": "description",
            "content": """Guesty es el PMS principal para las propiedades RentalMe gestionadas directamente. Centraliza reservas, comunicación con huéspedes, automatizaciones y sincronización con OTAs.

## ¿Qué hace Guesty?
- Gestión central de reservas de 60+ canales (Airbnb, Booking.com, Vrbo, directo...)
- Bandeja de entrada unificada: Airbnb, Booking.com, email, WhatsApp, SMS en un solo lugar
- Automatizaciones por eventos de reserva (confirmación, pre-llegada, estancia, checkout)
- Gestor de cerraduras integrado (Nuki, Vikey)
- Informes de rendimiento, ocupación, ADR, RevPAR
- App móvil para gestión en movilidad

## Propiedades RentalMe en Guesty (10)
- Angelica Leon (León)
- Encarna (Málaga)
- Carmen Cudillero
- Casa Teresa (Ribadesella)
- Colmenar
- Elena Carvajal (Benalmádena)
- Juanjo Nerja
- Martiricos (Málaga)
- Ricardo Soriano (Marbella)
- Paco Sienra
- Konk Hostel La Manga → Cloudbeds (separado)

## Documentación oficial
- Help Center: https://help.guesty.com/hc/en-gb
- Marketplace integraciones: https://app.guesty.com/integrations/marketplace
- API developers: https://api.guesty.com""",
        },
        {
            "title": "🔄 Guesty — Channel Manager y sincronización OTAs",
            "block_type": "integration_guide",
            "content": """## Cómo funciona el Channel Manager de Guesty

Guesty sincroniza en tiempo real disponibilidad, precios y reservas con todos los canales conectados. Previene dobles reservas automáticamente.

## Canales soportados
- Airbnb (partner preferente 2025)
- Booking.com
- Vrbo / HomeAway
- Reservas directas (motor de reservas propio)
- +60 canales adicionales

## Configuración por canal
Cada canal tiene sus propias reglas:
- **Airbnb**: No permite links externos en mensajes. Huéspedes suelen reservar con antelación.
- **Booking.com**: Huéspedes reservan más cerca de llegada, necesitan comunicación rápida.
- Puedes crear versiones de mensajes automatizados por canal.

## Sincronización de precios
Guesty se integra con Pricelabs para pricing dinámico:
1. Pricelabs calcula precio óptimo
2. Lo envía a Guesty
3. Guesty lo distribuye a todos los canales

## Proceso cuando llega una reserva nueva
1. Reserva entra desde el canal (Airbnb, Booking, directo)
2. Guesty bloquea automáticamente fechas en todos los canales
3. Se dispara la automatización de mensaje de bienvenida
4. Si la propiedad tiene Nuki/Vikey → se genera código de acceso automáticamente
5. Notificación al equipo

## Fuentes
- https://www.guesty.com/features/channel-manager/
- https://www.guesty.com/blog/rental-management-software-guide-to-channel-management/""",
        },
        {
            "title": "🤖 Guesty — Automatizaciones y mensajes automáticos",
            "block_type": "sop",
            "content": """## Cómo configurar automatizaciones en Guesty

Las automatizaciones se disparan por eventos de reserva. No responden a mensajes del huésped — se envían en momentos predefinidos.

## Triggers disponibles
- Reserva confirmada
- X horas/días antes del check-in
- En el momento del check-in
- Durante la estancia (X días después del check-in)
- X horas antes del checkout
- Tras el checkout
- Reserva cancelada

## Cómo crear un mensaje automático
1. Ir a **Automations** en el menú lateral
2. Click en **+ New Automation**
3. Seleccionar trigger (ej: "24 hours before check-in")
4. Escribir el mensaje usando variables: {{guest_name}}, {{check_in_date}}, {{access_code}}, {{property_name}}
5. Configurar canales de envío: email, SMS, Airbnb, Booking.com
6. Activar el automático

## Variables más útiles
- `{{guest_name}}` — nombre del huésped
- `{{check_in_date}}` / `{{check_out_date}}` — fechas
- `{{access_code}}` — código de cerradura (Nuki/Vikey)
- `{{property_address}}` — dirección de la propiedad
- `{{reservation_id}}` — ID de la reserva

## Bandeja de entrada unificada
Todos los mensajes de todos los canales llegan a un solo inbox en Guesty. El equipo responde desde ahí sin cambiar de plataforma.

## INTO AI en la bandeja de Guesty
INTO AI se instala como extensión de Chrome y trabaja DENTRO de la bandeja de Guesty:
- Genera respuestas automáticas en segundos
- 4 modos: asistente, copiloto, autopiloto, revenue booster
- No requiere cambiar de herramienta

## Fuentes
- https://www.guesty.com/features/automation-tools/
- https://www.guesty.com/blog/creating-automated-messages-with-guesty/""",
        },
        {
            "title": "🔐 Guesty Locks Manager — Gestión de cerraduras",
            "block_type": "integration_guide",
            "content": """## Guesty Locks Manager

Guesty gestiona los códigos de acceso de Nuki y Vikey directamente desde la plataforma, sin entrar en cada app por separado.

## Cerraduras conectadas en RentalMe (via Guesty)
- **Vikey**: Angelica Leon, Elena Carvajal, Encarna → ver integración específica Vikey
- **Nuki**: Encarna, Fuengirola Beach → ver integración específica Nuki

## Cómo funciona
1. Al confirmar una reserva, Guesty genera automáticamente el código/acceso
2. El código se incluye en el mensaje automático pre-llegada mediante variable `{{access_code}}`
3. El acceso se activa desde la hora de check-in hasta check-out + 1h de margen
4. Al hacer checkout, el código se desactiva automáticamente

## Configurar el código de cerradura en Guesty
1. Ir a la propiedad → **Smart Locks**
2. Conectar la cerradura (Nuki o Vikey via Marketplace)
3. En **Lock Settings**: configurar ventana de tiempo (check-in - checkout + márgenes)
4. Activar **Auto-generate codes** para que salga en los mensajes automáticos

## Problema conocido con Nuki
Los códigos de teclado Nuki NO pueden contener "0" ni empezar por "12".
⚠️ Usar siempre generación aleatoria de Guesty, NUNCA el teléfono del huésped como código.

## Fuentes
- https://help.guesty.com/hc/en-gb/articles/10500555118877-Managing-lock-code-settings-in-Guesty-Locks-Manager
- https://help.guesty.com/hc/en-gb/articles/9372117854237-Vikey
- https://help.guesty.com/hc/en-gb/articles/9372118673949-Nuki""",
        },
    ],

    # ─────────────────────────────────────────
    # AVANTIO
    # ─────────────────────────────────────────
    "Avantio": [
        {
            "title": "📋 Avantio — Visión general y funcionalidades",
            "block_type": "description",
            "content": """Avantio es el PMS principal de RentalMe para la mayoría de propiedades (25 unidades, 11 propiedades). Es un software español de gestión de alquiler vacacional todo en uno.

## ¿Qué hace Avantio?
- PMS: gestión central de reservas, calendarios, propiedades, propietarios
- Channel Manager: sincronización con 50+ portales (Airbnb, Booking, Vrbo, Rentalia...)
- Motor de reservas directo en la web propia
- Gestión de tareas y equipo
- Comunicación unificada con huéspedes y propietarios
- Informes y contabilidad

## Propiedades RentalMe en Avantio (11 propiedades)
- Apartamentos Pedregal (15 unidades) — Asturias
- Casa Sienra — Asturias
- Barqueras Llanes — Asturias
- Primo de Rivera Oviedo — Asturias
- Cudillero St Paul — Asturias
- Manilva
- Fuengirola Los Pacos
- Arcangel (Córdoba)
- Fuengirola Beach
- Nancy (Benalmádena)
- Oliva y Limón (Pedraza)

## Estado migración
La mayoría de propiedades Avantio están en evaluación de migración a Guesty.
- Apartamentos Pedregal → se queda en Avantio (por volumen y contratos)
- Resto → posibilidad de migrar cuando proceda

## Documentación oficial
- Web: https://www.avantio.com
- Channel Manager: https://www.avantio.com/vacation-rental-channel-manager/
- Integraciones API: https://www.avantio.com/api-integrations/
- Soporte: support@avantio.com""",
        },
        {
            "title": "🔄 Avantio — Channel Manager y canales conectados",
            "block_type": "integration_guide",
            "content": """## Channel Manager Avantio

Avantio se conecta con 50+ portales globales, locales y especializados. Con un solo clic, sincroniza disponibilidad, precios, fotos y descripciones desde el PMS a todos los portales.

## Partners principales
- Airbnb (Preferred Software Partner 2025)
- Booking.com (Premier Connectivity Partner 2025)
- Vrbo (Elite Partner 2025)
- Homes & Villas by Marriott Bonvoy (Elite 2025)
- Rentalia, Housetrip, Homelidays, y +45 más

## Cómo sincroniza Avantio
- Actualización de disponibilidad: en tiempo real
- Actualización de precios: en tiempo real
- Fotos y descripciones: sync manual o automático al publicar

## Reglas por canal
Avantio permite configurar reglas específicas por portal y por propiedad:
- Precio base + margen % por canal
- Mínimo de noches diferente por canal
- Políticas de cancelación por canal

## Integración con precios dinámicos
Avantio se integra con herramientas de pricing (Pricelabs, etc.) que ajustan automáticamente las tarifas según demanda y eventos.

## Fuentes
- https://www.avantio.com/vacation-rental-channel-manager/
- https://www.avantio.com/api-integrations/""",
        },
        {
            "title": "📅 Avantio — Gestión de reservas y flujo de trabajo",
            "block_type": "sop",
            "content": """## Ciclo de vida de una reserva en Avantio

### Estados de reserva
1. **Provisional** — solicitud recibida, pendiente de confirmación
2. **Confirmada** — reserva activa
3. **Check-in** — huésped ha llegado
4. **Check-out** — huésped se ha ido
5. **Cancelada** — anulada por cualquier motivo

### Flujo cuando llega una reserva nueva
1. Reserva entra desde canal (Airbnb, Booking, directo)
2. Avantio bloquea el calendario en todos los canales conectados
3. Se envía confirmación automática al huésped (si está configurado)
4. El equipo recibe notificación
5. Si la propiedad tiene UpMarket → UpMarket empieza la comunicación automática
6. Si tiene Vikey → check-in online se activa automáticamente

### Multi-calendario
El multi-calendario de Avantio muestra todas las propiedades y reservas en una vista unificada:
- Arrastrar para modificar fechas
- Ver disponibilidad de toda la cartera de un vistazo
- Bloquear fechas de mantenimiento directamente desde el calendario

### Gestión de tareas
Avantio permite crear y asignar tareas vinculadas a reservas:
- Limpieza (asignar al equipo de limpieza)
- Mantenimiento
- Check-in presencial
Cada tarea tiene fecha, responsable y estado.

### Comunicación con propietarios
Avantio genera informes automáticos para propietarios con liquidaciones, ocupación y ingresos.

## Fuentes
- https://www.avantio.com/property-management-software/
- https://www.avantio.com/operations-management-tool/""",
        },
        {
            "title": "🔗 Avantio — Integraciones con UpMarket y Vikey",
            "block_type": "integration_guide",
            "content": """## Integración Avantio + UpMarket

UpMarket se conecta con Avantio para importar todas las propiedades y reservas automáticamente.

### Cómo funciona la integración
1. Obtener credenciales de integración del equipo de Avantio
2. Introducirlas en la sección de integración de UpMarket
3. UpMarket importa automáticamente todas las propiedades
4. Sincronización continua cada 5 minutos

### Qué sincroniza
- Datos de reservas (fechas, huésped, canal)
- Información de propiedades (descripción, fotos, reglas)
- Cambios y cancelaciones en tiempo real

### Lo que hace UpMarket con los datos de Avantio
- Envía mensajes automáticos (email, SMS, WhatsApp) en momentos clave
- Gestiona el check-in online
- Opera el conserje virtual 24/7
- Genera upsells automáticos

---

## Integración Avantio + Vikey

Vikey gestiona el check-in online y los accesos para las propiedades Avantio.

### Propiedades RentalMe con Vikey (en Avantio)
- Apartamentos Pedregal (15 unidades)
- Barqueras Llanes
- Primo de Rivera Oviedo
- Fuengirola Los Pacos
- Nancy (Benalmádena)

### Cómo funciona
1. Cuando llega una reserva en Avantio, Vikey la recibe automáticamente
2. Vikey envía al huésped el formulario de check-in online
3. El huésped rellena sus datos y firma contratos
4. Vikey genera el acceso temporal (código o app) para el periodo de estancia
5. Al checkout, el acceso se desactiva

### Fuentes
- https://upmarket.cloud/registration-avantio
- https://upmarket.cloud/blog/leveraging-ai-for-superior-vacation-rental-management-the-upmarket-avantio-synergy/""",
        },
    ],

    # ─────────────────────────────────────────
    # VIKEY
    # ─────────────────────────────────────────
    "Vikey": [
        {
            "title": "📋 Vikey — Visión general",
            "block_type": "description",
            "content": """Vikey es la plataforma de check-in online y acceso sin llaves más usada en RentalMe. Combina compliance legal (recogida de DNI/firma) con acceso automático a la propiedad.

## ¿Qué hace Vikey?
- **Check-in online**: recoge datos de huéspedes, firma de contrato y pago de tasas turísticas antes de la llegada
- **Acceso sin llaves**: genera enlaces o códigos temporales para abrir la puerta desde el móvil
- **Compliance legal**: envía datos al registro policial automáticamente (España, Italia, Portugal)
- **Extras y upsells**: vende servicios adicionales durante el check-in online
- **App de gestión**: el host puede abrir puertas remotamente

## Propiedades RentalMe con Vikey (8)
Avantio:
- Apartamentos Pedregal, Barqueras Llanes, Primo de Rivera, Fuengirola Los Pacos, Nancy

Guesty:
- Angelica Leon (solo accesos), Elena Carvajal (plan heredado)

Cloudbeds:
- Konk Hostel La Manga

## Hardware Vikey
- **Vikey4**: dispositivo que se conecta al videoportero del edificio (abre portal)
- **Vikey Lock**: cilindro inteligente para la puerta del apartamento
- **Electrocerrojo**: alternativa al cilindro en puertas especiales
- **Caja de llaves inteligente**: para propiedades sin posibilidad de instalar cerradura

## Lo que NO necesita el huésped
✅ No hace falta descargar ninguna app
✅ El acceso llega por email como enlace web
✅ Funciona desde cualquier móvil

## Documentación oficial
- Web: https://vikey.it
- FAQ: https://vikey.it/en/faq-en/
- Cómo funciona: https://vikey.it/en/how-self-check-in-works/""",
        },
        {
            "title": "🚪 Vikey — Proceso de check-in online paso a paso",
            "block_type": "sop",
            "content": """## Flujo completo de check-in online con Vikey

### 1. Reserva confirmada
- Vikey recibe la reserva desde Avantio, Guesty o Cloudbeds automáticamente
- Se activa el flujo de check-in online para esa reserva

### 2. Email al huésped (normalmente 3-7 días antes)
El huésped recibe un email con enlace al portal de check-in online de Vikey.

### 3. El huésped completa el check-in online
En el portal, el huésped debe:
1. **Rellenar datos personales** (nombre, apellidos, email, teléfono)
2. **Subir foto del DNI/pasaporte** (todos los huéspedes de la reserva)
3. **Firmar el contrato de arrendamiento** digitalmente
4. **Pagar la tasa turística** si aplica (según municipio)
5. **Ver la información de acceso** a la propiedad

### 4. Acceso automático generado
Una vez completado el check-in:
- Vikey genera el acceso temporal (código o enlace de apertura web)
- El acceso solo funciona desde la hora de check-in hasta check-out
- El huésped recibe email/SMS con instrucciones de acceso

### 5. Apertura de puertas
El huésped accede a la propiedad:
- **Portal del edificio**: mediante enlace web que activa el Vikey4
- **Puerta del apartamento**: mediante enlace web (Vikey Lock) o código en teclado

### 6. Durante la estancia
- El host puede ver estado de puertas (abierta/cerrada) desde app
- El host puede abrir remotamente si el huésped tiene problema
- Si no hay internet: el huésped puede llamar al host para apertura remota

### 7. Checkout
- El acceso se desactiva automáticamente a la hora de checkout
- Los datos del huésped quedan registrados para compliance

## Tiempo de instalación hardware
- Inspección gratuita previa (fotos del videoportero y puertas)
- Instalación en menos de 1 semana tras confirmar la instalación
- No requiere obras ni permisos de comunidad (instalación interior)

## Fuentes
- https://vikey.it/en/how-self-check-in-works/online-check-in/
- https://vikey.it/en/faq-en/""",
        },
        {
            "title": "🔗 Vikey — Integración con Guesty",
            "block_type": "integration_guide",
            "content": """## Cómo conectar Vikey con Guesty

### Pasos de conexión
1. Iniciar sesión en Guesty
2. Menú → **Setup Mode** → **Integrations** → **Marketplace**
3. Buscar "Vikey" → click **Connect**
4. Copiar el **API Key** que aparece
5. Iniciar sesión en la cuenta de Vikey
6. Pegar el API Key en el campo correspondiente de la integración

### Qué sincroniza Vikey con Guesty
- Reservas (fechas, datos de huéspedes)
- Estados de reserva (confirmada, cancelada)
- Información de la propiedad

### Modos de uso de Vikey en RentalMe (Guesty)
- **Angelica Leon**: solo accesos (sin check-in online de Vikey — usa check-in de Guesty)
- **Elena Carvajal**: plan heredado de Vikey (revisar contrato)

### Automatizar el envío del acceso
Para que el código/enlace de acceso llegue al huésped automáticamente:
1. En Guesty → **Automations** → crear mensaje automático pre-llegada
2. Incluir la variable `{{access_code}}` en el mensaje
3. Guesty insertará el código Vikey generado para esa reserva

## Fuentes
- https://help.guesty.com/hc/en-gb/articles/9372117854237-Vikey
- https://www.guesty.com/marketplace-items/vikey/
- https://www.guesty.com/blog/guesty-integrates-with-vikey/""",
        },
    ],

    # ─────────────────────────────────────────
    # NUKI
    # ─────────────────────────────────────────
    "Nuki": [
        {
            "title": "📋 Nuki — Visión general y hardware",
            "block_type": "description",
            "content": """Nuki es una cerradura inteligente usada en 3 propiedades RentalMe. Se instala sobre el cilindro existente, sin sustituirlo.

## Propiedades RentalMe con Nuki
- **Encarna** (Málaga) — integración Guesty problemática, actualmente con Zapier
- **Fuengirola Beach** — integración Guesty con problemas reportados
- **Manilva** — (en Avantio)

## Hardware Nuki
- **Nuki Smart Lock**: se instala por dentro de la puerta, sobre el cilindro existente. No requiere obras.
- **Nuki Bridge**: dispositivo que conecta el Smart Lock a internet (necesario para control remoto y integración PMS)
- **Nuki Keypad**: teclado de códigos opcional para acceso sin móvil

## Instalación
1. Instalar la app Nuki
2. Montar el Smart Lock sobre el cilindro (sin herramientas, sistema de sujeción)
3. Instalar el Bridge cerca del Smart Lock (alcance Bluetooth)
4. Crear cuenta Nuki Web
5. Automatizar distribución de accesos

## Precios Smart Hosting
- Plan Smart Hosting: desde **69€/año** por propiedad
- Incluye: integraciones PMS, soporte prioritario (3h), garantía 3 años
- Prueba gratuita 30 días

## Documentación oficial
- Web: https://nuki.io/en-001/discover-nuki/for-your-vacation-rental/overview
- Soporte: https://help.nuki.io/hc/en-001
- API developers: https://developer.nuki.io/""",
        },
        {
            "title": "🔗 Nuki — Integración con Guesty (y problemas conocidos)",
            "block_type": "integration_guide",
            "content": """## Integración Nuki + Guesty

### Cómo conectar (proceso oficial)
1. En Guesty: buscar "Nuki" en el Marketplace → **Connect**
2. Copiar el API token
3. En Nuki Web: ir a **SHORT-TERM RENTAL** → **Link** bajo Guesty
4. Pegar el API token
5. La integración sincroniza reservas automáticamente

### Qué hace la integración (cuando funciona)
- Genera códigos de acceso automáticamente al confirmar reserva
- Activa el acceso desde la hora de check-in
- Desactiva el acceso tras el checkout
- Envía el código al huésped via mensajes automáticos de Guesty (variable `{{access_code}}`)

### ⚠️ PROBLEMA CONOCIDO — Restricción de dígitos
Los códigos de teclado Nuki tienen una restricción crítica:
- **No pueden contener el dígito "0"**
- **No pueden empezar por "12"**

**SOLUCIÓN**: Usar siempre la generación aleatoria de Guesty, NUNCA usar el teléfono del huésped como código.

### ⚠️ PROBLEMA CONOCIDO — Integración inestable (RentalMe)
La integración Nuki-Guesty ha fallado de forma recurrente en propiedades RentalMe:
- **Encarna (Málaga)**: actualmente usando Zapier + generación manual de enlaces como workaround
- **Fuengirola Beach**: integración con problemas reportados

### Workaround actual (mientras dure el problema)
1. Abrir Nuki Web directamente
2. Ir a la propiedad → **Access Manager**
3. Crear acceso temporal manual para las fechas de la reserva
4. Copiar el enlace de acceso
5. Enviar manualmente al huésped (o via Guesty como mensaje manual)

### Opciones de acceso para el huésped
Configurable en Guesty Lock Settings:
- **App Nuki**: el huésped descarga la app y usa Bluetooth
- **Código de teclado**: código numérico en el teclado físico
- **Enlace web**: enlace que abre via Bluetooth desde el navegador (recomendado como backup)
⚠️ Se recomienda dar SIEMPRE acceso a la app Nuki como prevención de bloqueos.

## Fuentes
- https://help.nuki.io/hc/en-us/articles/21284263535761-Connect-Nuki-and-Guesty
- https://help.guesty.com/hc/en-gb/articles/9372118673949-Nuki
- https://help.nuki.io/hc/en-us/articles/21285538639761-How-guests-get-access-to-the-accommodation""",
        },
    ],

    # ─────────────────────────────────────────
    # UPMARKET
    # ─────────────────────────────────────────
    "UpMarket": [
        {
            "title": "📋 UpMarket — Visión general y funcionalidades",
            "block_type": "description",
            "content": """UpMarket es el conserje virtual IA usado en todas las propiedades Avantio de RentalMe (11 propiedades) y Konk Hostel. Automatiza la comunicación con huéspedes via WhatsApp, email y SMS.

## ¿Qué hace UpMarket?
- **Comunicación automática**: mensajes en momentos clave del viaje del huésped
- **Conserje virtual 24/7**: responde preguntas con IA, hace recomendaciones locales
- **Check-in online**: recoge datos, firma de contrato, instrucciones de acceso
- **Upsells automáticos**: early check-in, late checkout, servicios extra
- **Pagos**: gestión de depósitos, extras, tasas turísticas
- **Guest App**: app del huésped con toda la info de la propiedad

## Canales de comunicación
- WhatsApp (principal — más apertura que email)
- Email
- SMS
- In-app notifications

## Propiedades RentalMe con UpMarket (11)
Avantio: Pedregal, Casa Sienra, Barqueras, Primo de Rivera, Cudillero St Paul, Manilva, Fuengirola Los Pacos, Arcangel, Fuengirola Beach, Nancy, Oliva y Limón
Cloudbeds: Konk Hostel (migración pendiente a bot nativo Cloudbeds)

## Integración con Avantio
- Sincronización cada 5 minutos
- Importa automáticamente propiedades y reservas
- Sincroniza información de vuelta a Avantio (datos de huéspedes)

## Documentación oficial
- Web: https://upmarket.cloud
- Integración Avantio: https://upmarket.cloud/registration-avantio
- Blog Avantio-UpMarket: https://upmarket.cloud/blog/leveraging-ai-for-superior-vacation-rental-management-the-upmarket-avantio-synergy/""",
        },
        {
            "title": "⚙️ UpMarket — Configuración y automatizaciones",
            "block_type": "sop",
            "content": """## Cómo funciona UpMarket con Avantio

### Configuración inicial
1. Obtener credenciales de integración del equipo de Avantio
2. Introducirlas en UpMarket → sección Integraciones
3. UpMarket importa todas las propiedades automáticamente
4. Configurar los mensajes automáticos por propiedad
5. Activar el conserje virtual IA

### Flujo automático por reserva
1. **Confirmación**: WhatsApp/email de bienvenida con info básica
2. **Pre-llegada** (3-7 días antes): formulario check-in online, instrucciones de acceso
3. **Día de llegada**: recordatorio con acceso y número de contacto
4. **Durante la estancia**: mensajes de upsell (late checkout, tours...)
5. **Pre-checkout** (día antes): instrucciones de salida
6. **Post-checkout**: solicitud de reseña, encuesta satisfacción

### Compliance España
UpMarket envía automáticamente los datos del huésped a las autoridades españolas (registro de viajeros) al completar el check-in online. Elimina el proceso manual.

### Configurar el conserje virtual
El conserje responde automáticamente preguntas frecuentes sobre:
- Cómo llegar a la propiedad
- Instrucciones de acceso
- Wifi, parking, normas de la casa
- Recomendaciones locales (restaurantes, actividades)
- Hora de check-in/checkout

Para entrenar el IA con información específica de cada propiedad: añadir FAQs y descripción detallada en UpMarket.

### Escalación a humano
Cuando el conserje IA no puede responder → notificación al equipo para respuesta manual.

## Fuentes
- https://upmarket.cloud/vacation-rentals
- https://upmarket.cloud/blog/leveraging-ai-for-superior-vacation-rental-management-the-upmarket-avantio-synergy/""",
        },
    ],

    # ─────────────────────────────────────────
    # INTO AI
    # ─────────────────────────────────────────
    "INTO": [
        {
            "title": "📋 INTO AI — Visión general",
            "block_type": "description",
            "content": """INTO AI es el conserje virtual IA usado en todas las propiedades Guesty de RentalMe (10 propiedades). A diferencia de UpMarket, INTO vive DENTRO de la bandeja de entrada de Guesty como extensión de Chrome.

## ¿Qué hace INTO AI?
- Genera respuestas automáticas a mensajes de huéspedes en segundos
- Trabaja directamente en la bandeja de entrada de Guesty (sin cambiar de herramienta)
- 4 modos de operación según nivel de automatización deseado
- Aprende continuamente de las conversaciones

## 4 modos de operación
1. **Agent Assistance**: INTO sugiere respuestas, el equipo las revisa y envía
2. **Copilot**: INTO proporciona información instantánea para guiar al equipo
3. **Autopilot**: INTO responde automáticamente durante 24 horas sin intervención
4. **Revenue Booster**: sugerencias automáticas de upsell y relleno de huecos de calendario

## Propiedades RentalMe con INTO AI (10 / Guesty)
Angelica Leon, Encarna, Carmen Cudillero, Casa Teresa, Colmenar, Elena Carvajal, Juanjo Nerja, Martiricos, Ricardo Soriano, Paco Sienra

## Ventajas respecto a UpMarket
- Integración nativa en Guesty (sin salir de la plataforma)
- Instalación en minutos (extensión Chrome)
- No requiere configuración de workflows externos

## Web oficial
- https://www.weareinto.ai/es

## Fuentes
- https://www.weareinto.ai/es""",
        },
        {
            "title": "⚙️ INTO AI — Setup y modos de uso",
            "block_type": "sop",
            "content": """## Cómo instalar y usar INTO AI con Guesty

### Instalación (minutos)
1. Registrarse en https://www.weareinto.ai
2. Conectar la cuenta de Guesty
3. Instalar la extensión de Chrome de INTO
4. Invitar al equipo (multi-usuario)
5. INTO está listo para usar

### Uso diario
INTO aparece integrado en la bandeja de entrada de Guesty:
- Cuando llega un mensaje de un huésped, INTO genera una respuesta sugerida
- El equipo puede enviarla directamente, editarla, o ignorarla
- En modo Autopilot, INTO envía la respuesta sin intervención humana

### Configurar el modo según la propiedad
Se recomienda ajustar el modo según el tipo de consulta:
- **Preguntas frecuentes simples** (wifi, check-in, parking) → Autopilot
- **Solicitudes complejas o quejas** → Agent Assistance (siempre con revisión humana)
- **Fuera de horario de oficina** → Autopilot activado

### Revenue Booster
INTO detecta automáticamente:
- Huecos de 1-2 noches en el calendario → propone al huésped extender la estancia
- Oportunidades de upsell según perfil del huésped

### Prueba gratuita
30 días Pro sin tarjeta de crédito.

## Fuentes
- https://www.weareinto.ai/es""",
        },
    ],

    # ─────────────────────────────────────────
    # PRICELABS
    # ─────────────────────────────────────────
    "Pricelabs": [
        {
            "title": "📋 Pricelabs — Visión general y productos",
            "block_type": "description",
            "content": """Pricelabs es la herramienta de pricing dinámico de RentalMe. Ajusta automáticamente los precios de las propiedades según demanda, eventos locales y mercado.

## 4 productos de Pricelabs

### 1. Dynamic Pricing (principal)
Ajusta automáticamente los precios basándose en:
- Demanda del mercado local
- Eventos y festivos
- Ocupación histórica
- Precio de la competencia
- Anticipación de la reserva (last-minute discount, early bird premium)

### 2. Market Dashboards
Inteligencia de mercado automatizada:
- Seguimiento de ocupación, precios y tendencias de reserva
- Comparación con la competencia en cualquier ubicación global

### 3. Portfolio Analytics
Monitorización de rendimiento en tiempo real:
- Ocupación, ADR, RevPAR
- Identifica propiedades con bajo rendimiento

### 4. Revenue Estimator Pro
Predicción de ingresos basada en tendencias históricas.

## Integración con PMS
Pricelabs se conecta directamente con Avantio, Guesty y Cloudbeds:
- Pricelabs calcula el precio óptimo
- Lo envía al PMS
- El PMS lo distribuye a todos los canales

## Precios
- 30 días de prueba gratuita para Dynamic Pricing
- 1 crédito gratuito de Market Dashboard al crear cuenta

## Soporte y formación
- Sesiones de formación en vivo disponibles en español
- Contacto: support@pricelabs.co
- Help Center: https://help.pricelabs.co/portal/en/kb/

## Documentación
- Guía de inicio: https://help.pricelabs.co/portal/en/kb/articles/getting-started-with-pricelabs-a-comprehensive-guide
- PMS integration: https://help.pricelabs.co/portal/en/kb/articles/pms""",
        },
        {
            "title": "⚙️ Pricelabs — Configuración inicial y parámetros clave",
            "block_type": "sop",
            "content": """## Cómo configurar Pricelabs desde cero

### Pasos de configuración inicial
1. Crear cuenta → importar propiedades desde el PMS
2. El import solo trae los datos; los precios NO cambian hasta activar **Sync Prices**
3. Configurar para cada propiedad:

### Parámetros a configurar por propiedad

**Precio base y mínimos**
- Base Price: precio de referencia (punto de partida para los ajustes)
- Minimum Price: precio mínimo absoluto (jamás bajará de aquí)
- Maximum Price: precio máximo (opcional)

**Estancias mínimas dinámicas**
Pricelabs puede ajustar automáticamente el mínimo de noches:
- Alta demanda → aumenta mínimo para evitar huecos
- Baja ocupación → reduce mínimo para aumentar conversión

**Ajustes por anticipación**
- Last-minute (< 7 días): -10% recomendado en RentalMe
- Far out (> 90 días): ajustar según estrategia de la propiedad

### Páginas clave del dashboard
- **Pricing Dashboard**: vista general de todas las propiedades
- **Listing Health Metrics**: métricas de salud de cada listado
- **Pricing Calendar**: ver y editar precios día a día
- **Multi Calendar**: vista de varios listados a la vez

### Activar los precios
Una vez configurado: activar **Sync Prices** en cada propiedad.
⚠️ Hasta activar Sync Prices, Pricelabs no envía ningún precio al PMS.

## Revisión recomendada
- Semanal: revisar el panel de Customization → Minimum Price por propiedad
- Mensual: revisar Market Dashboard para ajustar estrategia

## Fuentes
- https://help.pricelabs.co/portal/en/kb/articles/getting-started-with-pricelabs-a-comprehensive-guide
- https://help.pricelabs.co/portal/en/kb/articles/understanding-min-nights""",
        },
    ],

    # ─────────────────────────────────────────
    # CLOUDBEDS
    # ─────────────────────────────────────────
    "Cloudbeds": [
        {
            "title": "📋 Cloudbeds — Visión general (Konk Hostel)",
            "block_type": "description",
            "content": """Cloudbeds es el PMS usado exclusivamente para Konk Hostel La Manga. Es un PMS especialmente orientado a hostels, hoteles pequeños y alojamientos con múltiples tipos de habitación.

## ¿Por qué Cloudbeds para Konk?
- Gestión de habitaciones múltiples (dobles, literas, individuales) en una sola propiedad
- Ideal para hostels: reservas por cama o por habitación
- Check-in/out por habitación independiente
- Facturación por huésped (no por reserva)

## Stack de Konk Hostel La Manga
| Sistema | Función |
|---------|---------|
| Cloudbeds | PMS principal |
| Vikey | Acceso sin llaves |
| UpMarket | Conserje IA (hasta que Cloudbeds lance bot nativo) |
| Vapi | Bot de llamadas telefónicas |

## Estado UpMarket en Konk
UpMarket se usa como conserje IA temporal. La hoja de ruta prevé reemplazarlo cuando Cloudbeds lance su propio bot nativo de mensajería.

## Documentación oficial
- Help Center: https://myfrontdesk.cloudbeds.com/hc/en-us/
- API developers: https://developers.cloudbeds.com/
- Vikey en Cloudbeds: https://myfrontdesk.cloudbeds.com/hc/en-us/articles/14741564098459-Vikey-Everything-You-Need-to-Know""",
        },
    ],

    # ─────────────────────────────────────────
    # YACAN
    # ─────────────────────────────────────────
    "YACAN": [
        {
            "title": "📋 Yacan — Visión general y limitaciones",
            "block_type": "description",
            "content": """Yacan es una cerradura inteligente española usada en 2 propiedades RentalMe. A diferencia de Nuki y Vikey, Yacan NO tiene integración directa con Guesty ni Avantio.

## Propiedades RentalMe con Yacan (2)
- **Oliva y Limón** (Pedraza) — en Avantio, conserje UpMarket
- **Ricardo Soriano** (Marbella) — en Guesty, conserje INTO AI

## ⚠️ LIMITACIÓN CRÍTICA: Sin integración con PMS
**Yacan no tiene integración directa con Guesty ni Avantio.**

Esto significa que los códigos de acceso deben generarse MANUALMENTE para cada reserva.

### Workaround actual en Ricardo Soriano (Guesty)
1. Al confirmar reserva en Guesty, abrir la app de Yacan manualmente
2. Crear un código temporal para las fechas de la reserva
3. Copiar el enlace/código de acceso
4. Enviarlo manualmente al huésped desde Guesty o via WhatsApp
⚠️ Este proceso es totalmente manual — sin automatización posible actualmente.

### Workaround actual en Oliva y Limón (Avantio/UpMarket)
Proceso similar: generación manual en Yacan → envío via UpMarket o manual.
Nota en la hoja de sistemas: "¿a través de UpMarket?" — pendiente de confirmar si UpMarket puede gestionar el envío.

## Posible solución futura
- Evaluar sustitución de Yacan por Nuki (mejor integración con Guesty, aunque tiene sus propios problemas)
- Evaluar Vikey (integración más estable con ambos PMS)
- Contactar a Yacan para preguntar por integración API con Guesty/Avantio

## Contacto Yacan
Buscar soporte en: yacan.es (pendiente de documentar URL de soporte)""",
        },
    ],
}


async def run():
    async with async_session() as db:
        total_created = 0
        total_skipped = 0

        for system_name, blocks in SYSTEM_BLOCKS.items():
            result = await db.execute(select(System).where(System.name == system_name))
            system = result.scalar_one_or_none()

            if not system:
                print(f"⚠️  Sistema '{system_name}' no encontrado en la BD — saltando")
                continue

            print(f"\n📚 {system_name} ({len(blocks)} bloques)...")

            for bdata in blocks:
                existing = await db.execute(
                    select(KnowledgeBlock).where(
                        KnowledgeBlock.entity_id == system.id,
                        KnowledgeBlock.title == bdata["title"],
                    )
                )
                if existing.scalar_one_or_none():
                    print(f"   ⏭️  Ya existe: {bdata['title']}")
                    total_skipped += 1
                    continue

                block = KnowledgeBlock(
                    entity_type="system",
                    entity_id=system.id,
                    block_type=bdata["block_type"],
                    title=bdata["title"],
                    content=bdata["content"],
                    source="manual",
                    language="es",
                    is_active=True,
                )
                db.add(block)
                print(f"   ✅ Creado: {bdata['title']}")
                total_created += 1

        await db.commit()
        print(f"\n{'='*50}")
        print(f"✅ Completado: {total_created} bloques creados, {total_skipped} ya existían")
        print(f"📊 Sistemas procesados: {len(SYSTEM_BLOCKS)}")


if __name__ == "__main__":
    asyncio.run(run())
