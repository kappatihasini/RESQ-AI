import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import { CriticalZone, EmergencyResource, ResourcePlan, Incident } from '../types';

interface TacticalMapProps {
  zones: CriticalZone[];
  resources: EmergencyResource[];
  currentPlan: ResourcePlan | null;
  incidents: Incident[];
  currentAct: number;
  onSelectZone: (zone: CriticalZone) => void;
}

export const TacticalMap: React.FC<TacticalMapProps> = ({
  zones,
  resources,
  currentPlan,
  incidents,
  currentAct,
  onSelectZone,
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const layerGroupRef = useRef<L.LayerGroup | null>(null);

  // Initialize Map Once
  useEffect(() => {
    if (!mapContainerRef.current || mapInstanceRef.current) return;

    const map = L.map(mapContainerRef.current, {
      center: [13.0827, 80.2707],
      zoom: 14,
      zoomControl: false,
    });

    L.control.zoom({ position: 'bottomright' }).addTo(map);

    // Standard OpenStreetMap tiles (styled by dark filter in index.css)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 18,
      attribution: '&copy; OpenStreetMap contributors | RESQ-AI Tactical GIS',
    }).addTo(map);

    layerGroupRef.current = L.layerGroup().addTo(map);
    mapInstanceRef.current = map;

    return () => {
      map.remove();
      mapInstanceRef.current = null;
    };
  }, []);

  // Update Layers when data changes
  useEffect(() => {
    if (!mapInstanceRef.current || !layerGroupRef.current) return;

    const layerGroup = layerGroupRef.current;
    layerGroup.clearLayers();

    // 1. Render Critical Zones (Rings & Circles)
    zones.forEach((zone) => {
      const colorMap: Record<string, string> = {
        CRITICAL_P1: '#ef4444',
        HIGH_P2: '#f59e0b',
        MEDIUM_P3: '#eab308',
        LOW_P4: '#10b981',
      };
      const strokeColor = colorMap[zone.triage_level] || '#00f0ff';

      const circle = L.circle([zone.center_lat, zone.center_lon], {
        radius: zone.radius_meters || 450,
        color: strokeColor,
        weight: 2,
        opacity: 0.85,
        fillColor: strokeColor,
        fillOpacity: zone.triage_level === 'CRITICAL_P1' ? 0.25 : 0.15,
      });

      const popupHtml = `
        <div style="background: #0d131f; color: #fff; padding: 10px; font-family: monospace; border-radius: 6px; border: 1px solid ${strokeColor}; font-size: 12px; min-width: 200px;">
          <div style="font-weight: bold; font-size: 13px; color: ${strokeColor}; margin-bottom: 4px;">
            ${zone.name}
          </div>
          <div style="color: #94a3b8; font-size: 11px; margin-bottom: 6px;">${zone.code} // ${zone.triage_level}</div>
          <div style="display: flex; justify-content: space-between; margin-bottom: 3px;">
            <span style="color: #94a3b8;">Priority Score:</span>
            <strong style="color: #fff;">${zone.priority_score} / 100</strong>
          </div>
          <div style="display: flex; justify-content: space-between; margin-bottom: 3px;">
            <span style="color: #94a3b8;">Victims Stranded:</span>
            <strong style="color: #f59e0b;">~${zone.estimated_stranded_count}</strong>
          </div>
          <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
            <span style="color: #94a3b8;">Water Depth:</span>
            <strong style="color: #00f0ff;">${zone.water_level_m}m</strong>
          </div>
          <div style="font-size: 10px; color: #64748b; border-top: 1px solid #1e293b; padding-top: 4px;">
            Required: ${zone.required_capabilities.join(', ')}
          </div>
        </div>
      `;

      circle.bindPopup(popupHtml);
      circle.on('click', () => onSelectZone(zone));
      layerGroup.addLayer(circle);

      // Label Marker at Zone Center
      const labelIcon = L.divIcon({
        className: 'custom-zone-label',
        html: `
          <div style="transform: translate(-50%, -50%); pointer-events: none;">
            <span style="background: rgba(13, 19, 31, 0.9); border: 1px solid ${strokeColor}; color: ${strokeColor}; font-size: 10px; font-family: monospace; font-weight: bold; padding: 2px 6px; border-radius: 4px; box-shadow: 0 0 10px rgba(0,0,0,0.8); white-space: nowrap;">
              ${zone.code} (${zone.priority_score})
            </span>
          </div>
        `,
        iconSize: [0, 0],
      });
      const labelMarker = L.marker([zone.center_lat, zone.center_lon], { icon: labelIcon });
      layerGroup.addLayer(labelMarker);
    });

    // 2. Render Bhatia Bridge Collapse Point (If Act 2 or 3)
    if (currentAct >= 2) {
      const bridgeIcon = L.divIcon({
        className: 'bridge-collapse-marker',
        html: `
          <div style="transform: translate(-50%, -50%); background: #ef4444; color: #fff; padding: 4px 8px; border-radius: 4px; font-family: monospace; font-size: 10px; font-weight: bold; border: 2px solid #fff; box-shadow: 0 0 15px rgba(239,68,68,0.9); display: flex; align-items: center; gap: 4px; white-space: nowrap;">
            <span>⚠️ BHATIA BRIDGE COLLAPSED</span>
          </div>
        `,
        iconSize: [0, 0],
      });
      const bridgeMarker = L.marker([13.0845, 80.2735], { icon: bridgeIcon });
      bridgeMarker.bindPopup(`
        <div style="background: #0d131f; color: #fff; padding: 8px; font-family: monospace; font-size: 12px; border: 1px solid #ef4444;">
          <strong style="color: #ef4444;">CRITICAL INFRASTRUCTURE FAILURE</strong><br>
          Bhatia Bridge structural collapse. Primary arterial blocked. Amphibious or northern detour required.
        </div>
      `);
      layerGroup.addLayer(bridgeMarker);
    }

    // 3. Render Emergency Resources and Dispatch Trajectories
    const zoneMap = new Map(zones.map((z) => [z.id, z]));

    resources.forEach((res) => {
      // Find active allocation for this resource
      const decision = currentPlan?.decisions.find((d) => d.resource_id === res.id);
      const isAssigned = !!decision;
      const targetZone = decision ? zoneMap.get(decision.target_zone_id) : null;

      // Draw Trajectory line from resource to target zone
      if (isAssigned && targetZone) {
        const isDiverted = currentAct === 2 && decision?.status !== 'APPROVED';
        const trajectoryColor = isDiverted ? '#f59e0b' : '#00f0ff';

        const polyline = L.polyline(
          [
            [res.current_lat, res.current_lon],
            [targetZone.center_lat, targetZone.center_lon],
          ],
          {
            color: trajectoryColor,
            weight: 2,
            dashArray: '6, 8',
            opacity: 0.75,
          }
        );

        polyline.bindTooltip(
          `Unit ${res.code} ➔ ${targetZone.name} (ETA: ${decision.eta_minutes}m)`,
          {
            sticky: true,
            className: 'bg-eoc-panel text-white font-mono text-[10px] border border-cyan-500',
          }
        );
        layerGroup.addLayer(polyline);
      }

      // Unit Icon
      const unitIcon = L.divIcon({
        className: 'resource-unit-marker',
        html: `
          <div style="transform: translate(-50%, -50%); display: flex; flex-direction: column; align-items: center;">
            <div style="background: ${isAssigned ? '#00f0ff' : '#64748b'}; color: #070b12; font-weight: bold; font-family: monospace; font-size: 9px; padding: 2px 5px; border-radius: 3px; border: 1px solid #fff; box-shadow: 0 0 8px rgba(0,240,255,0.6); white-space: nowrap;">
              ${res.code}
            </div>
            <div style="width: 6px; height: 6px; background: #fff; border-radius: 50%; margin-top: 1px;"></div>
          </div>
        `,
        iconSize: [0, 0],
      });

      const resMarker = L.marker([res.current_lat, res.current_lon], { icon: unitIcon });
      resMarker.bindPopup(`
        <div style="background: #0d131f; color: #fff; padding: 8px; font-family: monospace; font-size: 11px; border: 1px solid #00f0ff; min-width: 180px;">
          <div style="color: #00f0ff; font-weight: bold;">${res.name} (${res.code})</div>
          <div style="color: #94a3b8; font-size: 10px; margin-bottom: 4px;">Base: ${res.base_station}</div>
          <div>Status: <strong style="color: #10b981;">${res.status}</strong></div>
          <div>Speed: ${res.speed_kmh} km/h | Cap: ${res.capacity_persons} pers</div>
          <div style="margin-top: 4px; font-size: 10px; color: #cbd5e1;">Capabilities: ${res.capabilities.join(', ')}</div>
          ${decision ? `<div style="margin-top: 4px; color: #fbbf24; border-top: 1px solid #334155; padding-top: 3px;">Assigned: ${decision.target_zone_name} (ETA ${decision.eta_minutes}m)</div>` : ''}
        </div>
      `);
      layerGroup.addLayer(resMarker);
    });
  }, [zones, resources, currentPlan, incidents, currentAct]);

  return (
    <div className="relative w-full h-full bg-eoc-darkest border border-eoc-border rounded-lg overflow-hidden flex flex-col">
      {/* Map Header Overlay */}
      <div className="absolute top-3 left-3 z-[1000] bg-eoc-darkest/90 backdrop-blur-md border border-eoc-border px-3 py-1.5 rounded text-xs font-mono flex items-center gap-3 shadow-lg">
        <span className="flex items-center gap-1.5 text-eoc-accent font-semibold">
          <span className="w-2 h-2 rounded-full bg-eoc-accent animate-ping"></span>
          GEOSPATIAL SITUATION RADAR
        </span>
        <span className="text-slate-500">|</span>
        <span className="text-slate-300">Active Sectors: <strong className="text-white">{zones.length}</strong></span>
        <span className="text-slate-500">|</span>
        <span className="text-slate-300">Fleet Units: <strong className="text-white">{resources.length}</strong></span>
      </div>

      {/* Map Canvas */}
      <div ref={mapContainerRef} className="w-full h-full z-0" />

      {/* Map Legend */}
      <div className="absolute bottom-3 left-3 z-[1000] bg-eoc-darkest/90 backdrop-blur-md border border-eoc-border px-3 py-2 rounded text-[10px] font-mono flex items-center gap-4 text-slate-300 shadow-lg">
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-rose-500"></span>
          <span>P1 Critical</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span>
          <span>P2 High</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-yellow-500"></span>
          <span>P3 Medium</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded bg-cyan-400"></span>
          <span>Fleet Unit</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-3 border-b-2 border-dashed border-cyan-400"></span>
          <span>Transit Vector</span>
        </div>
      </div>
    </div>
  );
};
