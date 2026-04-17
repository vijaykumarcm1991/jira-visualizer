import time

field_cache = {}
CACHE_TTL = 1800  # 10 mins


def get_cached_fields(instance):
    entry = field_cache.get(instance)

    if not entry:
        return None

    data, timestamp = entry

    if time.time() - timestamp > CACHE_TTL:
        return None

    return data


def set_cached_fields(instance, data):
    field_cache[instance] = (data, time.time())