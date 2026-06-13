# PROJECT_MAP — TaskMaster

## [TECH_STACK]

| Layer | Technology | Version |
|-------|-----------|---------|
| Backend | Flask | 3.1.3 |
| ORM | SQLAlchemy | 2.0.50 |
| Auth | Flask-Login + bcrypt | 0.6.3 |
| Forms | Flask-WTF + WTForms | 1.2.2 |
| Migrations | Flask-Migrate + Alembic | 4.1.0 |
| AI | OpenAI SDK | 2.41.1 (gpt-4o) |
| Frontend | Jinja2 + HTMX 2.0 + Alpine.js 3.14 + Tailwind CSS | CDN |
| Database | SQLite (dev) / PostgreSQL (prod) | — |
| WSGI | Waitress (win) / Gunicorn (linux) | 3.0.2 |
| Testing | pytest + pytest-flask | 8.4.2 |
| Logging | stdlib + QueueHandler + RotatingFileHandler | — |
| Container | Docker + docker-compose | — |

## [SYSTEM_FLOW]

```
User Browser                          Flask Server                     OpenAI API
    │                                      │                              │
    ├─ GET / → Landing page ──────────────►│                              │
    ├─ GET/POST /register → Register ─────►│                              │
    ├─ GET/POST /login → Login ───────────►│                              │
    │                                      │                              │
    │  (authenticated session)             │                              │
    │                                      │                              │
    ├─ GET /dashboard ────────────────────►│ Aggregate task stats          │
    │◄─── Stats cards, nav links ──────────┤                              │
    │                                      │                              │
    ├─ GET /tasks/ → Kanban Board ────────►│ Query tasks by status        │
    │◄─── 4-column drag-drop board ────────┤                              │
    ├─ POST /tasks/move (JSON) ───────────►│ Update task.status/position  │
    │◄─── {ok: true} ──────────────────────┤                              │
    ├─ GET/POST /tasks/create → New Task ─►│ Create task                  │
    ├─ GET/POST /tasks/<id>/edit ─────────►│ Update task                  │
    ├─ POST /tasks/<id>/delete ───────────►│ Delete task                  │
    ├─ GET /tasks/<id> → Task Detail ─────►│ Query single task            │
    │                                      │                              │
    ├─ GET /projects/ → Project List ─────►│ Query user projects          │
    ├─ GET/POST /projects/create ─────────►│ Create project               │
    ├─ GET /projects/<id> ────────────────►│ Project detail with tasks    │
    │                                      │                              │
    ├─ GET /ai/ → AI Assistant ───────────►│                              │
    ├─ POST /ai/generate-task (JSON) ─────►│                              ├──► generate task
    │◄─── {description, hours, priority} ──┤◄─────────────────────────────┤
    ├─ POST /ai/chat (JSON) ──────────────►│                              ├──► chat completion
    │◄─── {reply: "..."} ──────────────────┤◄─────────────────────────────┤
```

## [ARCHITECTURE]

```
taskmaster/
├── app/
│   ├── __init__.py              # create_app() factory + error handlers
│   ├── config.py                # Config / DevConfig / TestConfig / ProdConfig
│   ├── extensions.py            # db, login_manager, migrate, csrf
│   ├── models.py                # User, Project, Task (single file)
│   ├── forms.py                 # LoginForm, RegisterForm, ProjectForm, TaskForm, AIForm
│   ├── services.py              # create_task, update_task, delete_task, move_task, get_dashboard_stats
│   ├── utils.py                 # setup_logging, register_error_handlers
│   ├── routes/
│   │   ├── auth.py              # /register, /login, /logout
│   │   ├── main.py              # /, /dashboard
│   │   ├── tasks.py             # /tasks/* (board, create, edit, delete, move, detail)
│   │   ├── projects.py          # /projects/* (list, create, detail, edit, delete)
│   │   └── ai.py                # /ai/* (assistant, generate-task, chat)
│   └── templates/
│       ├── base.html            # Tailwind + HTMX + Alpine.js shell
│       ├── landing.html         # Public landing page
│       ├── auth/                # login.html, register.html
│       ├── tasks/               # board.html, form.html, detail.html
│       ├── projects/            # list.html, form.html, detail.html
│       ├── dashboard/           # index.html
│       ├── ai/                  # assistant.html
│       └── errors/              # 404.html, 500.html
├── tests/
│   ├── conftest.py              # Fixtures: app, client, registered_user, logged_in_client
│   ├── test_auth.py             # 8 tests (register, login, logout, auth guards)
│   ├── test_tasks.py            # 6 tests (CRUD, board, detail)
│   └── test_projects.py         # 4 tests (CRUD, detail)
├── requirements.txt
├── .env / .env.example
├── Dockerfile
├── docker-compose.yml
├── Makefile
└── PROJECT_MAP.md
```

### Design Decisions
- **Single-file models** — avoids micro-file fragmentation; all 3 entities fit in <100 lines
- **No Celery** — AI calls are synchronous; complexity not justified for MVP
- **No REST API** — server-rendered HTML with HTMX for interactivity; separates not needed until API consumers exist
- **Kanban via native HTML drag-drop** — no external library dependency for core interaction; SortableJS loaded optionally
- **TestConfig uses :memory: SQLite** WTF_CSRF disabled — fast isolated tests

## [ORPHANS & PENDING]

| Item | Status | Notes |
|------|--------|-------|
| AI tests | PENDING | Requires live OpenAI API key; mock-based tests needed |
| DB migrations init | PENDING | Run `flask db init && flask db migrate && flask db upgrade` before prod. `db.create_all()` in create_app() handles dev auto-setup |
| PostgreSQL adapter | PENDING | Add `psycopg2` to requirements when switching to PostgreSQL |
| OAuth (Google/GitHub) | FUTURE | Not in scope for MVP; Flask-Login extension when needed |
| Stripe billing | FUTURE | Not in scope for MVP |
| Email notifications | FUTURE | Not in scope for MVP |
| Task search/filter | FUTURE | SQL LIKE works for now; full-text search when needed |
| Pagination | FUTURE | Not needed until >100 tasks; SQL LIMIT works |

## [CHANGE_LOG]

| Date | Change | Author |
|------|--------|--------|
| 2026-06-13 | Initial scaffold: app factory, config, models, auth, tasks, projects, AI, logging, error pages, Docker, tests | Tech Lead |
| 2026-06-13 | Fix: auto-create DB tables in create_app() to prevent 500 on first register | Tech Lead |
