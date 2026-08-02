# apps/utils/utils.py


def custom_jsonable_encoder(obj):
    """Recursively encode lists and dicts to JSON-safe types."""
    if isinstance(obj, list):
        return [custom_jsonable_encoder(item) for item in obj]
    if isinstance(obj, dict):
        return {key: custom_jsonable_encoder(value) for key, value in obj.items()}
    return obj
