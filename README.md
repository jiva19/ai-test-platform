# AI Test Execution Platform

An AI-driven test execution platform where QA engineers save structured test cases, organized by project, and an AI agent autonomously executes them against a real web application — reasoning through each step, verifying outcomes at the database level, and reporting a structured, trustworthy verdict.

This is built specifically around the hardest, least-solved problem in AI-driven testing: **reliability**. Most tools in this space focus on generating tests from natural language; this project focuses on making sure the AI's actions and conclusions can actually be trusted.

Built to run against [HrManagement.Api](https://github.com/jiva19/HrManagement.Api) and [HrManagement.Frontend](https://github.com/jiva19/HrManagement.Frontend), a full-stack HR management app built as its target.

## Core Reliability Design

- **DOM-grounded execution** — the agent never guesses at selectors. A `read_page` tool lets it inspect the real page for stable `data-testid` attributes before acting, added specifically after an early failure where a guessed CSS selector matched the wrong element.
- **Independent database verification** — a constrained, read-only `query_database` tool lets the agent confirm outcomes directly against the database, rather than trusting only what the UI displays.
- **Structured, three-state verdicts** — every run resolves to `PASS`, `FAIL`, or `BLOCKED`, so the agent correctly distinguishes a genuine application defect from a test whose precondition wasn't met.
- **Evidence capture** — screenshots organized per test case, per run, with the result embedded in the folder name for at-a-glance review.
- **Safety controls** — a hard cap on agent loop iterations prevents a stuck run from executing indefinitely, and strict spend limits are enforced on the underlying API usage.

## Features

- Organize test cases by project
- Structured test case authoring: name, preconditions, steps, and expected result
- Run any saved test case on demand from the UI
- Persisted run history per test case, including result, reasoning, and evidence location
- Asynchronous execution — a run starts and returns immediately, with the frontend polling for completion

## Tech Stack

- **Python**, **Flask**, **Flask-SQLAlchemy**
- **Anthropic Claude API** — tool use (function calling) driving the agent loop
- **Playwright** — browser automation
- **SQL Server** — persisted test cases, run history, and the application-under-test's data
- Plain HTML/CSS/JavaScript frontend (server-rendered, with `fetch`-based polling for live run status)

## Architecture

**Data model:** `Project` → `TestCase` → `TestRun`, a one-to-many hierarchy at each level.

**Execution loop:** a test case is compiled into a prompt and sent to Claude along with a constrained set of tools (`navigate`, `click`, `type_text`, `select_dropdown_option`, `read_page`, `screenshot`, `query_database`, `finish_test`). Claude reasons through each step, requesting one tool call at a time; the orchestrator executes it via Playwright, feeds the result back, and the loop continues until a structured verdict is reported via `finish_test`.

```
├── app.py                  # Flask routes
├── orchestrator.py         # The agent execution loop
├── tools.py                # Tool definitions given to Claude
├── prompts.py               # Compiles a TestCase into a prompt
├── models.py                # TestCase dataclass (execution-time shape)
├── db_models.py             # SQLAlchemy models (Project, TestCaseEntity, TestRunEntity)
├── repositories/            # Database access, one file per concern
├── templates/, static/       # Frontend
```

## Running Locally

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install
```

Create a `.env` file with:
```
ANTHROPIC_API_KEY=your-key-here
DB_PASSWORD=your-sql-server-password
```

Requires SQL Server running locally (a Docker container works well) and the target application under test (HrManagement.Api and HrManagement.Frontend) running alongside it.

```bash
python app.py
```

Visit `http://localhost:5001`.

## Roadmap

- Separate the platform's own data from the application-under-test's database
- Support concurrent ("run all") execution, with unique per-run test data to avoid collisions between parallel tests
- Adopt Flask-Migrate for real, versioned schema migrations
