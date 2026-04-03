# AGENTS.md

This file provides guidance for AI agents working on the CommunityResourceDirectory project.

## Local Development with Docker Compose

The recommended way to run the project locally is with Docker Compose. This starts the Django web app and a PostgreSQL database with all environment variables pre-configured.

### Start the stack

```bash
docker compose up --build
```

The web application will be available at http://localhost:8000.

### Run management commands

To run Django management commands (e.g., `createsuperuser`, `makemigrations`) inside the running container:

```bash
docker compose exec web python manage.py <command>
```

### Stop the stack

```bash
docker compose down
```

To also remove the database volume:

```bash
docker compose down -v
```

## Environment Variables

See `.env.example` for all supported environment variables and their default values.

The Docker Compose file already sets all required variables for local development — no additional configuration is needed to get started.

## Tech Stack

- **Language:** Python
- **Framework:** Django 4.2+
- **Database:** PostgreSQL (via Docker Compose) / SQLite (fallback for non-Docker dev)
- **Dependencies:** `requirements.txt`

## Running Tests

```bash
docker compose exec web python manage.py test
```

Or without Docker (uses SQLite by default):

```bash
python manage.py test
```
