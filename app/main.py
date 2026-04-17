from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
import os
from app.cache import get_cached_fields, set_cached_fields
from app.jira_client import fetch_issues, fetch_fields
from app.field_mapper import build_field_map
from app.transformer import transform_issues

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

templates = Jinja2Templates(directory=f"{BASE_DIR}/templates")


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
        {"request": request}
    )


@app.post("/search")
async def search(
    request: Request,
    query: str = Form(...),
    instance: str = Form(...),
    view: str = Form("card")
):
    raw_issues = await fetch_issues(query, instance)
    fields_meta = get_cached_fields(instance)

    if not fields_meta:
        print(f"Fetching fields for {instance} (cache miss)")
        fields_meta = await fetch_fields(instance)
        set_cached_fields(instance, fields_meta)
    else:
        print(f"Using cached fields for {instance}")
    
    field_map = build_field_map(fields_meta)

    clean_data = transform_issues(raw_issues, field_map)

    template = "issue_card.html" if view == "card" else "issue_table.html"

    return templates.TemplateResponse(
        request,
        template,
        {
            "request": request,
            "issues": clean_data
        }
    )