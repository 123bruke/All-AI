import os

MICROSOFT_COPILOT_KEY = os.getenv("MICROSOFT_COPILOT_KEY", "")
MICROSOFT_COPILOT_ENDPOINT = os.getenv("MICROSOFT_COPILOT_ENDPOINT", "")

def analyze_images(image_paths):
    """
    Placeholder for Microsoft Copilot image analysis.
    Replace with real API calls.
    """
    results = []
    for p in image_paths:
        results.append({
            "image_path": p,
            "caption": "Placeholder caption for " + os.path.basename(p),
            "objects": ["placeholder_object_1", "placeholder_object_2"]
        })
    return results
