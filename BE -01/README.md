# Task API (BE-01 · Week 3 / Assignment A3)

A production-grade RESTful CRUD API built with **FastAPI**, **Python**, and a **PostgreSQL** database, fully containerized with **Docker** and **Docker Compose**.

---

## 📌 Project Overview

This assignment represents the third storage evolution of our Task API:
1. **Assignment 1:** In-memory list *(volatile RAM)*
2. **Assignment 2:** SQLite file *(single file on local disk)*
3. **Assignment 3 (This project):** **Containerized PostgreSQL Database** managed via **Docker Compose**

The API endpoints, request schemas, status codes, and validation rules remain 100% consistent, while the underlying storage is powered by a real PostgreSQL server.

---

## 🚀 One-Command Quick Start

### 1. Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (running with WSL 2 or Hyper-V backend)

### 2. Environment Configuration
Copy the example environment file:
```bash
cp .env.example .env
```
The default `.env` includes:
```env
DATABASE_URL=postgresql://postgres:dev@localhost:5432/tasks
```

### 3. Run the Entire Stack
Start both the FastAPI application and PostgreSQL database with a single command:
```bash
docker compose up --build
```
> The API will be live at `http://127.0.0.1:8000`  
> Interactive Swagger Documentation: `http://127.0.0.1:8000/docs`

To stop the stack:
```bash
docker compose down
```

---

## 📑 API Endpoints Summary

| Method | Endpoint | Description | Success Status | Error Status |
| :--- | :--- | :--- | :---: | :---: |
| `GET` | `/` | API metadata and documentation info | `200 OK` | — |
| `GET` | `/health` | Health check endpoint | `200 OK` | — |
| `GET` | `/tasks` | List all tasks (supports `?done=true`, `?search=query`, `?sort=title`) | `200 OK` | — |
| `GET` | `/tasks/{id}` | Retrieve a single task by ID | `200 OK` | `404 Not Found` |
| `POST` | `/tasks` | Create a new task (`{"title": "..."}`) | `201 Created` | `400 Bad Request` |
| `PUT` | `/tasks/{id}` | Update task `title` and/or `done` status | `200 OK` | `400 Bad Request`, `404 Not Found` |
| `DELETE` | `/tasks/{id}` | Delete a task by ID | `204 No Content` | `404 Not Found` |
| `GET` | `/stats` | Task statistics computed via SQL `COUNT(*)` | `200 OK` | — |
| `POST` | `/reset` | Restores database to the 3 original seed tasks | `200 OK` | — |

---

## 💻 Sample `curl -i` Command & Response Output

### 1. `GET /tasks` (Read All Tasks)
```bash
curl -i http://127.0.0.1:8000/tasks
```
```http
HTTP/1.1 200 OK
date: Sun, 13 Sep 2026 11:57:39 GMT
server: uvicorn
content-length: 136
content-type: application/json

[{"id":1,"title":"Buy groceries","done":false},{"id":2,"title":"Read a book","done":true},{"id":3,"title":"Learn FastAPI","done":false}]
```

### 2. `POST /tasks` (Create Task with Postgres `RETURNING`)
```bash
curl -i -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Containerize with Docker"}'
```
```http
HTTP/1.1 201 Created
date: Sun, 13 Sep 2026 11:58:05 GMT
server: uvicorn
content-length: 56
content-type: application/json

{"id":4,"title":"Containerize with Docker","done":false}
```

### 3. `GET /tasks/999` (404 Error Handling)
```bash
curl -i http://127.0.0.1:8000/tasks/999
```
```http
HTTP/1.1 404 Not Found
date: Sun, 13 Sep 2026 11:58:10 GMT
server: uvicorn
content-length: 30
content-type: application/json

{"error":"Task 999 not found"}
```

---

## 🗄️ Database Inspection Inside Container

You can inspect the PostgreSQL database directly inside the container via `docker exec`:

```bash
docker exec -it be-01-db-1 psql -U postgres -d tasks
```

```text
tasks=# \dt
         List of relations
 Schema | Name  | Type  |  Owner   
--------+-------+-------+----------
 public | tasks | table | postgres
(1 row)

tasks=# SELECT * FROM tasks;
 id |          title          | done 
----+-------------------------+------
  1 | Buy groceries           | f
  2 | Read a book             | t
  3 | Learn FastAPI           | f
  4 | Containerize with Docker| f
(4 rows)
```

---

## 💾 Persistence Across Restarts (Named Volume)

- Database storage is mapped to the named volume **`taskdata`** (`taskdata:/var/lib/postgresql/data`).
- When you execute `docker compose down` and later `docker compose up`, your tasks are completely preserved because the volume outlives the containers.

---

## 🔒 Secret Management (.env)

- **`.env`** holds your local connection credentials and is excluded from source control via `.gitignore`.
- **`.env.example`** is committed to the repository so anyone cloning the project knows which variables to configure.
