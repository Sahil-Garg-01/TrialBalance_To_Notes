def clean_value(value):
    try:
        if isinstance(value, str):
            value = value.replace(',', '').strip()
        return float(value) if value else 0.0
    except (ValueError, TypeError):
        return 0.0

def to_lakhs(value):
    return round(value / 100000, 2)


def convert_note_json_to_lakhs(note_json):
    """Recursively convert all numeric values in note JSON to lakhs."""
    from app.utils import to_lakhs

    def convert(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (int, float)):
                    obj[k] = to_lakhs(v)
                elif isinstance(v, str):
                    try:
                        obj[k] = to_lakhs(float(v.replace(',', '')))
                    except Exception:
                        pass
                else:
                    obj[k] = convert(v)
        elif isinstance(obj, list):
            for i in range(len(obj)):
                obj[i] = convert(obj[i])
        return obj

    return convert(note_json)