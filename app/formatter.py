from datetime import datetime

def format_datetime(value: str):
    try:
        dt = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f%z")
        return dt.strftime("%d-%b-%Y %I:%M %p")
    except Exception:
        return value


def parse_adf(content):
    texts = []

    def extract(node):
        if isinstance(node, dict):

            node_type = node.get("type")

            # TEXT
            if node_type == "text":
                texts.append(node.get("text", ""))

            # INLINE LINK / CARD
            elif node_type == "inlineCard":
                url = node.get("attrs", {}).get("url", "")
                texts.append(url)

            # MENTION (user tags)
            elif node_type == "mention":
                name = node.get("attrs", {}).get("text", "")
                texts.append(name)

            # HARD BREAK
            elif node_type == "hardBreak":
                texts.append("\n")

            # RECURSE
            for child in node.get("content", []):
                extract(child)

        elif isinstance(node, list):
            for item in node:
                extract(item)

    extract(content)

    # 🔥 CLEAN EMPTY / NOISE
    final_text = " ".join(texts)
    final_text = final_text.replace(" \n ", "\n").strip()

    return final_text if final_text else ""

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

        # 🔥 Skip empty comments
        if not body or not str(body).strip():
            continue

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

    # 🔥 WORKLOG HANDLING
    if isinstance(value, dict) and "worklogs" in value:
        return format_worklog(value)

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

def format_worklog(value):
    worklogs = value.get("worklogs", [])
    formatted = []

    for w in worklogs:
        author = w.get("author", {}).get("displayName", "Unknown")
        time_spent = w.get("timeSpent", "")
        started = format_datetime(w.get("started", ""))

        comment_raw = w.get("comment", "")

        if isinstance(comment_raw, dict) and comment_raw.get("type") == "doc":
            comment = parse_adf(comment_raw)
        else:
            comment = comment_raw

        entry = f"{author} ({started})\nTime Spent: {time_spent}"

        if comment:
            entry += f"\nComment: {comment}"

        formatted.append(entry)

    return "\n\n".join(formatted)