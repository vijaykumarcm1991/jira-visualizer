from app.formatter import format_value

def transform_issues(raw_issues, field_map):
    clean_issues = []

    for issue in raw_issues.get("issues", []):
        clean_fields = {}

        for key, value in issue["fields"].items():
            if value in [None, "", [], {}]:
                continue

            readable_name = field_map.get(key, key)

            formatted_value = format_value(value)

            if formatted_value in [None, ""]:
                continue

            clean_fields[readable_name] = formatted_value

        clean_issues.append({
            "key": issue["key"],
            "fields": clean_fields
        })

    return clean_issues