---
mode: agent
description: Add a new full-stack feature to the L7 CNOTA Dashboard — creates a FastAPI router and matching React dashboard view.
---


# Add New CNOTA Feature
/add-features
Add a new feature to the **L7 CNOTA Dashboard** that follows the existing split between the FastAPI backend (`backend/routers/`) and the React dashboard frontend (`frontend/src/components/`).

## Inputs
- **Feature name**: `${input:featureName:Snake-case name, e.g. "missions" or "virtue_log"}`
- **Short description**: `${input:featureDescription:One line describing what this feature does}`

## Step 1 — Backend Router

Create `backend/routers/${input:featureName}.py` following these conventions:

- Import `APIRouter` and any needed Pydantic models from `fastapi` and `pydantic`.
- Define a `router = APIRouter()` at module level.
- Prefix all route paths with `/api/${input:featureName}/`.
- Use `async def` handlers.
- Return mock/stub data for now — see existing patterns in `backend/routers/cnota.py` and `backend/routers/passport.py` for reference.
- Add a docstring to every endpoint describing its purpose.
- Use `Query(default=..., ge=..., le=...)` for pagination parameters where relevant.

Example shape to follow:
```python
"""${input:featureDescription}."""
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

@router.get("/api/${input:featureName}/list")
async def list_items():
    """Return a list of ${input:featureName} items."""
    return {"items": [], "total": 0}
```

## Step 2 — Register the Router

In `backend/main.py`, import and register the new router:

```python
from routers import ..., ${input:featureName}
...
app.include_router(${input:featureName}.router)
```

Keep the import line sorted alphabetically with the existing router imports.

## Step 3 — Frontend Component

Create `frontend/src/components/${input:featureName|capitalize}View.jsx` following these conventions:

- Functional React component using hooks (`useState`, `useEffect`).
- Fetch data with `axios` from `/api/${input:featureName}/...`.
- Include a loading state and a fallback for when data is unavailable.
- Reference the four Stoic virtue fields (`sophia`, `andreia`, `dikaiosyne`, `sophrosyne`) if the feature displays user scores.
- Use `const MOCK_*` constants at the top of the file for safe fallback data during development.
- Match the CSS class naming conventions from `frontend/src/App.css`.

## Step 4 — Wire Into Layout

In `frontend/src/components/Layout.jsx`, add a navigation link to the new view.  
In `frontend/src/App.jsx`, import the new component and add its route.

## Constraints

- Do **not** rename or alter existing API endpoints in `cnota.py`, `passport.py`, or `rewards_processor.py`.
- Keep all API paths rooted at `/api`.
- Backend port is `7860` — do not change.
- Do not add external dependencies without updating `backend/requirements.txt` and `frontend/package.json`.

## Done

After generating the code, summarize:
1. Files created/modified.
2. How to test the new endpoint (curl example).
3. Which mock fields should be replaced with real data first.
