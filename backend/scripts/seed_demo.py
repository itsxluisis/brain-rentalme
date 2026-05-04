"""Seed script: creates realistic demo data for BrAIn.

Run: python -m scripts.seed_demo (from backend/ directory with DB running)

Creates:
- 1 admin user
- 5 properties across different regions
- 4 systems linked to properties
- 15+ knowledge blocks per entity
- Property-system relations with notes
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.shared.database import async_session
from app.auth.models import User
from app.auth.service import hash_password
from app.properties.models import Property
from app.properties.service import _unique_slug
from app.systems.models import System
from app.systems.service import seed_systems
from app.knowledge.models import KnowledgeBlock
from app.shared.models import PropertySystemRelation

PROPERTIES = [
    {
        "name": "Apartamento Cala Bona 3A",
        "type": "apartment",
        "region": "costa_brava",
        "address": "Carrer de la Mar, 12, 3A, Cala Bona, Girona",
        "capacity": 4,
        "bedrooms": 2,
        "bathrooms": 1,
        "latitude": 41.785,
        "longitude": 3.020,
        "tags": ["piscina", "vistas al mar", "parking"],
        "blocks": [
            {
                "title": "Descripción general",
                "block_type": "description",
                "content": """Apartamento moderno de 2 habitaciones con vistas parciales al mar en la urbanización Cala Bona.

Capacidad: 4 huéspedes
Superficie: 65 m²
Planta: 3ª con ascensor

El apartamento dispone de salón-comedor con sofá cama, cocina americana equipada, 2 habitaciones dobles y baño completo. Terraza de 8 m² con vistas a la piscina comunitaria.""",
            },
            {
                "title": "Normas de la casa",
                "block_type": "rules",
                "content": """- No se permiten mascotas
- No se permiten fiestas ni eventos
- Silencio a partir de las 22:00h
- Máximo 4 huéspedes (no se admiten visitas que pernocten sin declarar)
- Prohibido fumar en el interior
- Los niños menores de 12 años deben estar supervisados en la piscina
- Dejar el apartamento en el mismo estado de limpieza en que se encontró""",
            },
            {
                "title": "Instrucciones de acceso",
                "block_type": "access_instructions",
                "content": """CÓDIGO CAJA DE LLAVES: #4821
La caja de llaves está instalada en el buzón nº 3A (tercera planta izquierda).
Código de apertura: 4821 (pulsar botón derecho + 4821 + confirmar)

Check-in: 15:00 - 22:00h
Check-out: antes de las 11:00h

WIFI: CalaBonaAP3A_5G | Contraseña: rentalme2024
Parking: plaza asignada P-12 en planta -1 (incluida)""",
            },
        ],
    },
    {
        "name": "Estudio Oviedo Centro",
        "type": "apartment",
        "region": "asturias",
        "address": "Calle Uría, 45, 2B, Oviedo, Asturias",
        "capacity": 2,
        "bedrooms": 0,
        "bathrooms": 1,
        "latitude": 43.362,
        "longitude": -5.849,
        "tags": ["centro histórico", "wifi 300mb", "sin ascensor"],
        "blocks": [
            {
                "title": "Descripción general",
                "block_type": "description",
                "content": """Acogedor estudio en el corazón del centro histórico de Oviedo, a 5 minutos caminando de la Catedral.

Ideal para parejas o viajeros de negocios. 35 m² reformados en 2022 con acabados modernos.""",
            },
            {
                "title": "FAQ Huéspedes",
                "block_type": "faq",
                "content": """P: ¿Hay aparcamiento cercano?
R: Sí, parking público a 200m (Parking El Cristo, tarifa 12€/día).

P: ¿Puedo llegar tarde por la noche?
R: Sí, el acceso es por código (self check-in 24h).

P: ¿Está bien comunicado con transporte?
R: A 3 minutos de la estación de autobuses. Bus a aeropuerto cada 30min.""",
            },
        ],
    },
    {
        "name": "Villa Ibiza Sunset Hills",
        "type": "villa",
        "region": "ibiza",
        "address": "Carretera de Santa Eulalia, km 3.5, Ibiza",
        "capacity": 8,
        "bedrooms": 4,
        "bathrooms": 3,
        "latitude": 38.909,
        "longitude": 1.432,
        "tags": ["piscina privada", "vistas al mar", "aire acondicionado", "barbacoa"],
        "blocks": [
            {
                "title": "Descripción general",
                "block_type": "description",
                "content": """Villa de lujo de 4 habitaciones con piscina privada de 10x5m y vistas panorámicas al mar Mediterráneo.

300 m² en una parcela de 1.200 m². Reformada en 2021 con diseño ibicenco auténtico. Domótica completa.""",
            },
            {
                "title": "Procedimiento de apertura piscina",
                "block_type": "sop",
                "content": """1. Abrir llave de paso en cuadro técnico (pared izq. en cuarto de máquinas)
2. Encender bomba filtradora (interruptor verde)
3. Comprobar nivel de cloro con kit (mantener entre 1-3 ppm)
4. Activar iluminación piscina desde panel domótico (app o control físico)

Sistema Vikey: código acceso piscina: el mismo que la villa (auto-rotativo cada reserva)""",
            },
            {
                "title": "Instrucciones de acceso",
                "block_type": "access_instructions",
                "content": """SISTEMA VIKEY instalado en puerta principal.
El código de acceso se genera automáticamente para cada reserva y se envía al huésped por Vikey 24h antes del check-in.

Emergencias: propietario Luis 650-XXX-XXX""",
            },
        ],
    },
    {
        "name": "Hostal La Manga - Habitación Doble 101",
        "type": "hostel_room",
        "region": "la_manga",
        "address": "Avenida del Mar, 89, La Manga del Mar Menor, Murcia",
        "capacity": 2,
        "bedrooms": 1,
        "bathrooms": 1,
        "latitude": 37.638,
        "longitude": -0.724,
        "tags": ["piscina", "desayuno disponible", "vistas piscina"],
        "blocks": [
            {
                "title": "Descripción habitación 101",
                "block_type": "description",
                "content": """Habitación doble superior con vistas a la piscina. Incluye baño privado y terraza de 4m².

Acceso al hostal desde las 14h con servicio de recepción de 8:00 a 22:00h.""",
            },
        ],
    },
    {
        "name": "Apartamento Malagueta Playa",
        "type": "apartment",
        "region": "malaga",
        "address": "Paseo de la Farola, 22, 4A, Málaga",
        "capacity": 4,
        "bedrooms": 2,
        "bathrooms": 1,
        "latitude": 36.719,
        "longitude": -4.404,
        "tags": ["primera línea de playa", "piscina", "gimnasio"],
        "blocks": [
            {
                "title": "Descripción general",
                "block_type": "description",
                "content": """Apartamento en primera línea de la playa de La Malagueta, a 5 min a pie del centro histórico.

Reformado en 2023. Vistas directas al mar desde el salón y ambas habitaciones.""",
            },
            {
                "title": "Notas de pricing temporada",
                "block_type": "pricing_notes",
                "content": """Temporada alta: 15 jun - 15 sep → precio base x1.8
Puentes y festivos nacionales: precio base x1.4
Semana Santa: precio base x1.6
Black Friday / Cyber Monday: -15% sobre precio base

Mínimo 2 noches todo el año. En julio-agosto mínimo 5 noches (sábado-sábado).

Pricelabs activo: ajuste automático diario según demanda y eventos en Málaga.""",
            },
        ],
    },
]

SYSTEM_KNOWLEDGE = [
    {
        "system_name": "Guesty",
        "blocks": [
            {
                "title": "Guía de integración Guesty",
                "block_type": "integration_guide",
                "content": """Guesty es nuestro PMS principal. Gestiona reservas, comunicación con huéspedes y sincronización de calendarios.

API: Guesty Pro Open API (REST)
Autenticación: Bearer token (API Key en Configuración > Integraciones)
Rate limit: 5 req/seg, 1000 req/hora

Endpoints principales utilizados:
- GET /v1/listings → listado de propiedades
- GET /v1/reservations → reservas activas
- GET /v1/guests → datos de huéspedes""",
            },
            {
                "title": "Procedimiento sync Guesty",
                "block_type": "sop",
                "content": """1. Ir a Sincronización en el menú lateral
2. Hacer clic en "Sincronizar ahora"
3. Esperar confirmación (generalmente < 2 minutos)
4. Revisar sección Conflictos si aparecen advertencias
5. Los bloques con edición manual no se sobreescriben automáticamente""",
            },
        ],
    },
    {
        "system_name": "Nuki",
        "blocks": [
            {
                "title": "Guía de acceso con Nuki",
                "block_type": "integration_guide",
                "content": """Nuki Smart Lock se usa en propiedades sin portero.

Tipos de acceso:
- Código temporal: generado por reserva (activo solo durante el periodo de estancia)
- App Nuki: los huéspedes pueden descargar la app y usar Bluetooth (sin código)
- Código maestro del equipo: NO compartir con huéspedes

Para generar código temporal:
1. Abrir app Nuki (cuenta equipo@rentalme.es)
2. Seleccionar cerradura de la propiedad
3. Acceso > Añadir acceso temporal
4. Establecer fechas check-in/check-out + 1h de margen en cada extremo""",
            },
        ],
    },
    {
        "system_name": "Pricelabs",
        "blocks": [
            {
                "title": "Configuración Pricelabs",
                "block_type": "integration_guide",
                "content": """Pricelabs gestiona el pricing dinámico de todas las propiedades.

Cuenta: admin@rentalme.es
Sincronización con Guesty: automática (Pricelabs → Guesty → OTAs)

Estrategia base:
- Base rate mínimo: 60€/noche (apartamentos), 150€ (villas)
- Health score objetivo: >90%
- Ajuste por last-minute (< 7 días): -10%
- Ajuste por eventos locales: automático (Pricelabs Events)

Revisar semanalmente: Customization panel > Minimum Price por propiedad.""",
            },
        ],
    },
]

PROPERTY_SYSTEM_LINKS = [
    {"property_name": "Apartamento Cala Bona 3A", "system_name": "Guesty", "notes": "Listing ID: gst-abc123"},
    {"property_name": "Apartamento Cala Bona 3A", "system_name": "Nuki", "notes": "Lock serial: NK-8821 | Código maestro: 9944"},
    {"property_name": "Apartamento Cala Bona 3A", "system_name": "Pricelabs", "notes": "Base rate: 85€/noche"},
    {"property_name": "Villa Ibiza Sunset Hills", "system_name": "Guesty", "notes": "Listing ID: gst-ibz456"},
    {"property_name": "Villa Ibiza Sunset Hills", "system_name": "Pricelabs", "notes": "Base rate: 350€/noche"},
    {"property_name": "Apartamento Malagueta Playa", "system_name": "Guesty", "notes": "Listing ID: gst-mlg789"},
    {"property_name": "Apartamento Malagueta Playa", "system_name": "Pricelabs", "notes": "Base rate: 120€/noche"},
]


async def run():
    async with async_session() as db:
        # Seed systems
        print("Seeding systems...")
        await seed_systems(db)

        # Create admin user
        from sqlalchemy import select
        existing = await db.execute(select(User).where(User.email == "admin@rentalme.es"))
        if not existing.scalar_one_or_none():
            print("Creating admin user...")
            admin = User(
                email="admin@rentalme.es",
                full_name="Admin RentalMe",
                password_hash=hash_password("admin1234"),
                role="admin",
                is_active=True,
            )
            db.add(admin)
            await db.commit()
        else:
            print("Admin user already exists, skipping.")

        # Create properties with knowledge blocks
        prop_map: dict[str, Property] = {}
        for pdata in PROPERTIES:
            existing_prop = await db.execute(
                select(Property).where(Property.name == pdata["name"])
            )
            prop = existing_prop.scalar_one_or_none()
            if not prop:
                slug = await _unique_slug(db, pdata["name"])
                prop = Property(
                    name=pdata["name"],
                    slug=slug,
                    type=pdata["type"],
                    region=pdata["region"],
                    address=pdata["address"],
                    capacity=pdata["capacity"],
                    bedrooms=pdata["bedrooms"],
                    bathrooms=pdata["bathrooms"],
                    latitude=pdata.get("latitude"),
                    longitude=pdata.get("longitude"),
                    tags=pdata["tags"],
                    status="active",
                )
                db.add(prop)
                await db.flush()
                print(f"  Created property: {prop.name}")

                for bdata in pdata.get("blocks", []):
                    block = KnowledgeBlock(
                        entity_type="property",
                        entity_id=prop.id,
                        block_type=bdata["block_type"],
                        title=bdata["title"],
                        content=bdata["content"],
                        source="manual",
                        language="es",
                        is_active=True,
                    )
                    db.add(block)
            prop_map[prop.name] = prop

        await db.commit()

        # Create system knowledge blocks
        sys_map: dict[str, System] = {}
        for sdata in SYSTEM_KNOWLEDGE:
            result = await db.execute(select(System).where(System.name == sdata["system_name"]))
            system = result.scalar_one_or_none()
            if system:
                sys_map[system.name] = system
                for bdata in sdata["blocks"]:
                    existing_block = await db.execute(
                        select(KnowledgeBlock).where(
                            KnowledgeBlock.entity_id == system.id,
                            KnowledgeBlock.title == bdata["title"],
                        )
                    )
                    if not existing_block.scalar_one_or_none():
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
                        print(f"  Created block for {system.name}: {bdata['title']}")

        await db.commit()

        # Create property-system relations
        for link in PROPERTY_SYSTEM_LINKS:
            prop = prop_map.get(link["property_name"])
            sys = sys_map.get(link["system_name"])
            if prop and sys:
                existing_rel = await db.execute(
                    select(PropertySystemRelation).where(
                        PropertySystemRelation.property_id == prop.id,
                        PropertySystemRelation.system_id == sys.id,
                    )
                )
                if not existing_rel.scalar_one_or_none():
                    rel = PropertySystemRelation(
                        property_id=prop.id,
                        system_id=sys.id,
                        notes=link["notes"],
                    )
                    db.add(rel)
                    print(f"  Linked {prop.name} → {sys.name}")

        await db.commit()
        print("\nSeed complete!")
        print(f"  Admin: admin@rentalme.es / admin1234")
        print(f"  Properties: {len(PROPERTIES)}")
        print(f"  System knowledge blocks: {sum(len(s['blocks']) for s in SYSTEM_KNOWLEDGE)}")
        print(f"  Relations: {len(PROPERTY_SYSTEM_LINKS)}")


if __name__ == "__main__":
    asyncio.run(run())
