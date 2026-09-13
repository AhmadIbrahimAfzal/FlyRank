# Task API (BE-01 · Week 3 / Assignment A2)

A clean, production-grade RESTful CRUD API built with **FastAPI**, **Python**, and a **SQLite** database (`tasks.db`).

---

## 📌 Project Overview

In Week 2, the API stored data in-memory. In Week 3 (Assignment A2), the storage layer was completely migrated to a persistent **SQLite database (`tasks.db`)**. 

The API interface, endpoints, response schemas, and status codes remain 100% consistent, but data now **survives server restarts**.

---

## 💡 Why SQLite?

- **Zero-Configuration & Serverless**: SQLite requires no external database daemon or background process.
- **Single File Storage**: All tables, schema definitions, and rows reside in a single file (`tasks.db`).
- **Disk Persistence**: Data reliably persists across server restarts and crashes.
- **Safe & Standard**: Utilizes Python's built-in `sqlite3` library with parameterized queries (`?`) to prevent SQL injection vulnerabilities.

---

## 📁 Database File Location & Auto-Creation

- **Database File**: Located at `BE -01/tasks.db` (created automatically upon application startup).
- **Auto-Initialization & Seeding**: If `tasks.db` does not exist or the table is empty, the database creates the `tasks` table and seeds 3 initial tasks.
- **Clean Clone**: `tasks.db` is `.gitignore`d so every fresh clone initializes cleanly with a single command.

---

## 🚀 Quick Start (Install & Run)

### 1. Prerequisites
- Python 3.10+
- `pip` package manager

### 2. Installation
Install the required packages:
```bash
pip install fastapi uvicorn watchfiles
```

### 3. Run the Server
From the `BE -01` directory, start the development server:
```bash
uvicorn main:app --reload
```
> The API will be live at `http://127.0.0.1:8000`

---

## 📑 API Endpoints Summary

| Method | Endpoint | Description | Success Status | Error Status |
| :--- | :--- | :--- | :---: | :---: |
| `GET` | `/` | API metadata and documentation info | `200 OK` | — |
| `GET` | `/health` | Server health check endpoint | `200 OK` | — |
| `GET` | `/tasks` | List all tasks (supports `?done=true`, `?search=query`, `?sort=title`) | `200 OK` | — |
| `GET` | `/tasks/{id}` | Retrieve a single task by ID | `200 OK` | `404 Not Found` |
| `POST` | `/tasks` | Create a new task (`{"title": "..."}`) | `201 Created` | `400 Bad Request` |
| `PUT` | `/tasks/{id}` | Update task `title` and/or `done` status | `200 OK` | `400 Bad Request`, `404 Not Found` |
| `DELETE` | `/tasks/{id}` | Delete a task by ID | `204 No Content` | `404 Not Found` |
| `GET` | `/stats` | Task statistics computed via SQL `COUNT(*)` | `200 OK` | — |
| `POST` | `/reset` | Restores database to the 3 original seed tasks | `200 OK` | — |

---

## 🔍 Stage 4: SQL Explored by Hand (DB Browser for SQLite)

During manual inspection of `tasks.db` in **DB Browser for SQLite**, the following queries were executed:

```sql
-- 1. List all tasks
SELECT * FROM tasks;

-- 2. Fetch only completed tasks
SELECT * FROM tasks WHERE done = 1;

-- 3. Count total number of tasks
SELECT COUNT(*) FROM tasks;

-- 4. Mark all tasks as completed
UPDATE tasks SET done = 1;

-- 5. Delete completed tasks
DELETE FROM tasks WHERE done = 1;
```

**Observation:** Direct modifications made via DB Browser for SQLite reflected immediately on API endpoints (`GET /tasks`) without needing to restart the server, proving that the SQLite database file serves as the single source of truth.

---

## 💻 Sample `curl -i` Command & Response Output

### 1. `GET /tasks/1` (Read Task)
```bash
curl -i http://127.0.0.1:8000/tasks/1
```
```http
HTTP/1.1 200 OK
date: Sun, 13 Sep 2026 10:20:00 GMT
server: uvicorn
content-length: 51
content-type: application/json

{"id":1,"title":"Buy groceries","done":false}
```

### 2. `POST /tasks` (Create Task)
```bash
curl -i -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d "{\"title\": \"Finish Backend Assignment\"}"
```
```http
HTTP/1.1 201 Created
date: Sun, 13 Sep 2026 10:20:05 GMT
server: uvicorn
content-length: 58
content-type: application/json

{"id":4,"title":"Finish Backend Assignment","done":false}
```

### 3. `GET /tasks/999` (404 Error Handling)
```bash
curl -i http://127.0.0.1:8000/tasks/999
```
```http
HTTP/1.1 404 Not Found
date: Sun, 13 Sep 2026 10:20:10 GMT
server: uvicorn
content-length: 30
content-type: application/json

{"error":"Task 999 not found"}
```

---

## 🎨 Interactive API Documentation (Swagger UI)

FastAPI automatically generates an interactive Swagger UI available at:
👉 **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

![Swagger UI Screenshot](./swagger_ui.png)

---

## 🔬 The Mortality Experiment & Persistence

> **Observation:** In Week 2, restarting the server erased all newly added tasks because memory (RAM) is ephemeral. In Week 3, because data is written to disk via SQLite (`tasks.db`), stopping and restarting the server leaves all tasks completely intact.

---

## ⚡ Stretch Goals & Performance Optimizations

1. **Indexes on Filter & Search Columns**:
   - `idx_tasks_done` on `tasks(done)` speeds up status queries (`WHERE done = ?`).
   - `idx_tasks_title` on `tasks(title)` speeds up text lookup and sorting (`ORDER BY title`).
   - *What an index is for:* An index is a fast-lookup data structure (B-tree in SQLite) that allows the database engine to locate matching rows without scanning every row in the table sequentially.

2. **Atomic Transactions**:
   - Multi-step seed insertions and batch resets are executed inside transactions (`conn.commit()`) ensuring an all-or-nothing guarantee that prevents corrupted, partial writes.

---

## 🤖 Stage 6: AI vs Me (The AI Rematch)

An independent AI version was generated in quarantine under the `ai-version/` folder based on specification prompts.

### Prompt Used:
> *"Build a complete FastAPI REST CRUD API backed by SQLite (`tasks.db`) using Python's standard `sqlite3` library. The database table `tasks` must have columns `id` (INTEGER PRIMARY KEY AUTOINCREMENT), `title` (TEXT NOT NULL), and `done` (INTEGER NOT NULL DEFAULT 0). The table must be created if missing, and seeded with 3 default tasks only when the count is 0. Implement GET /tasks, GET /tasks/{id}, POST /tasks (400 on empty/missing title, 201 on success), PUT /tasks/{id} (400 on empty body, 404 on missing id), and DELETE /tasks/{id} (204 on success, 404 on missing id). Always use parameterized SQL queries (`?`) for safety."*

### Key Comparison Differences:
1. **Context Manager Pattern**: The AI version utilized `with get_db() as conn:` context managers for automatic transaction management and closing, whereas the manual implementation used explicit connection opening and closing.
2. **Query Building**: The hand-built version included dynamic query construction for search, status filtering, and sorting (`?search=...`, `?done=...`, `?sort=...`) along with `GET /stats`.
3. **Seed Idempotency**: Both versions correctly checked `SELECT COUNT(*) FROM tasks` before inserting seed data to prevent duplicating sample rows across restarts.

