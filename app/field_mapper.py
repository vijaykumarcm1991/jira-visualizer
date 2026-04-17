def build_field_map(fields_meta):
    field_map = {}

    for field in fields_meta:
        field_map[field["id"]] = field["name"]

    return field_map