"use client";

import { useEffect } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import { Icon } from "leaflet";
import "leaflet/dist/leaflet.css";
import type { PropertySummary } from "@/types/property";
import Link from "next/link";

// Fix default marker icons for webpack
const markerIcon = new Icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
});

interface Props {
  properties: PropertySummary[];
}

export function PropertiesMap({ properties }: { properties: PropertySummary[] }) {
  const withCoords = properties.filter((p) => p.latitude != null && p.longitude != null);
  const center: [number, number] = withCoords.length > 0
    ? [withCoords[0].latitude!, withCoords[0].longitude!]
    : [40.416775, -3.703790]; // Madrid default

  if (withCoords.length === 0) {
    return (
      <div className="flex h-full items-center justify-center">
        <p className="text-sm text-white/30">
          Ninguna propiedad tiene coordenadas. Edita las propiedades para añadir latitud/longitud.
        </p>
      </div>
    );
  }

  return (
    <MapContainer
      center={center}
      zoom={7}
      style={{ height: "100%", width: "100%", borderRadius: "16px" }}
      className="z-0"
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {withCoords.map((p) => (
        <Marker
          key={p.id}
          position={[p.latitude!, p.longitude!]}
          icon={markerIcon}
        >
          <Popup>
            <div className="text-sm">
              <p className="font-semibold">{p.name}</p>
              <Link href={`/propiedades/${p.slug}`} className="text-xs text-blue-600 hover:underline">
                Ver detalle →
              </Link>
            </div>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}
