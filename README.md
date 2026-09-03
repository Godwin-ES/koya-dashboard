# Koya Operations Command Center

A polished Streamlit dashboard for Koya Talent's AI Operations Reporting System. The dashboard triggers the existing n8n reporting workflow, loads the exact returned run from Supabase, and presents deterministic KPIs alongside model-generated decision support.

## Product structure

- **Overview** — report health, a selective cross-functional KPI snapshot, executive summary, risks, and recommended actions.
- **Sales** — commercial KPIs and Closed Won revenue by lead source.
- **Project Delivery** — delivery KPIs, snapshot limitations, and team delivery load.
- **People Ops** — hiring, workforce movement, recruiting pace, and headcount distribution.
- **Data Quality** — executive limitations plus the filterable deterministic issue register.

The frontend formats persisted values but does not recalculate business KPIs. Supabase report runs, KPI metrics, AI insights, and data-quality issues remain authoritative.

## Local setup

This project requires Python 3.11 or newer and uses uv for reproducible dependency management.

1. Install dependencies:

   ~~~bash
   uv sync
   ~~~

2. Copy the configuration template:

   ~~~bash
   cp .streamlit/secrets.example.toml .streamlit/secrets.toml
   ~~~

3. Add the deployed n8n webhook URL and the dashboard-safe Supabase URL and anon/publishable key. Never use a Supabase service-role key.

4. Start the dashboard:

   ~~~bash
   uv run streamlit run app.py
   ~~~

5. Open http://localhost:8501.

## Tests

Run the unit suite with:

~~~bash
uv run pytest -q
~~~

The tests cover request payload validation, date bounds, null-safe value formatting, percentage-point comparison semantics, dimensional metric filtering, and data-quality preparation.

## Deployment

Deploy the directory as a Streamlit app with app.py as the entrypoint and configure these three secrets in the hosting environment:

~~~toml
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_ANON_KEY = "your-anon-or-publishable-key"
N8N_WEBHOOK_URL = "https://your-n8n-host/webhook/week2-operations-report"
~~~

The Supabase key should have read-only RLS access to reporting tables. If the dashboard is public, protect or rate-limit report generation because the primary action starts a live n8n execution.

## Reporting constraints

- Reporting is anchored to **30 June 2026** because the supplied source data ends then.
- Custom dates are constrained to **1 January 2025–30 June 2026**.
- Currency denomination is not supplied, so currency values intentionally have no symbol.
- Project status is a current snapshot; the interface surfaces the backend's calculation limitation.
- A partial run keeps deterministic reporting usable when AI analysis is unavailable.
