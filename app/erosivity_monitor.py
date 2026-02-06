# Forced reload comment
import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import folium_static
from datetime import datetime, timedelta, timezone
from pyproj import Transformer
import math
from io import BytesIO
import base64
from scipy.interpolate import Rbf
from PIL import Image, ImageColor
import os

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)


# ── Internationalization (i18n) ──
TRANSLATIONS = {
    "en": {
        # Page
        "page_title": "Rainfall – Erosion Alert",
        "main_title": "Rainfall Erosivity Monitor – REM",

        # Sidebar
        "control_panel": "Control Panel",
        "data_source": "Data Source",
        "location": "Location:",
        "location_help": "Default location: Kaindorf\n\nLat: 47.2154074 Lon: 15.9018356",
        "select_area": "Select your area of interest by entering coordinates below:",
        "latitude": "Latitude (-90 to 90)",
        "longitude": "Longitude (-180 to 180)",
        "refresh_coords": "Refresh Coords",
        "buffer_radius": "Buffer Radius (km)",
        "custom_date_range": "Custom Date Range",
        "date_range_help": "**Limitations:**\n\n- Start date must be before End date\n- Maximum date range: 45 days\n- End date cannot be in the future\n\nClick 'Fetch Data' to load data for the selected range.",
        "start_date": "Start date",
        "end_date": "End date",
        "fetch_data": "Fetch Data",
        "aggregation_interval": "Aggregation interval",
        "energy_equation": "Energy equation",
        "energy_equation_help": "**RUSLE2** (recommended): e = 0.29[1 - 0.72 exp(-0.082 i)], McGregor et al. (1995).\n\n**USLE**: e = 0.119 + 0.0873 log₁₀(i), capped at 0.283, Wischmeier & Smith (1978).",
        "show_heatmap": "Show EI30 Heatmap",
        "stations": "Stations",
        "language": "Language",

        # Aggregation options
        "10_min": "10 min",
        "30_min": "30 min",
        "1_hour": "1 hour",
        "3_hours": "3 hours",
        "6_hours": "6 hours",
        "24_hours": "24 hours",

        # Alert levels
        "high_erosion_risk": "High erosion risk",
        "moderate_erosion_risk": "Moderate erosion risk",
        "low_erosion_risk": "Low erosion risk",
        "no_risk": "No risk",

        # AMC classes
        "amc_wet": "Wet — high runoff potential",
        "amc_moderate": "Moderate",
        "amc_dry": "Dry — low runoff potential",

        # Contact
        "contact": "Contact",

        # Messages
        "map_centered_at": "Map centered at:",
        "lat_range_error": "Latitude must be between -90 and 90, and longitude between -180 and 180.",
        "invalid_coords_error": "Please enter valid numeric values (float or integer only).",
        "start_before_end_error": "Start date must be before End date.",
        "date_range_exceeded": "Date range exceeds 45 days ({days} days selected). Please select a shorter range.",
        "loading_metadata": "Loading station metadata...",
        "failed_load_metadata": "Failed to load station metadata:",
        "no_stations_found": "No matching stations found within the buffer zone.",
        "select_station": "Select at least one station in the sidebar.",
        "adjust_date_range": "Adjust the date range in the sidebar and click **Fetch Data** to load precipitation data.",
        "date_changed_warning": "Date range has changed. Currently showing data from **{start}** to **{end}**. Click **Fetch Data** to update.",
        "precipitation_caption": "Precipitation from {start} to {end} from GeoSphere Austria — {desc}",
        "inca_info": "INCA grid data: Virtual stations created based on hydrographic station locations (https://ehyd.gv.at/). I30 is approximated from hourly data and may underestimate sub-hourly peak intensities.",
        "fetching_data": "Fetching weather data...",
        "failed_fetch_data": "Failed to fetch weather data:",
        "no_data_returned": "No data returned for the selected stations and time range.",
        "generating_heatmap": "Generating interpolation heatmap...",
        "heatmap_min_stations": "Heatmap requires at least 3 stations with data to be selected.",
        "heatmap_error": "Could not generate heatmap. Not enough data or an error occurred during interpolation.",

        # Section headers
        "field_survey_recommendation": "Field Survey Recommendation",
        "station_map": "Station Map",
        "precipitation_totals": "Precipitation ({interval} totals)",
        "cumulative_precipitation": "Cumulative Precipitation",
        "rainfall_intensity": "Rainfall Intensity",
        "summary_statistics": "Summary Statistics",
        "context_data": "Context Data",
        "antecedent_rainfall": "Antecedent Rainfall (5 days before window)",
        "snowmelt_risk_assessment": "Snowmelt Risk Assessment",
        "raw_aggregated_data": "Raw Aggregated Data",
        "references": "References",
        "storm_events": "Storm Events ({count} storms detected)",

        # Field survey messages
        "erosive_event_in_progress": "**Erosive event in progress at {name}** — {label} (EI30 = {ei30}). Total so far: {rain} mm, I30: {i30} mm/h. Monitor conditions and plan survey after event ends.",
        "field_survey_recommended": "**Field survey recommended at {name}** — {label} (EI30 = {ei30}). Event ended ~{hours}h ago ({time} UTC). Rain: {rain} mm in {duration}h, I30: {i30} mm/h.",
        "alert_station_info": "**{name}** — {label} (EI30 = {ei30}), but erosive events ended > 24h ago.",
        "no_erosive_events": "No erosive storm events detected in the selected time window. No field survey needed.",

        # Storm table
        "storm_delineation_caption": "Storm delineation: {gap}h gap with < {rain} mm. Erosive threshold: >= {min_rain} mm total (or >= {intense} mm in 15 min). '*' = possibly ongoing.",

        # Table columns
        "col_station": "Station",
        "col_start": "Start (UTC)",
        "col_end": "End (UTC)",
        "col_duration": "Duration (h)",
        "col_rain": "Rain (mm)",
        "col_i30": "I30 (mm/h)",
        "col_ei30": "EI30",
        "col_erosive": "Erosive",
        "col_alert": "Alert",
        "col_storms": "Storms",
        "col_total": "Total (mm)",
        "col_max_ei30": "Max EI30",
        "col_r_sum": "R sum",
        "col_antecedent": "Antecedent 5d (mm)",
        "col_amc_class": "AMC Class",
        "col_snowmelt_risk": "Snowmelt risk",
        "col_latest_temp": "Latest Temp (°C)",
        "col_snow_depth": "Snow Depth (cm)",
        "col_description": "Description",
        "col_5day_antecedent": "5-day Antecedent (mm)",
        "col_latest_temp_short": "Latest Temp",
        "col_snow_depth_short": "Snow Depth",

        # Yes/No
        "yes": "Yes",
        "no": "No",
        "na": "N/A",

        # Chart labels
        "rainfall_label": "Rainfall ({interval}) [mm]",
        "time_label": "Time",
        "cumulative_label": "Cumulative Rainfall [mm]",
        "intensity_label": "Intensity [mm/h]",

        # Map popup
        "altitude": "Altitude",
        "distance": "Distance",
        "total_rainfall": "Total rainfall",
        "buffer_selected": "{km} km buffer (selected)",
        "buffer_ref": "{km} km buffer",

        # References text
        "energy_equation_label": "Energy equation:",
        "storm_delineation_label": "Storm delineation:",
        "gap_label": "h gap /",
        "erosive_threshold_label": "Erosive threshold:",
    },
    "de": {
        # Page
        "page_title": "Niederschlag – Erosionswarnung",
        "main_title": "Niederschlagserosivitäts-Monitor – REM",

        # Sidebar
        "control_panel": "Steuerungspanel",
        "data_source": "Datenquelle",
        "location": "Standort:",
        "location_help": "Standardstandort: Kaindorf\n\nBreite: 47.2154074 Länge: 15.9018356",
        "select_area": "Wählen Sie Ihr Interessengebiet durch Eingabe der Koordinaten:",
        "latitude": "Breitengrad (-90 bis 90)",
        "longitude": "Längengrad (-180 bis 180)",
        "refresh_coords": "Koordinaten aktualisieren",
        "buffer_radius": "Pufferradius (km)",
        "custom_date_range": "Benutzerdefinierter Datumsbereich",
        "date_range_help": "**Einschränkungen:**\n\n- Startdatum muss vor dem Enddatum liegen\n- Maximaler Datumsbereich: 45 Tage\n- Enddatum kann nicht in der Zukunft liegen\n\nKlicken Sie auf 'Daten abrufen', um Daten für den ausgewählten Bereich zu laden.",
        "start_date": "Startdatum",
        "end_date": "Enddatum",
        "fetch_data": "Daten abrufen",
        "aggregation_interval": "Aggregationsintervall",
        "energy_equation": "Energiegleichung",
        "energy_equation_help": "**RUSLE2** (empfohlen): e = 0.29[1 - 0.72 exp(-0.082 i)], McGregor et al. (1995).\n\n**USLE**: e = 0.119 + 0.0873 log₁₀(i), begrenzt auf 0.283, Wischmeier & Smith (1978).",
        "show_heatmap": "EI30-Heatmap anzeigen",
        "stations": "Stationen",
        "language": "Sprache",

        # Aggregation options
        "10_min": "10 Min",
        "30_min": "30 Min",
        "1_hour": "1 Stunde",
        "3_hours": "3 Stunden",
        "6_hours": "6 Stunden",
        "24_hours": "24 Stunden",

        # Alert levels
        "high_erosion_risk": "Hohes Erosionsrisiko",
        "moderate_erosion_risk": "Mäßiges Erosionsrisiko",
        "low_erosion_risk": "Geringes Erosionsrisiko",
        "no_risk": "Kein Risiko",

        # AMC classes
        "amc_wet": "Feucht — hohes Abflusspotenzial",
        "amc_moderate": "Mäßig",
        "amc_dry": "Trocken — geringes Abflusspotenzial",

        # Contact
        "contact": "Kontakt",

        # Messages
        "map_centered_at": "Karte zentriert auf:",
        "lat_range_error": "Breitengrad muss zwischen -90 und 90 liegen, Längengrad zwischen -180 und 180.",
        "invalid_coords_error": "Bitte geben Sie gültige numerische Werte ein (nur Dezimalzahlen oder Ganzzahlen).",
        "start_before_end_error": "Startdatum muss vor dem Enddatum liegen.",
        "date_range_exceeded": "Datumsbereich überschreitet 45 Tage ({days} Tage ausgewählt). Bitte wählen Sie einen kürzeren Bereich.",
        "loading_metadata": "Lade Stationsmetadaten...",
        "failed_load_metadata": "Fehler beim Laden der Stationsmetadaten:",
        "no_stations_found": "Keine passenden Stationen im Pufferbereich gefunden.",
        "select_station": "Wählen Sie mindestens eine Station in der Seitenleiste aus.",
        "adjust_date_range": "Passen Sie den Datumsbereich in der Seitenleiste an und klicken Sie auf **Daten abrufen**, um Niederschlagsdaten zu laden.",
        "date_changed_warning": "Datumsbereich wurde geändert. Aktuell werden Daten von **{start}** bis **{end}** angezeigt. Klicken Sie auf **Daten abrufen** zum Aktualisieren.",
        "precipitation_caption": "Niederschlag von {start} bis {end} von GeoSphere Austria — {desc}",
        "inca_info": "INCA-Rasterdaten: Virtuelle Stationen basierend auf hydrographischen Stationsstandorten (https://ehyd.gv.at/). I30 wird aus Stundendaten geschätzt und kann Spitzenintensitäten unter einer Stunde unterschätzen.",
        "fetching_data": "Rufe Wetterdaten ab...",
        "failed_fetch_data": "Fehler beim Abrufen der Wetterdaten:",
        "no_data_returned": "Keine Daten für die ausgewählten Stationen und den Zeitraum zurückgegeben.",
        "generating_heatmap": "Generiere Interpolations-Heatmap...",
        "heatmap_min_stations": "Für die Heatmap müssen mindestens 3 Stationen mit Daten ausgewählt sein.",
        "heatmap_error": "Heatmap konnte nicht generiert werden. Nicht genügend Daten oder ein Fehler bei der Interpolation.",

        # Section headers
        "field_survey_recommendation": "Feldbegehungsempfehlung",
        "station_map": "Stationskarte",
        "precipitation_totals": "Niederschlag ({interval} Summen)",
        "cumulative_precipitation": "Kumulativer Niederschlag",
        "rainfall_intensity": "Niederschlagsintensität",
        "summary_statistics": "Zusammenfassende Statistiken",
        "context_data": "Kontextdaten",
        "antecedent_rainfall": "Vorregen (5 Tage vor dem Zeitfenster)",
        "snowmelt_risk_assessment": "Schneeschmelze-Risikobewertung",
        "raw_aggregated_data": "Rohe aggregierte Daten",
        "references": "Referenzen",
        "storm_events": "Sturmereignisse ({count} Stürme erkannt)",

        # Field survey messages
        "erosive_event_in_progress": "**Erosives Ereignis im Gange bei {name}** — {label} (EI30 = {ei30}). Bisherige Summe: {rain} mm, I30: {i30} mm/h. Überwachen Sie die Bedingungen und planen Sie die Begehung nach Ende des Ereignisses.",
        "field_survey_recommended": "**Feldbegehung empfohlen bei {name}** — {label} (EI30 = {ei30}). Ereignis endete vor ~{hours}h ({time} UTC). Regen: {rain} mm in {duration}h, I30: {i30} mm/h.",
        "alert_station_info": "**{name}** — {label} (EI30 = {ei30}), aber erosive Ereignisse endeten vor > 24h.",
        "no_erosive_events": "Keine erosiven Sturmereignisse im ausgewählten Zeitfenster erkannt. Keine Feldbegehung erforderlich.",

        # Storm table
        "storm_delineation_caption": "Sturmabgrenzung: {gap}h Lücke mit < {rain} mm. Erosivitätsschwelle: >= {min_rain} mm gesamt (oder >= {intense} mm in 15 Min). '*' = möglicherweise noch andauernd.",

        # Table columns
        "col_station": "Station",
        "col_start": "Start (UTC)",
        "col_end": "Ende (UTC)",
        "col_duration": "Dauer (h)",
        "col_rain": "Regen (mm)",
        "col_i30": "I30 (mm/h)",
        "col_ei30": "EI30",
        "col_erosive": "Erosiv",
        "col_alert": "Warnung",
        "col_storms": "Stürme",
        "col_total": "Gesamt (mm)",
        "col_max_ei30": "Max EI30",
        "col_r_sum": "R Summe",
        "col_antecedent": "Vorregen 5T (mm)",
        "col_amc_class": "AMC-Klasse",
        "col_snowmelt_risk": "Schneeschmelzerisiko",
        "col_latest_temp": "Letzte Temp. (°C)",
        "col_snow_depth": "Schneehöhe (cm)",
        "col_description": "Beschreibung",
        "col_5day_antecedent": "5-Tage Vorregen (mm)",
        "col_latest_temp_short": "Letzte Temp.",
        "col_snow_depth_short": "Schneehöhe",

        # Yes/No
        "yes": "Ja",
        "no": "Nein",
        "na": "k.A.",

        # Chart labels
        "rainfall_label": "Niederschlag ({interval}) [mm]",
        "time_label": "Zeit",
        "cumulative_label": "Kumulativer Niederschlag [mm]",
        "intensity_label": "Intensität [mm/h]",

        # Map popup
        "altitude": "Höhe",
        "distance": "Entfernung",
        "total_rainfall": "Gesamtniederschlag",
        "buffer_selected": "{km} km Puffer (ausgewählt)",
        "buffer_ref": "{km} km Puffer",

        # References text
        "energy_equation_label": "Energiegleichung:",
        "storm_delineation_label": "Sturmabgrenzung:",
        "gap_label": "h Lücke /",
        "erosive_threshold_label": "Erosivitätsschwelle:",
    },
}


def get_text(key, lang="en", **kwargs):
    """Get translated text for a given key."""
    text = TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)
    if kwargs:
        text = text.format(**kwargs)
    return text


def get_alert_labels(lang):
    """Get alert labels based on language."""
    return {
        "high": get_text("high_erosion_risk", lang),
        "moderate": get_text("moderate_erosion_risk", lang),
        "low": get_text("low_erosion_risk", lang),
        "none": get_text("no_risk", lang),
    }


def get_amc_descriptions(lang):
    """Get AMC class descriptions based on language."""
    return {
        "AMC III": get_text("amc_wet", lang),
        "AMC II": get_text("amc_moderate", lang),
        "AMC I": get_text("amc_dry", lang),
    }


# ── API Configuration ──
API_HOST = "https://dataset.api.hub.geosphere.at"
API_VERSION = "v1"

DATA_SOURCES = {
    "TAWES Weather Station": {
        "resource_id": "tawes-v1-10min",
        "api_type": "station",
        "mode_data": "historical",
        "mode_meta": "current",
        "interval_minutes": 10,
        "request_params": "RR,TL,SCHNEE",
        "rain_param": "RR",
        "param_map": {"RR": "RR", "TL": "TL", "SCHNEE": "SCHNEE"},
        "description": "TAWES 10-min station data",
        "i30_correction": 1.0,  # 10-min intervals span exactly 30 min (3 intervals)
    },
    "Weather Station 10 min": {
        "resource_id": "klima-v2-10min",
        "api_type": "station",
        "mode_data": "historical",
        "mode_meta": "historical",
        "interval_minutes": 10,
        "request_params": "rr,tl,sh",
        "rain_param": "rr",
        "param_map": {"rr": "RR", "tl": "TL", "sh": "SCHNEE"},
        "description": "Klima v2 10-min station data",
        "i30_correction": 1.0,
    },
    "INCA Hourly": {
        "resource_id": "inca-v1-1h-1km",
        "api_type": "timeseries",
        "mode_data": "historical",
        "mode_meta": "historical",
        "interval_minutes": 60,
        "request_params": "RR,T2M",
        "rain_param": "RR",
        "param_map": {"RR": "RR", "T2M": "TL"},
        "description": "INCA 1h 1km grid (virtual stations from CSV)",
        "i30_correction": 1.0,  # already an approximation for hourly data
    },
}

# Storm delineation parameters (Wischmeier & Smith, 1978; Nearing et al., 2017)
STORM_GAP_HOURS = 6        # minimum dry gap separating storms
STORM_GAP_RAIN_MM = 1.27   # max rainfall during gap to count as "dry"
STORM_MIN_RAIN_MM = 12.7   # minimum total rain for an erosive storm
STORM_INTENSE_15MIN_MM = 6.0  # storms with >= this in ~15 min are included regardless



CSV_PATH = os.path.join(PROJECT_ROOT, "data", "messstellen_nlv.csv")

# CRS transformer: EPSG:31287 (MGI / Austria Lambert) → EPSG:4326 (WGS84)
_transformer = Transformer.from_crs("EPSG:31287", "EPSG:4326", always_xy=True)


def haversine_km(lat1, lon1, lat2, lon2):
    """Return the great-circle distance in km between two points."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))
         * math.sin(dlon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


AGGREGATION_OPTIONS_10MIN = {
    "10 min": "10min",
    "30 min": "30min",
    "1 hour": "1h",
    "24 hours": "24h",
}

AGGREGATION_OPTIONS_HOURLY = {
    "1 hour": "1h",
    "3 hours": "3h",
    "6 hours": "6h",
    "24 hours": "24h",
}

ALERT_THRESHOLDS = [
    (200, "red", "high_erosion_risk", "#e74c3c"),
    (100, "orange", "moderate_erosion_risk", "#e67e22"),
    (25, "yellow", "low_erosion_risk", "#f1c40f"),
    (0, "green", "no_risk", "#2ecc71"),
]


def get_alert_level(ei30, lang="en"):
    """Return (level_name, label, color_hex) for a given EI30 value."""
    for threshold, level, label_key, color in ALERT_THRESHOLDS:
        if ei30 >= threshold:
            return level, get_text(label_key, lang), color
    return "green", get_text("no_risk", lang), "#2ecc71"


# SCS/NRCS Antecedent Moisture Condition (5-day antecedent rainfall)
AMC_CLASSES = [
    (28.0, "AMC III", "amc_wet"),
    (13.0, "AMC II", "amc_moderate"),
    (0.0, "AMC I", "amc_dry"),
]


def classify_amc(antecedent_mm, lang="en"):
    """Classify 5-day antecedent rainfall into AMC I/II/III (SCS/NRCS)."""
    for threshold, cls, desc_key in AMC_CLASSES:
        if antecedent_mm >= threshold:
            return cls, get_text(desc_key, lang)
    return "AMC I", get_text("amc_dry", lang)


def build_api_url(api_type, mode, resource_id):
    """Construct a GeoSphere dataset API URL."""
    return f"{API_HOST}/{API_VERSION}/{api_type}/{mode}/{resource_id}"


# ── Station Metadata ──

@st.cache_data(ttl=600)
def load_csv_stations(buffer_km, center_lat, center_lon):
    """Load virtual stations from CSV, convert EPSG:31287 → WGS84, filter by buffer."""
    df = pd.read_csv(CSV_PATH, sep=";", encoding="latin-1")
    stations = {}
    for _, row in df.iterrows():
        try:
            x = float(str(row["xrkko08"]).replace(",", "."))
            y = float(str(row["yhkko09"]).replace(",", "."))
        except (ValueError, TypeError):
            continue
        lon, lat = _transformer.transform(x, y)
        dist = haversine_km(center_lat, center_lon, lat, lon)
        if dist <= buffer_km:
            sid = str(row["dbmsnr"])
            stations[sid] = {
                "id": sid,
                "name": str(row.get("mstnam02", sid)),
                "lat": round(lat, 6),
                "lon": round(lon, 6),
                "altitude": int(float(str(row["mpmua04"]).replace(",", "."))) if pd.notna(row.get("mpmua04")) else None,
                "state": str(row.get("gew03", "")),
                "distance_km": round(dist, 1),
            }
    return stations


@st.cache_data(ttl=600)
def fetch_station_metadata_api(resource_id, api_type, mode_meta, buffer_km, center_lat, center_lon):
    """Fetch station metadata from API and filter by buffer distance."""
    url = build_api_url(api_type, mode_meta, resource_id) + "/metadata"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    stations = {}
    for s in data.get("stations", []):
        dist = haversine_km(center_lat, center_lon, s["lat"], s["lon"])
        if dist <= buffer_km:
            sid = str(s["id"])
            stations[sid] = {
                "id": sid,
                "name": s.get("name", sid),
                "lat": s["lat"],
                "lon": s["lon"],
                "altitude": s.get("altitude", None),
                "state": s.get("state", ""),
                "distance_km": round(dist, 1),
            }
    return stations


def get_stations(source_name, buffer_km, center_lat, center_lon):
    """Get station metadata for the selected data source."""
    cfg = DATA_SOURCES[source_name]
    if cfg["api_type"] == "timeseries":
        return load_csv_stations(buffer_km, center_lat, center_lon)
    return fetch_station_metadata_api(
        cfg["resource_id"], cfg["api_type"], cfg["mode_meta"], buffer_km, center_lat, center_lon
    )


# ── Data Fetching ──

@st.cache_data(ttl=300)
def _fetch_station_data(resource_id, mode, station_ids_tuple, start_str, end_str, parameters):
    """Fetch data from a station endpoint."""
    url = build_api_url("station", mode, resource_id)
    params = {
        "parameters": parameters,
        "station_ids": ",".join(station_ids_tuple),
        "start": start_str,
        "end": end_str,
        "output_format": "geojson",
    }
    resp = requests.get(url, params=params, timeout=60)
    resp.raise_for_status()
    return resp.json()


@st.cache_data(ttl=300)
def _fetch_inca_data(lat_lon_tuple, station_ids_tuple, start_str, end_str, parameters):
    """Fetch data from INCA timeseries endpoint using lat/lon coordinates."""
    url = build_api_url("timeseries", "historical", "inca-v1-1h-1km")
    # Use list of tuples to support repeated lat_lon parameter
    param_list = [
        ("parameters", parameters),
        ("start", start_str),
        ("end", end_str),
        ("output_format", "geojson"),
    ]
    for ll in lat_lon_tuple:
        param_list.append(("lat_lon", ll))

    resp = requests.get(url, params=param_list, timeout=120)
    resp.raise_for_status()
    data = resp.json()

    # Inject virtual station IDs into features (order matches lat_lon order)
    for i, feature in enumerate(data.get("features", [])):
        if i < len(station_ids_tuple):
            feature.setdefault("properties", {})["station"] = station_ids_tuple[i]
    return data


def fetch_weather_data(source_name, station_ids, stations_meta, hours=None,
                       parameters=None, start_str=None, end_str=None):
    """Unified data-fetch dispatcher."""
    cfg = DATA_SOURCES[source_name]
    if parameters is None:
        parameters = cfg["request_params"]

    if start_str is None or end_str is None:
        start_str, end_str = _time_window(hours)
    station_tuple = tuple(station_ids)

    if cfg["api_type"] == "timeseries":
        lat_lon_tuple = tuple(
            f"{stations_meta[sid]['lat']},{stations_meta[sid]['lon']}"
            for sid in station_ids
        )
        return _fetch_inca_data(lat_lon_tuple, station_tuple, start_str, end_str, parameters)
    return _fetch_station_data(
        cfg["resource_id"], cfg["mode_data"], station_tuple, start_str, end_str, parameters,
    )


def fetch_antecedent_data(source_name, station_ids, stations_meta, window_hours=None,
                          window_start_dt=None):
    """Fetch 5-day (120 h) antecedent rainfall ending at the start of the main window."""
    cfg = DATA_SOURCES[source_name]
    if window_start_dt is not None:
        window_start = window_start_dt
    else:
        now = datetime.now(timezone.utc)
        window_start = (now - timedelta(hours=window_hours)).replace(
            hour=0, minute=0, second=0, microsecond=0,
        )
    ant_start = (window_start - timedelta(hours=120)).replace(
        hour=0, minute=0, second=0, microsecond=0,
    )
    start_str = ant_start.strftime("%Y-%m-%dT%H:%M")
    end_str = window_start.strftime("%Y-%m-%dT%H:%M")
    station_tuple = tuple(station_ids)
    rain_param = cfg["rain_param"]

    if cfg["api_type"] == "timeseries":
        lat_lon_tuple = tuple(
            f"{stations_meta[sid]['lat']},{stations_meta[sid]['lon']}"
            for sid in station_ids
        )
        return _fetch_inca_data(lat_lon_tuple, station_tuple, start_str, end_str, rain_param)
    return _fetch_station_data(
        cfg["resource_id"], cfg["mode_data"], station_tuple, start_str, end_str, rain_param,
    )


# ── Parsing ──

def parse_geojson_to_df(geojson, stations_meta, param_map, parameter_defaults=None):
    """Parse GeoSphere GeoJSON response into a DataFrame with normalized column names.

    param_map: dict mapping source-specific parameter names to standard names,
               e.g. {"rr": "RR", "tl": "TL", "sh": "SCHNEE"}.
    parameter_defaults: dict mapping *standard* names to default values for nulls.
    """
    if parameter_defaults is None:
        parameter_defaults = {"RR": 0.0}

    timestamps = geojson.get("timestamps", [])
    features = geojson.get("features", [])
    rows = []

    for feature in features:
        props = feature.get("properties", {})
        station_id = str(props.get("station", ""))
        parameters_data = props.get("parameters", {})
        station_name = stations_meta.get(station_id, {}).get("name", station_id)

        param_names = list(parameters_data.keys())
        if not param_names:
            continue

        data_length = len(parameters_data[param_names[0]].get("data", []))

        for i in range(min(data_length, len(timestamps))):
            row = {
                "timestamp": timestamps[i],
                "station_id": station_id,
                "station_name": station_name,
            }
            for pname in param_names:
                std_name = param_map.get(pname, pname)
                raw_val = (
                    parameters_data[pname]["data"][i]
                    if i < len(parameters_data[pname].get("data", []))
                    else None
                )
                default = parameter_defaults.get(std_name, np.nan)
                row[std_name] = raw_val if raw_val is not None else default
            rows.append(row)

    df = pd.DataFrame(rows)
    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    return df


# ── Computation ──

def _compute_energy(intensity, rr, energy_equation):
    """Compute unit energy and interval energy arrays."""
    if energy_equation == "USLE":
        # Wischmeier & Smith (1978), Eq. 1 in Nearing et al. (2017)
        e_unit = np.where(
            intensity > 0,
            np.minimum(0.119 + 0.0873 * np.log10(np.maximum(intensity, 1e-6)), 0.283),
            0.0,
        )
    else:
        # RUSLE2: McGregor et al. (1995), Eq. 7 in Nearing et al. (2017)
        e_unit = 0.29 * (1.0 - 0.72 * np.exp(-0.082 * intensity))
    return e_unit, e_unit * rr


def _compute_i30(rr, interval_minutes, i30_correction=1.0):
    """Compute maximum 30-min intensity from rainfall array."""
    intervals_per_hour = 60.0 / interval_minutes
    if interval_minutes <= 30:
        n = max(1, int(30 / interval_minutes))
        if len(rr) >= n:
            rolling_30 = np.convolve(rr, np.ones(n), mode="valid")
            I30 = float(np.max(rolling_30) * 2.0)  # 30-min sum → mm/h
        else:
            I30 = float(np.sum(rr) * intervals_per_hour) if len(rr) > 0 else 0.0
    else:
        # Hourly or coarser: approximate I30 as max hourly intensity
        intensity = rr * intervals_per_hour
        I30 = float(np.max(intensity)) if len(rr) > 0 else 0.0
    return I30 * i30_correction


def delineate_storms(rr, interval_minutes):
    """Split a rainfall array into individual storm events (USLE methodology).

    A storm break is a period of >= STORM_GAP_HOURS where < STORM_GAP_RAIN_MM falls.
    Returns list of (start_idx, end_idx) tuples.
    """
    n = len(rr)
    if n == 0:
        return []

    gap_intervals = max(1, int(STORM_GAP_HOURS * 60 / interval_minutes))

    if n <= gap_intervals:
        return [(0, n)] if np.sum(rr) > 0 else []

    # Cumulative sum for fast window calculations
    cumsum = np.concatenate([[0.0], np.cumsum(rr)])
    # rolling_sum[i] = sum(rr[i : i + gap_intervals])
    rolling_sum = cumsum[gap_intervals:] - cumsum[:-gap_intervals]

    # Mark intervals that lie inside any dry-gap window
    in_gap = np.zeros(n, dtype=bool)
    for i in range(len(rolling_sum)):
        if rolling_sum[i] < STORM_GAP_RAIN_MM:
            in_gap[i: i + gap_intervals] = True

    # Group consecutive non-gap intervals into storms
    storms = []
    start = None
    for i in range(n):
        if not in_gap[i]:
            if start is None:
                start = i
        else:
            if start is not None:
                storms.append((start, i))
                start = None
    if start is not None:
        storms.append((start, n))

    return storms


def _storm_is_erosive(rr, interval_minutes):
    """Check if a storm meets the minimum erosive threshold (Wischmeier, 1959)."""
    total = float(np.sum(rr))
    if total >= STORM_MIN_RAIN_MM:
        return True
    # Also include if >= 6 mm fell within ~15 min
    if interval_minutes <= 30:
        n_15 = max(1, math.ceil(15 / interval_minutes))
        if len(rr) >= n_15:
            rolling_15 = np.convolve(rr, np.ones(n_15), mode="valid")
            if float(np.max(rolling_15)) >= STORM_INTENSE_15MIN_MM:
                return True
    return False


def compute_station_erosivity(df_station, interval_minutes, energy_equation, i30_correction, lang="en"):
    """Delineate storms and compute per-storm EI30 for one station.

    Returns dict with aggregate results plus a ``storms`` list.
    """
    no_risk_label = get_text("no_risk", lang)
    empty = {
        "total_rainfall": 0.0, "I30": 0.0, "E_total": 0.0,
        "EI30": 0.0, "R_sum": 0.0,
        "alert_level": "green", "alert_label": no_risk_label, "alert_color": "#2ecc71",
        "storms": [], "n_erosive_storms": 0,
    }
    if df_station.empty or "RR" not in df_station.columns:
        return empty

    df = df_station.sort_values("timestamp").reset_index(drop=True)
    rr_all = df["RR"].values.astype(float)
    timestamps = df["timestamp"].values
    intervals_per_hour = 60.0 / interval_minutes
    n = len(rr_all)

    # Delineate storms
    storm_slices = delineate_storms(rr_all, interval_minutes)
    if not storm_slices:
        return empty

    # Is the last storm potentially still ongoing?
    last_end = storm_slices[-1][1] if storm_slices else 0

    storm_results = []
    for s_start, s_end in storm_slices:
        rr = rr_all[s_start:s_end]
        if float(np.sum(rr)) <= 0:
            continue

        is_ongoing = (s_end >= n)  # extends to end of data
        is_erosive = _storm_is_erosive(rr, interval_minutes)

        intensity = rr * intervals_per_hour
        _, e_interval = _compute_energy(intensity, rr, energy_equation)
        E_total = float(np.sum(e_interval))
        I30 = _compute_i30(rr, interval_minutes, i30_correction)
        EI30 = E_total * I30

        level, label, color = get_alert_level(EI30, lang) if is_erosive else ("green", no_risk_label, "#2ecc71")

        storm_results.append({
            "start": pd.Timestamp(timestamps[s_start]),
            "end": pd.Timestamp(timestamps[min(s_end - 1, n - 1)]),
            "duration_hours": round((s_end - s_start) * interval_minutes / 60.0, 1),
            "total_rain": round(float(np.sum(rr)), 2),
            "I30": round(I30, 2),
            "E_total": round(E_total, 4),
            "EI30": round(EI30, 2),
            "is_ongoing": is_ongoing,
            "is_erosive": is_erosive,
            "alert_level": level,
            "alert_label": label,
            "alert_color": color,
        })

    # Aggregate: alert is driven by the worst *erosive* storm
    erosive = [s for s in storm_results if s["is_erosive"]]
    if erosive:
        worst = max(erosive, key=lambda s: s["EI30"])
        alert_level, alert_label, alert_color = worst["alert_level"], worst["alert_label"], worst["alert_color"]
        max_ei30 = worst["EI30"]
    else:
        alert_level, alert_label, alert_color = "green", no_risk_label, "#2ecc71"
        max_ei30 = 0.0

    return {
        "total_rainfall": round(sum(s["total_rain"] for s in storm_results), 2),
        "I30": round(max((s["I30"] for s in storm_results), default=0.0), 2),
        "E_total": round(sum(s["E_total"] for s in storm_results), 4),
        "EI30": round(max_ei30, 2),
        "R_sum": round(sum(s["EI30"] for s in erosive), 2),
        "alert_level": alert_level,
        "alert_label": alert_label,
        "alert_color": alert_color,
        "storms": storm_results,
        "n_erosive_storms": len(erosive),
    }


def compute_all_stations_ei30(df_raw, stations_meta, interval_minutes=10,
                              energy_equation="RUSLE2", i30_correction=1.0, lang="en"):
    """Compute storm-delineated EI30 for every station."""
    results = {}
    for station_id in stations_meta:
        df_s = df_raw[df_raw["station_id"] == station_id].sort_values("timestamp")
        results[station_id] = compute_station_erosivity(
            df_s, interval_minutes, energy_equation, i30_correction, lang,
        )
    return results


def compute_antecedent_totals(geojson, stations_meta, param_map):
    """Compute 5-day antecedent rainfall totals per station."""
    df = parse_geojson_to_df(geojson, stations_meta, param_map, parameter_defaults={"RR": 0.0})
    totals = {}
    if df.empty:
        return totals
    for station_id in stations_meta:
        sdf = df[df["station_id"] == station_id]
        totals[station_id] = round(float(sdf["RR"].sum()), 2) if not sdf.empty else 0.0
    return totals


def compute_snowmelt_risk(df_context, stations_meta):
    """Determine snowmelt risk per station from TL and SCHNEE data."""
    results = {}
    for station_id in stations_meta:
        sdf = df_context[df_context["station_id"] == station_id].sort_values("timestamp")
        risk = False
        latest_temp = None
        latest_snow = None

        if not sdf.empty:
            has_tl = "TL" in sdf.columns
            has_schnee = "SCHNEE" in sdf.columns

            if has_tl:
                tl_valid = sdf["TL"].dropna()
                if not tl_valid.empty:
                    latest_temp = round(float(tl_valid.iloc[-1]), 1)

            if has_schnee:
                schnee_valid = sdf["SCHNEE"].dropna()
                if not schnee_valid.empty:
                    latest_snow = round(float(schnee_valid.iloc[-1]), 1)

            if has_tl and has_schnee:
                mask = (sdf["TL"] > 0) & (sdf["SCHNEE"] > 0)
                risk = bool(mask.any())

        results[station_id] = {
            "snowmelt_risk": risk,
            "latest_temp": latest_temp,
            "latest_snow_depth": latest_snow,
        }
    return results


def create_interpolation_heatmap(stations_meta, ei30_results, grid_resolution=100):
    """
    Create an IDW-like spatial interpolation heatmap of EI30 values.
    Returns a base64 encoded PNG and the bounds for map overlay.
    """
    points = []
    values = []
    for sid, result in ei30_results.items():
        if sid in stations_meta:
            points.append([stations_meta[sid]['lon'], stations_meta[sid]['lat']])
            values.append(result.get('EI30', 0.0))

    if len(points) < 3:
        return None, None  # Need at least 3 points for interpolation

    points = np.array(points)
    values = np.array(values)

    # Define grid bounds based on station locations
    lon_min, lat_min = points.min(axis=0)
    lon_max, lat_max = points.max(axis=0)
    
    # Add a small buffer to the bounds
    lon_buf = (lon_max - lon_min) * 0.1
    lat_buf = (lat_max - lat_min) * 0.1
    bounds = [[lat_min - lat_buf, lon_min - lon_buf], [lat_max + lat_buf, lon_max + lon_buf]]

    # Create a grid: y (lat) descending, x (lon) ascending
    grid_lat, grid_lon = np.mgrid[lat_max + lat_buf:lat_min - lat_buf:complex(0, grid_resolution), 
                                  lon_min - lon_buf:lon_max + lon_buf:complex(0, grid_resolution)]

    # RBF interpolation (x=lon, y=lat)
    rbf = Rbf(points[:, 0], points[:, 1], values, function='linear')
    interp_values = rbf(grid_lon, grid_lat)
    
    # Normalize values for coloring
    vmin, vmax = np.nanmin(interp_values), np.nanmax(interp_values)
    if vmax <= vmin:
        vmax = vmin + 1.0
    # Use np.nan_to_num to handle potential NaNs from interpolation
    normalized_values = np.nan_to_num((interp_values - vmin) / (vmax - vmin))
    
    # Create an image from the interpolated data
    img = Image.new('RGBA', (grid_resolution, grid_resolution))
    pixels = img.load()
    
    # Colormap (e.g., from green to red)
    cmap = [ImageColor.getrgb(c) for c in ['#2ecc71', '#f1c40f', '#e67e22', '#e74c3c']]
    
    for i in range(grid_resolution):  # Corresponds to x, or columns (lon)
        for j in range(grid_resolution):  # Corresponds to y, or rows (lat)
            val = normalized_values[j, i] # index as (row, col) -> (lat, lon)
            
            # Simple linear interpolation between colormap colors
            idx = val * (len(cmap) - 1)
            idx_floor = int(idx)
            idx_ceil = min(idx_floor + 1, len(cmap) - 1)
            
            if idx_floor == idx_ceil:
                color = cmap[idx_floor]
            else:
                interp = idx - idx_floor
                color = tuple(int(c1 * (1 - interp) + c2 * interp) for c1, c2 in zip(cmap[idx_floor], cmap[idx_ceil]))

            # Set opacity based on value (fade out low values)
            opacity = int(255 * max(0, val - 0.1) / 0.9) if val > 0.1 else 0
            pixels[i, j] = color + (opacity,)

    # Convert image to base64 string
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return img_str, bounds



def aggregate_rainfall(df, freq):
    """Aggregate rainfall data to the chosen frequency by summing."""
    if df.empty:
        return df
    return (
        df.groupby([pd.Grouper(key="timestamp", freq=freq), "station_id", "station_name"])
        ["RR"]
        .sum()
        .reset_index()
    )


# ── Map ──

def build_map(stations_meta, center_lat, center_lon, ei30_results=None, heatmap_img=None, heatmap_bounds=None, buffer_km=25, lang="en"):
    """Build a folium map with CircleMarkers colored/sized by alert level."""
    if not stations_meta:
        return folium.Map(location=[47.5, 13.5], zoom_start=7)

    m = folium.Map(location=[center_lat, center_lon], zoom_start=9)

    if heatmap_img and heatmap_bounds:
        img_overlay = folium.raster_layers.ImageOverlay(
            image=f"data:image/png;base64,{heatmap_img}",
            bounds=heatmap_bounds,
            opacity=0.6,
            name="EI30 Heatmap",
        )
        img_overlay.add_to(m)
        folium.LayerControl().add_to(m)

    # Draw buffer circles
    drawn_radii = []
    # Draw the main, user-selected buffer first
    folium.Circle(
        location=[center_lat, center_lon],
        radius=buffer_km * 1000,
        color="#e74c3c", fill=True, fill_opacity=0.05, weight=2, dash_array="5",
        tooltip=get_text("buffer_selected", lang, km=buffer_km),
    ).add_to(m)
    drawn_radii.append(buffer_km)

    # Draw other reference circles if they are different
    for radius_km_ref in [50, 25, 10]:
        if radius_km_ref not in drawn_radii:
            folium.Circle(
                location=[center_lat, center_lon],
                radius=radius_km_ref * 1000,
                color="#3388ff", fill=True, fill_opacity=0.05, weight=1, dash_array="5",
                tooltip=get_text("buffer_ref", lang, km=radius_km_ref),
            ).add_to(m)

    folium.Marker(
        location=[center_lat, center_lon],
        icon=folium.Icon(color="blue", icon="crosshairs", prefix="fa"),
        tooltip="Kaindorf",
    ).add_to(m)

    max_rain = 1.0
    if ei30_results:
        max_rain = max((r["total_rainfall"] for r in ei30_results.values()), default=1.0)
    if max_rain <= 0:
        max_rain = 1.0

    alt_label = get_text("altitude", lang)
    dist_label = get_text("distance", lang)
    rain_label = get_text("total_rainfall", lang)
    na_text = get_text("na", lang)

    for sid, s in stations_meta.items():
        alt_text = f"{s['altitude']} m" if s.get("altitude") is not None else na_text
        dist_text = f"{s['distance_km']} km" if "distance_km" in s else ""

        if ei30_results and sid in ei30_results:
            res = ei30_results[sid]
            color = res["alert_color"]
            radius = 5 + 15 * min(res["total_rainfall"] / max_rain, 1.0)
            popup_text = (
                f"<b>{s['name']}</b><br>"
                f"{alt_label}: {alt_text}<br>"
                f"{dist_label}: {dist_text}<br>"
                f"{rain_label}: {res['total_rainfall']} mm<br>"
                f"I30: {res['I30']} mm/h<br>"
                f"EI30: {res['EI30']} MJ\u00b7mm\u00b7ha\u207b\u00b9\u00b7h\u207b\u00b9<br>"
                f"{get_text('col_alert', lang)}: {res['alert_label']}"
            )
        else:
            color = "#2ecc71"
            radius = 5
            popup_text = (
                f"<b>{s['name']}</b><br>ID: {s['id']}<br>"
                f"{alt_label}: {alt_text}<br>{dist_label}: {dist_text}"
            )

        folium.CircleMarker(
            location=[s["lat"], s["lon"]],
            radius=radius, color=color, fill=True, fill_color=color, fill_opacity=0.7,
            popup=folium.Popup(popup_text, max_width=300),
            tooltip=s["name"],
        ).add_to(m)

    return m


# ── Main ──

def main():
    # Initialize language in session state (must be before set_page_config)
    if "lang" not in st.session_state:
        st.session_state.lang = "de"  # German as default
    lang = st.session_state.lang

    st.set_page_config(page_title=get_text("page_title", lang), layout="wide")

    st.sidebar.image(os.path.join(PROJECT_ROOT, "assets", "BAW Research.png"))

    # Language selector at top of sidebar
    lang_options = {"Deutsch": "de", "English": "en"}
    selected_lang_name = st.sidebar.selectbox(
        get_text("language", lang),
        options=list(lang_options.keys()),
        index=0 if lang == "de" else 1,
    )
    new_lang = lang_options[selected_lang_name]
    if new_lang != st.session_state.lang:
        st.session_state.lang = new_lang
        st.rerun()
    lang = st.session_state.lang

    st.title(get_text("main_title", lang))

    # ── Sidebar controls ──
    st.sidebar.header(get_text("control_panel", lang))
    # Data source
    source_name = st.sidebar.selectbox(
        get_text("data_source", lang),
        options=list(DATA_SOURCES.keys()),
        index=0,
    )
    source_cfg = DATA_SOURCES[source_name]
    interval_minutes = source_cfg["interval_minutes"]

    # Coordinate inputs
    st.sidebar.markdown(f"##### {get_text('location', lang)}",
                        help=get_text("location_help", lang))
    st.sidebar.write(get_text("select_area", lang))

    # Define default coordinates using existing global constants
    default_coords = [47.1965936, 15.8583828]

    # Set defaults in session state
    if "selected_coords" not in st.session_state:
        st.session_state.selected_coords = default_coords
    if "lat_input_val" not in st.session_state:
        st.session_state.lat_input_val = str(st.session_state.selected_coords[0])
    if "lon_input_val" not in st.session_state:
        st.session_state.lon_input_val = str(st.session_state.selected_coords[1])

    lat_input = st.sidebar.text_input(get_text("latitude", lang), value=st.session_state.lat_input_val, placeholder="e.g., 47.2154")
    lon_input = st.sidebar.text_input(get_text("longitude", lang), value=st.session_state.lon_input_val, placeholder="e.g., 15.9018")

    # Validate and update coordinates only if both inputs are valid floats or integers
    try:
        lat = float(lat_input.strip())
        lon = float(lon_input.strip())
        is_valid_number = True
    except ValueError:
        is_valid_number = False

    if is_valid_number:
        if -90 <= lat <= 90 and -180 <= lon <= 180:
            if [lat, lon] != st.session_state.selected_coords:
                st.session_state.selected_coords = [lat, lon]
                st.session_state.lat_input_val = str(lat)
                st.session_state.lon_input_val = str(lon)
                st.sidebar.success(f"{get_text('map_centered_at', lang)} ({lat}, {lon})")
        else:
            st.sidebar.error(get_text("lat_range_error", lang))
    elif lat_input or lon_input:
        st.sidebar.error(get_text("invalid_coords_error", lang))

    # Get Data Button
    if st.sidebar.button(get_text("refresh_coords", lang)):
        st.session_state.get_data_clicked = True

    buffer_km = st.sidebar.slider(f"##### {get_text('buffer_radius', lang)}", 5, 100, 25)

    # Time range
    st.sidebar.markdown(
        f"##### {get_text('custom_date_range', lang)}",
        help=get_text("date_range_help", lang),
    )
    today = datetime.now(timezone.utc)
    default_start = today - timedelta(days=3)

    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input(get_text("start_date", lang), value=default_start)
    with col2:
        end_date = st.date_input(get_text("end_date", lang), value=today, max_value=today.date())

    # Validate date range
    date_range_valid = True
    date_range_days = (end_date - start_date).days

    if start_date >= end_date:
        st.sidebar.error(get_text("start_before_end_error", lang))
        date_range_valid = False
    elif date_range_days > 45:
        st.sidebar.error(get_text("date_range_exceeded", lang, days=date_range_days))
        date_range_valid = False
    


    # Initialize session state for data fetching
    if "data_loaded" not in st.session_state:
        st.session_state.data_loaded = False
    if "fetched_start_date" not in st.session_state:
        st.session_state.fetched_start_date = None
    if "fetched_end_date" not in st.session_state:
        st.session_state.fetched_end_date = None

    # On first visit, auto-load with default 72h range
    is_first_load = not st.session_state.data_loaded
    if is_first_load and date_range_valid:
        st.session_state.data_loaded = True
        st.session_state.fetched_start_date = start_date
        st.session_state.fetched_end_date = end_date

    # Check if user changed dates since last fetch
    dates_changed = (
        st.session_state.fetched_start_date != start_date or
        st.session_state.fetched_end_date != end_date
    )

    # Fetch Data button
    fetch_button_disabled = not date_range_valid
    if st.sidebar.button(get_text("fetch_data", lang), disabled=fetch_button_disabled, type="primary"):
        st.session_state.data_loaded = True
        st.session_state.fetched_start_date = start_date
        st.session_state.fetched_end_date = end_date
        dates_changed = False  # Just clicked, so we're fetching current selection

    # Use the fetched dates for data retrieval (not the current UI selection if changed)
    fetch_start_date = st.session_state.fetched_start_date if st.session_state.fetched_start_date else start_date
    fetch_end_date = st.session_state.fetched_end_date if st.session_state.fetched_end_date else end_date

    # Convert to datetime objects for fetching
    start_dt_utc = datetime.combine(fetch_start_date, datetime.min.time()).replace(tzinfo=timezone.utc)
    end_dt_utc = datetime.combine(fetch_end_date, datetime.max.time()).replace(tzinfo=timezone.utc)

    # Ensure end time is not in the future
    if end_dt_utc > today:
        end_dt_utc = today

    start_str = start_dt_utc.strftime("%Y-%m-%dT%H:%M")
    end_str = end_dt_utc.strftime("%Y-%m-%dT%H:%M")

    # Aggregation (options depend on data resolution)
    # Translate aggregation option labels
    agg_options_base = AGGREGATION_OPTIONS_HOURLY if interval_minutes >= 60 else AGGREGATION_OPTIONS_10MIN
    agg_label_map = {
        "10 min": get_text("10_min", lang),
        "30 min": get_text("30_min", lang),
        "1 hour": get_text("1_hour", lang),
        "3 hours": get_text("3_hours", lang),
        "6 hours": get_text("6_hours", lang),
        "24 hours": get_text("24_hours", lang),
    }
    agg_options_translated = {agg_label_map.get(k, k): v for k, v in agg_options_base.items()}
    agg_label = st.sidebar.radio(
        get_text("aggregation_interval", lang),
        options=list(agg_options_translated.keys()),
        index=0,
    )
    agg_freq = agg_options_translated[agg_label]

    # Energy equation for EI30
    energy_equation = st.sidebar.radio(
        get_text("energy_equation", lang),
        options=["RUSLE2", "USLE"],
        index=0,
        help=get_text("energy_equation_help", lang),
    )

    show_heatmap = st.sidebar.checkbox(get_text("show_heatmap", lang), value=False)

    # ── Station metadata ──
    with st.spinner(get_text("loading_metadata", lang)):
        try:
            stations_meta = get_stations(source_name, buffer_km, st.session_state.selected_coords[0], st.session_state.selected_coords[1])
        except Exception as e:
            st.error(f"{get_text('failed_load_metadata', lang)} {e}")
            return

    if not stations_meta:
        st.warning(get_text("no_stations_found", lang))
        return

    # Station selection
    name_to_id = {s["name"]: sid for sid, s in stations_meta.items()}
    sorted_names = sorted(name_to_id.keys())
    selected_names = st.sidebar.multiselect(get_text("stations", lang), options=sorted_names, default=sorted_names)
    selected_station_ids = [name_to_id[n] for n in selected_names]

    if not selected_station_ids:
        st.info(get_text("select_station", lang))
        return

    # Build selected_meta early for map display
    selected_meta = {
        sid: stations_meta[sid] for sid in selected_station_ids if sid in stations_meta
    }

    # Check if data should be fetched
    if not st.session_state.data_loaded:
        st.info(get_text("adjust_date_range", lang))
        # Still show the map with station locations
        st.subheader(get_text("station_map", lang))
        station_map = build_map(selected_meta, st.session_state.selected_coords[0], st.session_state.selected_coords[1], None, None, None, buffer_km, lang)
        folium_static(station_map, width=900, height=450)
        return

    # Warn if dates changed since last fetch
    if dates_changed:
        st.warning(
            get_text("date_changed_warning", lang,
                     start=st.session_state.fetched_start_date,
                     end=st.session_state.fetched_end_date)
        )

    st.caption(
        get_text("precipitation_caption", lang,
                 start=fetch_start_date.strftime('%Y-%m-%d'),
                 end=fetch_end_date.strftime('%Y-%m-%d'),
                 desc=source_cfg['description'])
    )

    if source_cfg["api_type"] == "timeseries":
        st.info(get_text("inca_info", lang))

    st.sidebar.divider()
    st.sidebar.subheader(get_text("contact", lang))
    st.sidebar.markdown("""
    **BAW Research**

    Pollnbergstraße 1
    3252 Petzenkirchen
    Telefon: `+43 7416 52108 859`
    E-Mail: [research@baw.at](mailto:research@baw.at)
    """)

    # ── Fetch main data ──
    with st.spinner(get_text("fetching_data", lang)):
        try:
            geojson = fetch_weather_data(source_name, selected_station_ids, selected_meta, start_str=start_str, end_str=end_str)
        except Exception as e:
            st.error(f"{get_text('failed_fetch_data', lang)} {e}")
            return

    param_map = source_cfg["param_map"]
    df_raw = parse_geojson_to_df(
        geojson, selected_meta, param_map,
        parameter_defaults={"RR": 0.0, "TL": np.nan, "SCHNEE": np.nan},
    )

    if df_raw.empty:
        st.warning(get_text("no_data_returned", lang))
        return

    # ── EI30 (storm-delineated, per USLE methodology) ──
    i30_correction = source_cfg["i30_correction"]
    ei30_results = compute_all_stations_ei30(
        df_raw, selected_meta, interval_minutes, energy_equation, i30_correction, lang,
    )

    # ── Antecedent rainfall ──
    antecedent_totals = {}
    try:
        ant_geojson = fetch_antecedent_data(
            source_name, selected_station_ids, selected_meta, window_start_dt=start_dt_utc,
        )
        antecedent_totals = compute_antecedent_totals(ant_geojson, selected_meta, param_map)
    except Exception:
        pass  # non-critical

    # ── Snowmelt risk ──
    snowmelt_results = compute_snowmelt_risk(df_raw, selected_meta)

    # ── Field Survey Recommendation ──
    now_utc = datetime.now(timezone.utc)
    survey_needed = False
    ongoing_events = []
    recent_events = []  # erosive storms ended within last 24 h

    for sid, res in ei30_results.items():
        name = selected_meta.get(sid, {}).get("name", sid)
        for storm in res.get("storms", []):
            if not storm["is_erosive"]:
                continue
            if storm["is_ongoing"]:
                ongoing_events.append((name, sid, storm))
                survey_needed = True
            else:
                hours_ago = (now_utc - storm["end"].to_pydatetime().replace(tzinfo=timezone.utc)).total_seconds() / 3600
                if hours_ago <= 24:
                    recent_events.append((name, sid, storm, round(hours_ago, 1)))
                    survey_needed = True

    st.subheader(get_text("field_survey_recommendation", lang))
    if ongoing_events:
        for name, sid, storm in ongoing_events:
            st.error(
                get_text("erosive_event_in_progress", lang,
                         name=name, label=storm['alert_label'], ei30=storm['EI30'],
                         rain=storm['total_rain'], i30=storm['I30'])
            )
    if recent_events:
        for name, sid, storm, hours_ago in sorted(recent_events, key=lambda x: x[2]["EI30"], reverse=True):
            st.warning(
                get_text("field_survey_recommended", lang,
                         name=name, label=storm['alert_label'], ei30=storm['EI30'],
                         hours=f"{hours_ago:.0f}", time=storm['end'].strftime('%Y-%m-%d %H:%M'),
                         rain=storm['total_rain'], duration=storm['duration_hours'], i30=storm['I30'])
            )
    if not survey_needed:
        # Check for any alert-level stations (non-green)
        alert_stations = {
            sid: res for sid, res in ei30_results.items() if res["alert_level"] != "green"
        }
        if alert_stations:
            for sid, res in sorted(alert_stations.items(), key=lambda x: x[1]["EI30"], reverse=True):
                name = selected_meta.get(sid, {}).get("name", sid)
                st.info(
                    get_text("alert_station_info", lang,
                             name=name, label=res['alert_label'], ei30=res['EI30'])
                )
        else:
            st.success(get_text("no_erosive_events", lang))

    # ── Storm Events Detail ──
    yes_text = get_text("yes", lang)
    no_text = get_text("no", lang)
    all_storms = []
    for sid, res in ei30_results.items():
        name = selected_meta.get(sid, {}).get("name", sid)
        for storm in res.get("storms", []):
            all_storms.append({
                get_text("col_station", lang): name,
                get_text("col_start", lang): storm["start"].strftime("%Y-%m-%d %H:%M"),
                get_text("col_end", lang): storm["end"].strftime("%Y-%m-%d %H:%M") + (" *" if storm["is_ongoing"] else ""),
                get_text("col_duration", lang): storm["duration_hours"],
                get_text("col_rain", lang): storm["total_rain"],
                get_text("col_i30", lang): storm["I30"],
                get_text("col_ei30", lang): storm["EI30"],
                get_text("col_erosive", lang): yes_text if storm["is_erosive"] else no_text,
                get_text("col_alert", lang): storm["alert_label"],
            })

    if all_storms:
        with st.expander(get_text("storm_events", lang, count=len(all_storms)), expanded=bool(survey_needed)):
            st.caption(
                get_text("storm_delineation_caption", lang,
                         gap=STORM_GAP_HOURS, rain=STORM_GAP_RAIN_MM,
                         min_rain=STORM_MIN_RAIN_MM, intense=STORM_INTENSE_15MIN_MM)
            )
            storm_df = pd.DataFrame(all_storms)
            storm_df = storm_df.sort_values(get_text("col_ei30", lang), ascending=False)
            st.dataframe(storm_df, use_container_width=True, hide_index=True)

    # ── Interpolation Heatmap ──
    heatmap_img, heatmap_bounds = None, None
    if show_heatmap:
        with st.spinner(get_text("generating_heatmap", lang)):
            if len(selected_station_ids) < 3:
                st.warning(get_text("heatmap_min_stations", lang))
            else:
                heatmap_img, heatmap_bounds = create_interpolation_heatmap(selected_meta, ei30_results)
                if not heatmap_img:
                    st.warning(get_text("heatmap_error", lang))

    # ── Map ──
    st.subheader(get_text("station_map", lang))
    station_map = build_map(selected_meta, st.session_state.selected_coords[0], st.session_state.selected_coords[1], ei30_results, heatmap_img, heatmap_bounds, buffer_km, lang)
    folium_static(station_map, width=900, height=450)

    # ── Aggregate for display ──
    df_agg = aggregate_rainfall(df_raw, agg_freq)

    # ── Time-series chart ──
    st.subheader(get_text("precipitation_totals", lang, interval=agg_label))
    fig = px.bar(
        df_agg, x="timestamp", y="RR", color="station_name", barmode="group",
        labels={"RR": get_text("rainfall_label", lang, interval=agg_label),
                "timestamp": get_text("time_label", lang)},
    )
    fig.update_layout(legend_title_text=get_text("col_station", lang), hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

    # ── Cumulative chart ──
    st.subheader(get_text("cumulative_precipitation", lang))
    df_agg_sorted = df_agg.sort_values("timestamp")
    df_agg_sorted["cumulative"] = df_agg_sorted.groupby("station_name")["RR"].cumsum()
    fig_cum = px.line(
        df_agg_sorted, x="timestamp", y="cumulative", color="station_name",
        labels={"cumulative": get_text("cumulative_label", lang),
                "timestamp": get_text("time_label", lang)},
    )
    fig_cum.update_layout(legend_title_text=get_text("col_station", lang), hovermode="x unified")
    st.plotly_chart(fig_cum, use_container_width=True)

    # ── Hyetograph (Intensity Chart) ──
    st.subheader(get_text("rainfall_intensity", lang))
    # Use a copy to avoid Streamlit's "modified" warning
    df_intensity = df_raw.copy()
    df_intensity["intensity_mmh"] = df_intensity["RR"] * (60.0 / interval_minutes)
    fig_hyeto = px.bar(
        df_intensity, x="timestamp", y="intensity_mmh", color="station_name", barmode="group",
        labels={"intensity_mmh": get_text("intensity_label", lang),
                "timestamp": get_text("time_label", lang)},
    )
    fig_hyeto.update_layout(legend_title_text=get_text("col_station", lang), hovermode="x unified")
    st.plotly_chart(fig_hyeto, use_container_width=True)

    # ── Summary Table ──
    st.subheader(get_text("summary_statistics", lang))
    na_text = get_text("na", lang)
    summary_rows = []
    for sid in selected_station_ids:
        if sid not in selected_meta:
            continue
        name = selected_meta[sid]["name"]
        res = ei30_results.get(sid, {})
        ant = antecedent_totals.get(sid, 0.0)
        amc_class, _ = classify_amc(ant, lang)
        snow = snowmelt_results.get(sid, {})
        summary_rows.append({
            get_text("col_station", lang): name,
            get_text("col_storms", lang): res.get("n_erosive_storms", 0),
            get_text("col_total", lang): res.get("total_rainfall", 0.0),
            get_text("col_i30", lang): res.get("I30", 0.0),
            get_text("col_max_ei30", lang): res.get("EI30", 0.0),
            get_text("col_r_sum", lang): res.get("R_sum", 0.0),
            get_text("col_alert", lang): res.get("alert_label", get_text("no_risk", lang)),
            get_text("col_antecedent", lang): ant,
            get_text("col_amc_class", lang): amc_class,
            get_text("col_snowmelt_risk", lang): yes_text if snow.get("snowmelt_risk") else no_text,
            get_text("col_latest_temp", lang): snow.get("latest_temp") if snow.get("latest_temp") is not None else na_text,
            get_text("col_snow_depth", lang): snow.get("latest_snow_depth") if snow.get("latest_snow_depth") is not None else na_text,
        })
    summary_df = pd.DataFrame(summary_rows)
    if not summary_df.empty:
        summary_df = summary_df.sort_values(get_text("col_max_ei30", lang), ascending=False)
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

    # ── Context Data Section ──
    st.subheader(get_text("context_data", lang))
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**{get_text('antecedent_rainfall', lang)}**")
        ant_rows = []
        for sid in selected_station_ids:
            if sid not in selected_meta:
                continue
            ant = antecedent_totals.get(sid, 0.0)
            amc_class, amc_desc = classify_amc(ant, lang)
            ant_rows.append({
                get_text("col_station", lang): selected_meta[sid]["name"],
                get_text("col_5day_antecedent", lang): ant,
                get_text("col_amc_class", lang): amc_class,
                get_text("col_description", lang): amc_desc,
            })
        ant_df = pd.DataFrame(ant_rows)
        if not ant_df.empty:
            ant_df = ant_df.sort_values(get_text("col_5day_antecedent", lang), ascending=False)
        st.dataframe(ant_df, use_container_width=True, hide_index=True)

    with col2:
        st.markdown(f"**{get_text('snowmelt_risk_assessment', lang)}**")
        snow_rows = []
        for sid in selected_station_ids:
            if sid not in selected_meta:
                continue
            snow = snowmelt_results.get(sid, {})
            temp_str = f"{snow['latest_temp']} °C" if snow.get("latest_temp") is not None else na_text
            snow_str = f"{snow['latest_snow_depth']} cm" if snow.get("latest_snow_depth") is not None else na_text
            snow_rows.append({
                get_text("col_station", lang): selected_meta[sid]["name"],
                get_text("col_snowmelt_risk", lang): yes_text if snow.get("snowmelt_risk") else no_text,
                get_text("col_latest_temp_short", lang): temp_str,
                get_text("col_snow_depth_short", lang): snow_str,
            })
        snow_df = pd.DataFrame(snow_rows)
        if not snow_df.empty:
            snow_df = snow_df.sort_values(get_text("col_snowmelt_risk", lang), ascending=False)
        st.dataframe(snow_df, use_container_width=True, hide_index=True)

    # ── Raw data (expandable) ──
    with st.expander(get_text("raw_aggregated_data", lang)):
        st.dataframe(
            df_agg.sort_values(["station_name", "timestamp"]),
            use_container_width=True, hide_index=True,
        )

    # ── References ──
    st.divider()
    st.subheader(get_text("references", lang))
    st.markdown(
        f"**{get_text('energy_equation_label', lang)}** {energy_equation} | "
        f"**{get_text('storm_delineation_label', lang)}** {STORM_GAP_HOURS}{get_text('gap_label', lang)} {STORM_GAP_RAIN_MM} mm | "
        f"**{get_text('erosive_threshold_label', lang)}** {STORM_MIN_RAIN_MM} mm\n\n"
        "- Nearing, M.A., Yin, S., Borrelli, P., Polyakov, V.O. (2017). "
        "Rainfall erosivity: An historical review. "
        "*Catena*, 157, 357–362. "
        "[doi:10.1016/j.catena.2017.06.004]"
        "(https://doi.org/10.1016/j.catena.2017.06.004)\n"
        "- Wischmeier, W.H., Smith, D.D. (1978). "
        "Predicting rainfall erosion losses. "
        "*USDA Agriculture Handbook* No. 537. "
        "(Storm delineation: 6h gap with < 1.27 mm; "
        "erosive threshold: 12.7 mm or 6 mm in 15 min)\n"
        "- McGregor, K.C., Bingner, R.L., Bowie, A.J., Foster, G.R. (1995). "
        "Erosivity index values for northern Mississippi. "
        "*Trans. ASAE*, 38(4), 1039–1047.\n"
        "- Brown, L.C., Foster, G.R. (1987). "
        "Storm erosivity using idealized intensity distributions. "
        "*Trans. ASAE*, 30(2), 379–386.\n"
        "- Wischmeier, W.H. (1959). "
        "A rainfall erosion index for a universal soil loss equation. "
        "*Soil Sci. Soc. Am. Proc.*, 23, 322–326.\n"
    )


if __name__ == "__main__":
    main()