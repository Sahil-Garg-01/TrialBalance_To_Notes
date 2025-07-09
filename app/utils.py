def clean_value(value):
    try:
        if isinstance(value, str):
            value = value.replace(',', '').strip()
        return float(value) if value else 0.0
    except (ValueError, TypeError):
        return 0.0

def to_lakhs(value):
    return round(value / 100000, 2)