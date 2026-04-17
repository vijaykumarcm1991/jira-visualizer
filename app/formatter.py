from datetime import datetime

def format_datetime(value: str):
    try:
        dt = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f%z")
        return dt.strftime("%d-%b-%Y %I:%M %p")
    except Exception:
        return value


def parse_adf(content):
    """Extract text from Atlassian Document Format"""
    texts = []

    def extract(node):
        if isinstance(node, dict):
            if node.get("type") == "inlineCard":
                url = node.get("attrs", {}).get("url", "")
                texts.append(url)

            for child in node.get("content", []):
                extract(child)

        elif isinstance(node, list):
            for item in node:
                extract(item)

    extract(content)
    return " ".join(texts)


def format_comments(value):
    comments = value.get("comments", [])
    formatted = []

    for c in comments:
        author = c.get("author", {}).get("displayName", "Unknown")
        raw_body = c.get("body", "")
        created = format_datetime(c.get("created", ""))

        # 🔥 HANDLE ADF BODY (CLOUD)
        if isinstance(raw_body, dict) and raw_body.get("type") == "doc":
            body = parse_adf(raw_body)
        else:
            body = raw_body

        formatted.append(f"{author} ({created}): {body}")

    return "\n\n".join(formatted)


def format_value(value):
    # Skip empty
    if value in [None, "", [], {}]:
        return None

    # 🔥 DATE HANDLING
    if isinstance(value, str) and "T" in value and "+" in value:
        return format_datetime(value)

    # Simple types
    if isinstance(value, (str, int, float)):
        return value

    # 🔥 COMMENTS HANDLING
    if isinstance(value, dict) and "comments" in value:
        return format_comments(value)

    # 🔥 ADF (description, summary details)
    if isinstance(value, dict) and value.get("type") == "doc":
        return parse_adf(value)

    # Dict handling (Jira objects)
    if isinstance(value, dict):
        for key in ["displayName", "name", "value", "key"]:
            if key in value:
                return value[key]

        return str(value)

    # List handling
    if isinstance(value, list):
        formatted = []

        for item in value:
            if isinstance(item, dict):
                for key in ["displayName", "name", "value"]:
                    if key in item:
                        formatted.append(item[key])
                        break
            else:
                formatted.append(str(item))

        return ", ".join(formatted)

    return str(value)