# disease_info.py
# Small knowledge base for crop diseases used by Krishi Mitra backend.
# Keys are "simple slugs" (lowercase, underscores) like "tomato_late_blight".
# Each entry contains:
#  - friendly_name: human-friendly disease name
#  - treatment: general treatment suggestions (non-prescriptive)
#  - prevention: general prevention & cultural practices
#  - example_classes: optional list of PlantVillage-style class names

from typing import Dict, Any

# Core knowledge map
_DISEASE_DB: Dict[str, Dict[str, Any]] = {
    # Tomato - Late blight
    "tomato_late_blight": {
        "friendly_name": "Tomato — Late Blight",
        "treatment": (
            "Remove and safely destroy heavily infected plants and plant parts. "
            "Improve air circulation by pruning dense foliage. Use copper-based "
            "organic fungicides or registered fungicides when disease pressure is high; "
            "follow product label instructions and local extension guidance."
        ),
        "prevention": (
            "Plant resistant varieties where available, avoid overhead irrigation, "
            "rotate crops (avoid planting solanaceous crops on the same site year-to-year), "
            "and ensure adequate spacing for airflow. Monitor regularly and remove volunteer plants."
        ),
        "example_classes": ["Tomato___Late_blight", "Tomato___Healthy"]
    },

    # Tomato - Healthy
    "tomato_healthy": {
        "friendly_name": "Tomato — Healthy",
        "treatment": "No treatment required. Maintain good cultural practices and monitor for pests/diseases.",
        "prevention": "Maintain balanced fertilization, regular monitoring and sanitation to keep plants healthy.",
        "example_classes": ["Tomato___Healthy"]
    },

    # Potato - Early blight
    "potato_early_blight": {
        "friendly_name": "Potato — Early Blight",
        "treatment": (
            "Remove affected foliage and tubers for disposal. Apply approved fungicides when necessary "
            "and follow local recommendations and label directions."
        ),
        "prevention": (
            "Practice crop rotation, plant certified seed, avoid excess nitrogen fertilization, "
            "and improve drainage and airflow."
        ),
        "example_classes": ["Potato___Early_blight", "Potato___Healthy"]
    },

    # Potato - Healthy
    "potato_healthy": {
        "friendly_name": "Potato — Healthy",
        "treatment": "No treatment needed. Continue routine crop management and scouting.",
        "prevention": "Use certified seed, rotate crops, and follow good irrigation and nutrient management."
    },

    # Corn - Common rust
    "corn_common_rust": {
        "friendly_name": "Maize/Corn — Common Rust",
        "treatment": (
            "Rust is often managed by planting resistant hybrids and timely fungicide applications "
            "when thresholds are reached. Consult local extension services for thresholds and products."
        ),
        "prevention": (
            "Use resistant varieties, rotate crops where possible, and avoid excessive plant density. "
            "Monitor fields and manage volunteer host plants."
        ),
        "example_classes": ["Corn___Common_rust", "Corn___Healthy"]
    },

    # Corn - Healthy
    "corn_healthy": {
        "friendly_name": "Corn — Healthy",
        "treatment": "No treatment required.",
        "prevention": "Maintain best agronomic practices and monitor for pests and diseases."
    }
}

# Generic fallback entry for unknown slugs
_DEFAULT_ENTRY = {
    "friendly_name": "Unknown / Not found",
    "treatment": (
        "No specific treatment available for this detected class. "
        "Collect a clear photo, note symptoms (spots, wilting, discoloration), "
        "and consult your local agricultural extension office or a trusted crop specialist."
    ),
    "prevention": (
        "General good practices: use certified seed/planting material, rotate crops, "
        "ensure balanced fertilization, avoid waterlogging, and monitor frequently."
    ),
    "example_classes": []
}


def _normalize_simple(simple: str) -> str:
    """
    Normalize a PlantVillage-style simple slug to our DB key.
    Accept inputs like "Tomato__Late_blight", "tomato_late_blight", "Tomato___Late_blight".
    """
    if not simple:
        return ""
    s = str(simple).lower().strip()
    s = s.replace("___", "_").replace("__", "_").replace(" - ", "_").replace(" ", "_")
    # remove accidental double underscores
    while "__" in s:
        s = s.replace("__", "_")
    return s


def get_info_for_simple(simple: str) -> Dict[str, Any]:
    """
    Return a dict with keys friendly_name, treatment, prevention, example_classes.
    If the slug is unknown, returns a safe generic entry.
    """
    key = _normalize_simple(simple)
    entry = _DISEASE_DB.get(key)
    if entry:
        # return a shallow copy so callers cannot accidentally mutate our DB
        return dict(entry)
    else:
        fallback = dict(_DEFAULT_ENTRY)
        fallback["friendly_name"] = f"Unknown ({simple})" if simple else fallback["friendly_name"]
        return fallback


def get_all_info() -> Dict[str, Dict[str, Any]]:
    """
    Return the entire disease DB (copy) keyed by normalized simple slugs.
    Useful for debugging or for exposing a documentation endpoint.
    """
    out = {}
    for k, v in _DISEASE_DB.items():
        out[k] = dict(v)
    return out


# Example convenience function in case other code wants mapping from detailed PlantVillage class name
def get_by_detailed_name(detailed_name: str) -> Dict[str, Any]:
    """
    Accept detailed names like 'Tomato___Late_blight' and return the matching entry.
    """
    if not detailed_name:
        return dict(_DEFAULT_ENTRY)
    # convert to simple slug and lookup
    simple = _normalize_simple(detailed_name.replace("___", "_"))
    return get_info_for_simple(simple)