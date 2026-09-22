import React, { useEffect, useState, useRef } from 'react';
import { createRoot } from 'react-dom/client';
import {
  MapContainer,
  TileLayer,
  CircleMarker,
  Marker,
  Popup,
  Polyline,
  Circle,
  useMap
} from 'react-leaflet';
import L from 'leaflet';
import {
  Flame,
  ShieldAlert,
  AlertTriangle,
  Wind,
  Activity,
  Building2,
  CheckCircle2,
  FileDown,
  Radio,
  Search,
  RefreshCw,
  Eye,
  Hospital,
  Zap,
  School,
  X,
  Printer
} from 'lucide-react';
import './style.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

// Custom icons
const createCustomIcon = (color, symbol) => {
  return L.divIcon({
    className: 'custom-div-icon',
    html: `<div style="background:${color};width:26px;height:26px;border-radius:50%;border:2px solid white;display:flex;align-items:center;justify-content:center;color:white;font-weight:bold;font-size:12px;box-shadow:0 0 8px ${color}">${symbol}</div>`,
    iconSize: [26, 26],
    iconAnchor: [13, 13]
  });
};

const indIcon = createCustomIcon('#9333ea', '🏭');
const hospIcon = createCustomIcon('#0ea5e9', '🏥');
const powerIcon = createCustomIcon('#eab308', '⚡');
const schoolIcon = createCustomIcon('#10b981', '🏫');

// Helper to center map on select
function MapRecenter({ lat, lon }) {
  const map = useMap();
  useEffect(() => {
    if (lat && lon) {
      map.flyTo([lat, lon], 12, { animate: true, duration: 1.2 });
    }
  }, [lat, lon, map]);
  return null;
}

function App() {
  const [events, setEvents] = useState([]);
  const [stats, setStats] = useState(null);
  const [selectedId, setSelectedId] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [simulating, setSimulating] = useState(false);
  const [search, setSearch] = useState('');
  const [filterLevel, setFilterLevel] = useState('ALL');
  const [alertBanner, setAlertBanner] = useState(null);
  const [reportModal, setReportModal] = useState(null);
  const [showBuffers, setShowBuffers] = useState(true);
  const [showPlume, setShowPlume] = useState(true);
  const [showAssets, setShowAssets] = useState(true);
  const [validationSuccess, setValidationSuccess] = useState(null);

  // Fetch stats and events list
  const loadData = async () => {
    try {
      const [sRes, eRes] = await Promise.all([
        fetch(`${API_URL}/events/stats`),
        fetch(`${API_URL}/events/?limit=100`)
      ]);
      const sData = await sRes.json();
      const eData = await eRes.json();
      setStats(sData);
      setEvents(eData.events || []);

      // Auto-select first critical or first event
      if (!selectedId && eData.events && eData.events.length > 0) {
        const topEvent = eData.events.find(x => x.risk_level === 'CRITICAL') || eData.events[0];
        selectEvent(topEvent.event_id);
      }
    } catch (err) {
      console.error('Failed to load initial data:', err);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 45000);
    return () => clearInterval(interval);
  }, []);

  const selectEvent = async (id) => {
    setSelectedId(id);
    setLoading(true);
    setValidationSuccess(null);
    try {
      const res = await fetch(`${API_URL}/events/${id}/analysis?refresh=true`);
      const data = await res.json();
      setAnalysis(data);

      if (data.risk?.level === 'CRITICAL') {
        setAlertBanner(`EMERGENCY ALERT: Critical Anomaly at ${id} (FRP ${data.event.frp_max} MW) - Sensitive Infrastructure Downwind`);
      }
    } catch (err) {
      console.error('Analysis failed:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSimulatePass = async () => {
    setSimulating(true);
    try {
      const res = await fetch(`${API_URL}/events/simulate-stream`, { method: 'POST' });
      const simData = await res.json();
      setAlertBanner(`SATELLITE PASS PROCESSED: ${simData.message}`);
      await loadData();
      if (simData.simulated_events && simData.simulated_events[0]) {
        selectEvent(simData.simulated_events[0]);
      }
    } catch (err) {
      console.error('Simulation error:', err);
    } finally {
      setSimulating(false);
    }
  };

  const handleValidate = async (label) => {
    if (!selectedId) return;
    try {
      const res = await fetch(`${API_URL}/events/${selectedId}/validate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ label, reason: 'Analyst verified via Mission Control UI', analyst: 'Lead Disaster Analyst' })
      });
      if (res.ok) {
        setValidationSuccess(`Validated as ${label}`);
        setTimeout(() => setValidationSuccess(null), 4000);
        loadData();
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleOpenReport = async () => {
    if (!selectedId) return;
    try {
      const res = await fetch(`${API_URL}/events/${selectedId}/report`);
      const data = await res.json();
      setReportModal(data);
    } catch (err) {
      console.error('Report fetch failed:', err);
    }
  };

  // Filter events
  const filteredEvents = events.filter(e => {
    const matchesSearch = e.event_id.toLowerCase().includes(search.toLowerCase());
    const matchesFilter = filterLevel === 'ALL' || e.risk_level === filterLevel;
    return matchesSearch && matchesFilter;
  });

  const curEvent = analysis?.event;
  const curPlume = analysis?.plume;
  const curRisk = analysis?.risk;
  const curCtx = analysis?.context;

  return (
    <div className="tg-app">
      {/* Top Navigation Bar */}
      <header className="tg-header">
        <div className="tg-brand">
          <div className="tg-logo">
            <Flame size={20} color="white" />
          </div>
          <div className="tg-title">
            <h1>ThermalGuard</h1>
            <span>Smart India Hackathon 2026 · PS SIH26162</span>
          </div>
        </div>

        {stats && (
          <div className="tg-header-stats">
            <div className="stat-pill critical">
              <ShieldAlert size={14} color="#ef4444" />
              <span>Critical: <b>{stats.critical_count}</b></span>
            </div>
            <div className="stat-pill high">
              <AlertTriangle size={14} color="#f97316" />
              <span>High: <b>{stats.high_count}</b></span>
            </div>
            <div className="stat-pill active-fires">
              <Flame size={14} color="#f59e0b" />
              <span>Avg FRP: <b>{stats.average_frp_mw} MW</b></span>
            </div>
            <div className="stat-pill">
              <Building2 size={14} color="#06b6d4" />
              <span>Facilities Monitored: <b>{stats.monitored_facilities}</b></span>
            </div>
          </div>
        )}

        <button
          className="btn-sim"
          onClick={handleSimulatePass}
          disabled={simulating}
          title="Simulate incoming satellite pass with live FIRMS detections"
        >
          <RefreshCw size={14} className={simulating ? 'animate-spin' : ''} />
          {simulating ? 'Processing Orbit Pass...' : 'Simulate Live Satellite Feed'}
        </button>
      </header>

      {/* Real-Time Emergency Alert Banner */}
      {alertBanner && (
        <div className="alert-banner">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Radio size={16} className="animate-pulse" />
            <span>{alertBanner}</span>
          </div>
          <button
            onClick={() => setAlertBanner(null)}
            style={{ background: 'none', border: 'none', color: '#fca5a5', cursor: 'pointer' }}
          >
            ✕
          </button>
        </div>
      )}

      {/* 3-Column Command Center Workspace */}
      <div className="tg-main">
        {/* Left Column: Event Prioritization Queue */}
        <div className="tg-sidebar">
          <div className="sidebar-header">
            <div className="search-box">
              <Search size={14} />
              <input
                type="text"
                placeholder="Search by Event ID (e.g. TG-000098)..."
                value={search}
                onChange={e => setSearch(e.target.value)}
              />
            </div>

            <div className="filter-chips">
              {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map(lvl => (
                <button
                  key={lvl}
                  className={`filter-chip ${lvl.toLowerCase()} ${filterLevel === lvl ? 'active' : ''}`}
                  onClick={() => setFilterLevel(lvl)}
                >
                  {lvl}
                </button>
              ))}
            </div>
          </div>

          <div className="event-list">
            {filteredEvents.map(e => (
              <div
                key={e.event_id}
                className={`event-card ${selectedId === e.event_id ? 'active' : ''}`}
                onClick={() => selectEvent(e.event_id)}
              >
                <div className="event-card-header">
                  <span className="event-id">{e.event_id}</span>
                  <span className={`badge ${e.risk_level}`}>{e.risk_level}</span>
                </div>
                <div className="event-card-body">
                  <span>FRP: <b>{e.frp_max.toFixed(1)} MW</b></span>
                  <span>Confidence: <b>{e.confidence_mean.toFixed(0)}%</b></span>
                  <span>{e.detection_count} pts</span>
                </div>
                <div className="event-card-footer">
                  <span>Score: {e.risk_score || 0}/100</span>
                  <span>{e.ai_label || 'EVALUATING'}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Center Column: Interactive Geospatial Leaflet Map */}
        <div className="tg-center">
          <div className="map-overlay-controls">
            <label className="overlay-toggle">
              <input
                type="checkbox"
                checked={showBuffers}
                onChange={e => setShowBuffers(e.target.checked)}
              />
              Evacuation Buffers
            </label>
            <label className="overlay-toggle">
              <input
                type="checkbox"
                checked={showPlume}
                onChange={e => setShowPlume(e.target.checked)}
              />
              Wind Plume Vector
            </label>
            <label className="overlay-toggle">
              <input
                type="checkbox"
                checked={showAssets}
                onChange={e => setShowAssets(e.target.checked)}
              />
              Industrial & Critical Assets
            </label>
          </div>

          <MapContainer
            id="map-container"
            center={[26.9, 89.5]}
            zoom={10}
            scrollWheelZoom={true}
          >
            <TileLayer
              attribution='&copy; <a href="https://carto.com/">CARTO</a>'
              url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            />

            {/* Recenter hook */}
            {curEvent && <MapRecenter lat={curEvent.latitude} lon={curEvent.longitude} />}

            {/* All Thermal Events */}
            {events.map(ev => {
              const isSelected = ev.event_id === selectedId;
              const color =
                ev.risk_level === 'CRITICAL' ? '#ef4444' :
                ev.risk_level === 'HIGH' ? '#f97316' :
                ev.risk_level === 'MEDIUM' ? '#eab308' : '#10b981';

              const radius = Math.min(22, Math.max(8, Math.sqrt(ev.frp_max) * 2.2));

              return (
                <CircleMarker
                  key={ev.event_id}
                  center={[ev.latitude, ev.longitude]}
                  radius={radius}
                  pathOptions={{
                    color: isSelected ? '#60a5fa' : color,
                    weight: isSelected ? 3 : 1.5,
                    fillColor: color,
                    fillOpacity: isSelected ? 0.9 : 0.65
                  }}
                  eventHandlers={{
                    click: () => selectEvent(ev.event_id)
                  }}
                >
                  <Popup>
                    <div style={{ color: '#0f172a', fontSize: '12px' }}>
                      <b>{ev.event_id}</b> ({ev.risk_level})<br />
                      FRP Max: {ev.frp_max} MW<br />
                      Confidence: {ev.confidence_mean}%<br />
                      Detections: {ev.detection_count}
                    </div>
                  </Popup>
                </CircleMarker>
              );
            })}

            {/* Evacuation & Threat Buffer Rings for Selected Event */}
            {curEvent && showBuffers && (
              <>
                <Circle
                  center={[curEvent.latitude, curEvent.longitude]}
                  radius={500}
                  pathOptions={{ color: '#ef4444', weight: 1.5, dashArray: '4, 4', fillOpacity: 0.1 }}
                />
                <Circle
                  center={[curEvent.latitude, curEvent.longitude]}
                  radius={1500}
                  pathOptions={{ color: '#f97316', weight: 1, dashArray: '6, 6', fillOpacity: 0.05 }}
                />
                <Circle
                  center={[curEvent.latitude, curEvent.longitude]}
                  radius={3000}
                  pathOptions={{ color: '#38bdf8', weight: 1, dashArray: '8, 8', fillOpacity: 0.02 }}
                />
              </>
            )}

            {/* Downwind Plume Vector & Dispersion Line */}
            {curEvent && curPlume && showPlume && (
              <Polyline
                positions={[
                  [curEvent.latitude, curEvent.longitude],
                  [curPlume.plume_endpoint.latitude, curPlume.plume_endpoint.longitude]
                ]}
                pathOptions={{
                  color: '#f97316',
                  weight: 3,
                  dashArray: '5, 8'
                }}
              />
            )}

            {/* Nearby Industrial & Sensitive Assets from Context */}
            {curCtx?.osm && showAssets && (
              <>
                {curCtx.osm.industrial?.map((a, idx) => (
                  <Marker key={`ind-${idx}`} position={[a.lat, a.lon]} icon={indIcon}>
                    <Popup>
                      <div style={{ color: '#0f172a' }}>
                        <b>🏭 {a.name}</b><br />
                        Type: {a.subtype}<br />
                        Distance: {a.distance_km || 0} km
                      </div>
                    </Popup>
                  </Marker>
                ))}

                {curCtx.osm.hospitals?.map((a, idx) => (
                  <Marker key={`hosp-${idx}`} position={[a.lat, a.lon]} icon={hospIcon}>
                    <Popup>
                      <div style={{ color: '#0f172a' }}>
                        <b>🏥 {a.name}</b><br />
                        Emergency Hospital ({a.distance_km || 0} km)
                      </div>
                    </Popup>
                  </Marker>
                ))}

                {curCtx.osm.power?.map((a, idx) => (
                  <Marker key={`pwr-${idx}`} position={[a.lat, a.lon]} icon={powerIcon}>
                    <Popup>
                      <div style={{ color: '#0f172a' }}>
                        <b>⚡ {a.name}</b><br />
                        Critical Power Infrastructure
                      </div>
                    </Popup>
                  </Marker>
                ))}

                {curCtx.osm.schools?.map((a, idx) => (
                  <Marker key={`sch-${idx}`} position={[a.lat, a.lon]} icon={schoolIcon}>
                    <Popup>
                      <div style={{ color: '#0f172a' }}>
                        <b>🏫 {a.name}</b><br />
                        Educational Campus
                      </div>
                    </Popup>
                  </Marker>
                ))}
              </>
            )}
          </MapContainer>

          {/* Map Legend */}
          <div className="map-legend">
            <h4>Map Overlay Legend</h4>
            <div className="legend-item">
              <span className="legend-dot critical"></span> Critical Fire Anomaly
            </div>
            <div className="legend-item">
              <span className="legend-dot high"></span> High Threat Anomaly
            </div>
            <div className="legend-item">
              <span className="legend-dot medium"></span> Moderate / Persistent
            </div>
            <div className="legend-item">
              <span className="legend-dot low"></span> Low / Benign
            </div>
            <div className="legend-item">
              <span className="legend-dot industrial"></span> Industrial Complex
            </div>
            <div className="legend-item">
              <span className="legend-dot sensitive"></span> Hospital / School / Power
            </div>
          </div>
        </div>

        {/* Right Column: Incident Intelligence Dossier Drawer */}
        <div className="tg-dossier">
          {loading ? (
            <div className="dossier-empty">
              <Activity className="animate-spin" size={32} color="#3b82f6" />
              <p>Synthesizing Multi-Modal Geospatial Intelligence...</p>
            </div>
          ) : analysis ? (
            <>
              {/* Dossier Header */}
              <div className="dossier-card">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <h2 style={{ fontSize: '1.2rem', fontWeight: 800 }}>{curEvent.event_id}</h2>
                    <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
                      Coords: {curEvent.latitude.toFixed(4)}, {curEvent.longitude.toFixed(4)}
                    </span>
                  </div>
                  <span className={`badge ${curRisk?.level}`}>{curRisk?.level} RISK</span>
                </div>
              </div>

              {/* Satellite Telemetry */}
              <div className="dossier-card">
                <h3><Radio size={14} color="#3b82f6" /> Satellite Telemetry (VIIRS 375m)</h3>
                <div className="telemetry-grid">
                  <div className="telemetry-item">
                    <label>Peak FRP</label>
                    <value style={{ color: '#ef4444' }}>{curEvent.frp_max} MW</value>
                  </div>
                  <div className="telemetry-item">
                    <label>Detection Conf.</label>
                    <value>{curEvent.confidence_mean.toFixed(0)}%</value>
                  </div>
                  <div className="telemetry-item">
                    <label>Cluster Size</label>
                    <value>{curEvent.detection_count} points</value>
                  </div>
                  <div className="telemetry-item">
                    <label>Brightness Temp</label>
                    <value>{curEvent.bright_ti4_max.toFixed(1)} K</value>
                  </div>
                </div>
              </div>

              {/* Dual AI Models Consensus (XGBoost + FNN) */}
              <div className="dossier-card">
                <h3><Activity size={14} color="#8b5cf6" /> Dual AI Consensus Engine</h3>
                <div className="model-row">
                  <div>
                    <b>XGBoost Classifier</b>
                    <div style={{ color: '#94a3b8', fontSize: '0.72rem' }}>Gradient Boosted Trees</div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <span className="model-tag" style={{ background: 'rgba(59, 130, 246, 0.2)', color: '#60a5fa' }}>
                      {analysis.ml?.label || 'ANALYZING'}
                    </span>
                    <div style={{ fontSize: '0.7rem', color: '#64748b' }}>
                      Conf: {(analysis.ml?.confidence * 100).toFixed(1)}%
                    </div>
                  </div>
                </div>

                <div className="model-row">
                  <div>
                    <b>FNN Neural Network</b>
                    <div style={{ color: '#94a3b8', fontSize: '0.72rem' }}>Deep MLP (23 &rarr; 64 &rarr; 32 &rarr; 4)</div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <span className="model-tag" style={{ background: 'rgba(168, 85, 247, 0.2)', color: '#c084fc' }}>
                      {analysis.fnn?.predicted_class || 'ANALYZING'}
                    </span>
                    <div style={{ fontSize: '0.7rem', color: '#64748b' }}>
                      Conf: {(analysis.fnn?.confidence * 100).toFixed(1)}%
                    </div>
                  </div>
                </div>
              </div>

              {/* Explainable Contributing Factors Breakdown */}
              <div className="dossier-card">
                <h3><ShieldAlert size={14} color="#f59e0b" /> Explainable Risk Factors ({curRisk?.score}/100)</h3>
                <div className="factor-bar-list">
                  {curRisk?.factor_contributions?.map((f, i) => (
                    <div key={i} className="factor-item">
                      <div className="factor-header">
                        <span>{f.factor} ({f.detail})</span>
                        <b style={{ color: '#f87171' }}>+{f.points} pts</b>
                      </div>
                      <div className="factor-track">
                        <div
                          className="factor-fill"
                          style={{ width: `${Math.min(100, f.points * 3)}%` }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Plume & Wind Spread Dynamics */}
              {curPlume && (
                <div className="dossier-card">
                  <h3><Wind size={14} color="#06b6d4" /> Atmospheric Spread Vector</h3>
                  <div className="telemetry-grid">
                    <div className="telemetry-item">
                      <label>Wind Speed</label>
                      <value>{curPlume.wind_speed_kmh} km/h</value>
                    </div>
                    <div className="telemetry-item">
                      <label>Downwind Trajectory</label>
                      <value>{curPlume.downwind_bearing_deg}&deg;</value>
                    </div>
                    <div className="telemetry-item">
                      <label>Spread Hazard Index</label>
                      <value style={{ color: curPlume.fire_spread_index > 50 ? '#ef4444' : '#f59e0b' }}>
                        {curPlume.fire_spread_index}/100
                      </value>
                    </div>
                    <div className="telemetry-item">
                      <label>Threatened Assets</label>
                      <value>{curPlume.threatened_count} downwind</value>
                    </div>
                  </div>
                </div>
              )}

              {/* Automated Forensic Investigation Report */}
              <div className="dossier-card">
                <h3><Eye size={14} color="#10b981" /> Forensic Agent Assessment</h3>
                <p style={{ fontSize: '0.78rem', color: '#cbd5e1', lineHeight: '1.4' }}>
                  {analysis.investigation?.executive_summary}
                </p>

                <div style={{ marginTop: '8px' }}>
                  <b style={{ fontSize: '0.72rem', color: '#94a3b8', textTransform: 'uppercase' }}>Recommended Actions:</b>
                  <ul style={{ paddingLeft: '16px', fontSize: '0.75rem', marginTop: '4px', color: '#e2e8f0' }}>
                    {analysis.investigation?.recommended_actions?.map((act, i) => (
                      <li key={i} style={{ marginBottom: '3px' }}>{act}</li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Human-in-the-Loop Analyst Validation */}
              <div className="dossier-card">
                <h3><CheckCircle2 size={14} color="#3b82f6" /> Analyst Ground-Truth Verification</h3>
                {validationSuccess && (
                  <div style={{ padding: '6px 10px', background: 'rgba(16, 185, 129, 0.2)', border: '1px solid #10b981', borderRadius: '4px', color: '#6ee7b7', fontSize: '0.75rem' }}>
                    ✓ {validationSuccess}
                  </div>
                )}
                <div className="action-buttons">
                  <button
                    className="btn-validate fire"
                    onClick={() => handleValidate('CRITICAL_INDUSTRIAL_FIRE')}
                  >
                    Confirm Fire
                  </button>
                  <button
                    className="btn-validate persistent"
                    onClick={() => handleValidate('PERSISTENT_INDUSTRIAL_SOURCE')}
                  >
                    Confirm Flare / Kiln
                  </button>
                </div>

                <button className="btn-report" onClick={handleOpenReport}>
                  <FileDown size={16} />
                  Export Official Incident Dossier
                </button>
              </div>
            </>
          ) : (
            <div className="dossier-empty">
              <Flame size={48} color="#334155" />
              <h3>Select a Thermal Anomaly</h3>
              <p>Click any event marker on the live map or from the priority queue to inspect forensic intelligence.</p>
            </div>
          )}
        </div>
      </div>

      {/* Official Emergency Incident Report Modal */}
      {reportModal && (
        <div className="modal-overlay" onClick={() => setReportModal(null)}>
          <div className="modal-card" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <ShieldAlert size={22} color="#ef4444" />
                <div>
                  <h3 style={{ fontSize: '1.05rem', color: 'white' }}>OFFICIAL INCIDENT DOSSIER</h3>
                  <span style={{ fontSize: '0.7rem', color: '#94a3b8' }}>Dossier ID: {reportModal.report_id}</span>
                </div>
              </div>
              <button
                onClick={() => setReportModal(null)}
                style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer', fontSize: '18px' }}
              >
                ✕
              </button>
            </div>

            <div className="modal-body">
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px', padding: '12px', background: '#1e293b', borderRadius: '8px' }}>
                <div>
                  <label style={{ fontSize: '0.65rem', color: '#94a3b8', textTransform: 'uppercase' }}>Severity</label>
                  <p style={{ fontWeight: 800, color: '#ef4444' }}>{reportModal.severity}</p>
                </div>
                <div>
                  <label style={{ fontSize: '0.65rem', color: '#94a3b8', textTransform: 'uppercase' }}>Classification</label>
                  <p style={{ fontWeight: 700, color: 'white' }}>{reportModal.classification}</p>
                </div>
                <div>
                  <label style={{ fontSize: '0.65rem', color: '#94a3b8', textTransform: 'uppercase' }}>Coordinates</label>
                  <p style={{ fontFamily: 'monospace' }}>{reportModal.coordinates?.latitude}, {reportModal.coordinates?.longitude}</p>
                </div>
                <div>
                  <label style={{ fontSize: '0.65rem', color: '#94a3b8', textTransform: 'uppercase' }}>Sensor</label>
                  <p>{reportModal.satellite_telemetry?.sensor}</p>
                </div>
              </div>

              <div>
                <h4 style={{ color: '#38bdf8', marginBottom: '6px' }}>1. SITUATION ASSESSMENT</h4>
                <p style={{ lineHeight: '1.5' }}>{reportModal.executive_summary}</p>
              </div>

              <div>
                <h4 style={{ color: '#38bdf8', marginBottom: '6px' }}>2. ATMOSPHERIC PLUME & DISPERSION</h4>
                <p>
                  Downwind trajectory heading <b>{reportModal.plume_meteorology?.downwind_trajectory_deg}&deg;</b> at <b>{reportModal.plume_meteorology?.wind_speed_kmh} km/h</b>.
                  Fire Spread Hazard Index is rated at <b>{reportModal.plume_meteorology?.fire_spread_index}/100</b>.
                </p>
              </div>

              <div>
                <h4 style={{ color: '#38bdf8', marginBottom: '6px' }}>3. AI CONSENSUS & CAUSAL EVIDENCE</h4>
                <p>
                  <b>XGBoost Prediction:</b> {reportModal.ai_models_consensus?.xgboost_prediction} ({(reportModal.ai_models_consensus?.xgboost_confidence * 100).toFixed(1)}% confidence)<br />
                  <b>FNN Neural Network:</b> {reportModal.ai_models_consensus?.fnn_neural_prediction} ({(reportModal.ai_models_consensus?.fnn_confidence * 100).toFixed(1)}% confidence)
                </p>
              </div>

              <div>
                <h4 style={{ color: '#ef4444', marginBottom: '6px' }}>4. EMERGENCY ACTION MANDATES</h4>
                <ul style={{ paddingLeft: '20px' }}>
                  {reportModal.tactical_recommendations?.map((r, i) => (
                    <li key={i} style={{ marginBottom: '4px' }}>{r}</li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="modal-footer">
              <button
                className="btn-validate"
                onClick={() => window.print()}
                style={{ background: '#3b82f6', color: 'white' }}
              >
                <Printer size={14} /> Print / Save PDF
              </button>
              <button
                className="btn-validate"
                onClick={() => setReportModal(null)}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);
