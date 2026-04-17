import os
import httpx
from dotenv import load_dotenv

load_dotenv()


def get_config(instance: str):
    if instance == "cloud":
        return {
            "base_url": os.getenv("JIRA_CLOUD_URL"),
            "auth": (
                os.getenv("JIRA_CLOUD_EMAIL"),
                os.getenv("JIRA_CLOUD_API_TOKEN")
            ),
            "api_version": "3"
        }

    elif instance == "onprem":
        return {
            "base_url": os.getenv("JIRA_ONPREM_URL"),
            "auth": (
                os.getenv("JIRA_ONPREM_USERNAME"),
                os.getenv("JIRA_ONPREM_PASSWORD")
            ),
            "api_version": "2"
        }

def normalize_query(query: str):
    query = query.strip()

    # If user enters just issue key (e.g., ABC-123)
    if " " not in query and "-" in query:
        return f"issueKey = {query}"

    return query

async def fetch_issues(query: str, instance: str):
    config = get_config(instance)

    # ✅ normalize query
    query = normalize_query(query)

    if instance == "cloud":
        url = f"{config['base_url']}/rest/api/3/search/jql"
    else:
        url = f"{config['base_url']}/rest/api/{config['api_version']}/search"

    params = {
        "jql": query,
        "maxResults": 50,
        "fields": "*all"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, auth=config["auth"])

        print("INSTANCE:", instance)
        print("STATUS:", response.status_code)
        print("URL:", response.url)
        print("RESPONSE:", response.text[:500])  # 🔥 add this

        return response.json()


async def fetch_fields(instance: str):
    config = get_config(instance)

    url = f"{config['base_url']}/rest/api/{config['api_version']}/field"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, auth=config["auth"])

        return response.json()