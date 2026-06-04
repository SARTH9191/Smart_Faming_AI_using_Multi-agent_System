"""
geo_verifier.py — EXIF extraction + GPS geo-verification
=========================================================
Standalone module with no FastAPI dependency.

Public API:
    extract_exif(image_bytes: bytes) -> dict
    haversine(lat1, lon1, lat2, lon2) -> float   # metres
    verify_geo(image_bytes, farm_lat, farm_lon, allowed_radius_m) -> dict
"""

import math
import io
from typing import Optional, Dict, Any

# ── EXIF helpers ────────────────────────────────────────────────────────────

def _to_float(val) -> Optional[float]:
    """Safely convert an EXIF rational value to float.
    Handles: (numerator, denominator) tuples, IFDRational objects, plain ints/floats.
    """
    try:
        if isinstance(val, tuple) and len(val) == 2:
            return val[0] / val[1] if val[1] != 0 else None
        # IFDRational and plain numerics both support float()
        return float(val)
    except Exception:
        return None


def _dms_to_decimal(dms_values, ref: str) -> Optional[float]:
    """
    Convert DMS sequence + ref ('N'/'S'/'E'/'W') → decimal degrees.
    Handles tuples, IFDRational objects, and bare floats (single-element = already decimal).
    Returns None on any error.
    """
    try:
        if not dms_values:
            return None

        # If only one element, it may already be a decimal degree value
        if len(dms_values) == 1:
            decimal = _to_float(dms_values[0])
        else:
            deg = _to_float(dms_values[0])
            mins = _to_float(dms_values[1]) if len(dms_values) > 1 else 0.0
            secs = _to_float(dms_values[2]) if len(dms_values) > 2 else 0.0
            if deg is None or mins is None or secs is None:
                return None
            decimal = deg + mins / 60.0 + secs / 3600.0

        if decimal is None:
            return None
        if ref in ("S", "W"):
            decimal = -decimal
        return decimal
    except Exception:
        return None




def extract_exif(image_bytes: bytes) -> Dict[str, Any]:
    """
    Extract GPS + datetime + device info from JPEG EXIF.

    Returns:
        {
          "gps_latitude":  float | None,
          "gps_longitude": float | None,
          "datetime":      str   | None,
          "make":          str   | None,
          "model":         str   | None,
          "has_gps":       bool,
          "raw_tags":      dict,   # minimal subset
          "error":         str | None
        }
    """
    result: Dict[str, Any] = {
        "gps_latitude": None,
        "gps_longitude": None,
        "datetime": None,
        "make": None,
        "model": None,
        "has_gps": False,
        "raw_tags": {},
        "error": None,
    }

    try:
        from PIL import Image
        from PIL.ExifTags import TAGS, GPSTAGS

        img = Image.open(io.BytesIO(image_bytes))
        raw_exif = img._getexif()
        if not raw_exif:
            result["error"] = "No EXIF data found in image"
            return result

        # Decode all EXIF tags
        exif_decoded: Dict[str, Any] = {}
        for tag_id, value in raw_exif.items():
            tag = TAGS.get(tag_id, tag_id)
            exif_decoded[tag] = value

        # Basic device/time info
        result["make"] = str(exif_decoded.get("Make", "")).strip() or None
        result["model"] = str(exif_decoded.get("Model", "")).strip() or None
        result["datetime"] = str(exif_decoded.get("DateTimeOriginal", exif_decoded.get("DateTime", ""))).strip() or None

        # GPS parsing
        gps_info_raw = exif_decoded.get("GPSInfo")
        if gps_info_raw:
            gps_info: Dict[str, Any] = {}
            for key, val in gps_info_raw.items():
                sub_tag = GPSTAGS.get(key, key)
                gps_info[sub_tag] = val

            result["raw_tags"] = {k: str(v) for k, v in gps_info.items()}

            lat_dms = gps_info.get("GPSLatitude")
            lat_ref = gps_info.get("GPSLatitudeRef", "N")
            lon_dms = gps_info.get("GPSLongitude")
            lon_ref = gps_info.get("GPSLongitudeRef", "E")

            if lat_dms and lon_dms:
                lat = _dms_to_decimal(lat_dms, lat_ref)
                lon = _dms_to_decimal(lon_dms, lon_ref)
                if lat is not None and lon is not None:
                    result["gps_latitude"] = round(lat, 7)
                    result["gps_longitude"] = round(lon, 7)
                    result["has_gps"] = True
                else:
                    result["error"] = "EXIF GPS DMS values could not be parsed"
            else:
                result["error"] = "EXIF GPS tags present but lat/lon missing"
        else:
            result["error"] = "No GPSInfo tag found in EXIF"

    except ImportError:
        result["error"] = "Pillow library not installed — cannot parse EXIF"
    except Exception as exc:
        result["error"] = f"EXIF parsing error: {str(exc)}"

    return result


# ── Haversine formula ───────────────────────────────────────────────────────

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points in **metres**.
    """
    R = 6_371_000  # Earth radius in metres
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ── Main verification entry-point ────────────────────────────────────────────

def verify_geo(
    image_bytes: bytes,
    farm_lat: Optional[float],
    farm_lon: Optional[float],
    allowed_radius_m: float = 600.0,
) -> Dict[str, Any]:
    """
    Full geo verification pipeline.

    Returns:
        {
          "passed":              bool,
          "verification_level":  str,   # L1_IMAGE_UPLOADED | L2_GEO_VERIFIED | verification_failed
          "reason":              str,
          "proof_latitude":      float | None,
          "proof_longitude":     float | None,
          "distance_meters":     float | None,
          "allowed_radius_m":    float,
          "exif":                dict,   # full exif result
        }
    """
    exif = extract_exif(image_bytes)

    # ── Case 1: no GPS in image ──────────────────────────────────────────────
    if not exif["has_gps"]:
        return {
            "passed": False,
            "verification_level": "L1_IMAGE_UPLOADED",
            "reason": exif.get("error") or "EXIF GPS data missing from image",
            "proof_latitude": None,
            "proof_longitude": None,
            "distance_meters": None,
            "allowed_radius_m": allowed_radius_m,
            "exif": exif,
        }

    proof_lat = exif["gps_latitude"]
    proof_lon = exif["gps_longitude"]

    # ── Case 2: farm profile GPS not configured ──────────────────────────────
    if farm_lat is None or farm_lon is None:
        return {
            "passed": False,
            "verification_level": "L1_IMAGE_UPLOADED",
            "reason": "Farm GPS coordinates not configured — admin must set farm profile",
            "proof_latitude": proof_lat,
            "proof_longitude": proof_lon,
            "distance_meters": None,
            "allowed_radius_m": allowed_radius_m,
            "exif": exif,
        }

    # ── Case 3: compute distance ─────────────────────────────────────────────
    distance_m = haversine(proof_lat, proof_lon, farm_lat, farm_lon)

    if distance_m <= allowed_radius_m:
        return {
            "passed": True,
            "verification_level": "L2_GEO_VERIFIED",
            "reason": f"GPS matched: {distance_m:.1f}m from farm center (radius {allowed_radius_m:.0f}m)",
            "proof_latitude": proof_lat,
            "proof_longitude": proof_lon,
            "distance_meters": round(distance_m, 2),
            "allowed_radius_m": allowed_radius_m,
            "exif": exif,
        }
    else:
        return {
            "passed": False,
            "verification_level": "verification_failed",
            "reason": (
                f"GPS out of radius: proof is {distance_m:.1f}m from farm center "
                f"(allowed radius {allowed_radius_m:.0f}m)"
            ),
            "proof_latitude": proof_lat,
            "proof_longitude": proof_lon,
            "distance_meters": round(distance_m, 2),
            "allowed_radius_m": allowed_radius_m,
            "exif": exif,
        }
