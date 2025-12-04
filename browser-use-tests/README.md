# Browser-Use Tests

Browser-Use agent for testing vulnerable applications.

## Setup

```bash
uv venv --python 3.11
source .venv/bin/activate
uv sync
uvx browser-use install
```

Copy `.env.example` to `.env` and add your API key:

```bash
cp .env.example .env
```

Get a free API key at https://cloud.browser-use.com/new-api-key

## Usage

```bash
# Default exploration task
uv run agent.py --url "http://localhost:5000"

# Custom task
uv run agent.py --url "http://localhost:5000" --task "Try to login with admin credentials"

# Headless mode
uv run agent.py --url "http://localhost:5000" --headless
```
