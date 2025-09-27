# AI Agent Builder

AI Agent Builder for Swiss AI Hackathon.

Our builder allows you to start with creating your own AI agents **without** writing any code at all! Just select desired toolkit and let the work flow!

## Install

Use at least python version 3.11 and npm 11.2.0.

### Frontend

```sh
cd frontend
npm i
```

### Backend

```sh
cd backend

# Create a new python venv
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

## Run

You need two separate terminal sessions, for frontend and backend.

### Frontend

```sh
cd frontend
npm run dev
```

### Backend

```sh
cd backend
fastapi dev main.py
```

## Requirements

Create a `.env` file in the backend and frontend repos with the required env vars.

```env
SUPABASE_URL=
SUPABASE_KEY=
AGENTS_TABLE_NAME=agent
AGENTS_SET_TABLE_NAME=agent_set
SUPABASE_USER=
SUPABASE_PASSWORD=
OPENAI_API_KEY=
COMPOSIO_API_KEY=
SWISS_AI_PLATFORM_API_KEY=

```
