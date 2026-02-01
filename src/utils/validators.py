def is_positive_int(v):
    try:
        return int(v) > 0
    except Exception:
        return False
