import os
import sqlite3
from fastapi import FastAPI, Body
from fastapi.responses import JSONResponse, Response

app = FastAPI(
    title="Task API",
    description="A simple task management API built with FastAPI and SQLite.",
    version="1.0"
)

DB_PATH = os.path.join(os.path.dirname(__file__), "tasks.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done INTEGER NOT NULL DEFAULT 0
        )
    """)
    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]
    if count == 0:
        seed_tasks = [
            ("Buy groceries", 0),
            ("Read a book", 1),
            ("Learn FastAPI", 0)
        ]
        cursor.executemany("INSERT INTO tasks (title, done) VALUES (?, ?)", seed_tasks)
        conn.commit()
    conn.close()

init_db()

@app.get("/", summary="Get API information")
def read_root():
    """Return metadata about the API."""
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }

@app.get("/health", summary="Health check endpoint")
def health_check():
    """Check if the server is healthy and alive."""
    return {"status": "ok"}

from typing import Optional

def format_task(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"])
    }

@app.get("/tasks", summary="List all tasks")
def get_tasks(
    done: Optional[bool] = None,
    search: Optional[str] = None,
    sort: Optional[str] = None
):
    """Retrieve tasks with optional filtering, search, and sorting from SQLite."""
    conn = get_db_connection()
    query = "SELECT * FROM tasks"
    conditions = []
    params = []
    
    if done is not None:
        conditions.append("done = ?")
        params.append(1 if done else 0)
        
    if search is not None and search.strip():
        conditions.append("title LIKE ?")
        params.append(f"%{search.strip()}%")
        
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
        
    if sort == "title":
        query += " ORDER BY title ASC"
    else:
        query += " ORDER BY id ASC"
        
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [format_task(row) for row in rows]

@app.get("/tasks/{id}", summary="Get a task by ID")
def get_task(id: int):
    """Retrieve a single task object by its unique ID from the database, or return 404 if not found."""
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (id,)).fetchone()
    conn.close()
    if row is None:
        return JSONResponse(status_code=404, content={"error": f"Task {id} not found"})
    return format_task(row)

@app.post("/tasks", summary="Create a new task")
def create_task(payload: dict = Body(default={})):
    """Create a new task with a given title in the database."""
    title = payload.get("title") if isinstance(payload, dict) else None
    if not title or not isinstance(title, str) or not title.strip():
        return JSONResponse(status_code=400, content={"error": "Title is required and cannot be empty"})
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", (title.strip(), 0))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    new_task = {
        "id": new_id,
        "title": title.strip(),
        "done": False
    }
    return JSONResponse(status_code=201, content=new_task)

@app.put("/tasks/{id}", summary="Update an existing task")
def update_task(id: int, payload: dict = Body(default={})):
    """Update title and/or done status for a task by ID in the database."""
    if not isinstance(payload, dict) or not payload:
        return JSONResponse(status_code=400, content={"error": "Request body cannot be empty"})
    
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (id,)).fetchone()
    if row is None:
        conn.close()
        return JSONResponse(status_code=404, content={"error": f"Task {id} not found"})
    
    current_title = row["title"]
    current_done = row["done"]
    has_update = False
    
    if "title" in payload:
        title = payload["title"]
        if not isinstance(title, str) or not title.strip():
            conn.close()
            return JSONResponse(status_code=400, content={"error": "Title cannot be empty"})
        current_title = title.strip()
        has_update = True
        
    if "done" in payload:
        done = payload["done"]
        if not isinstance(done, bool):
            conn.close()
            return JSONResponse(status_code=400, content={"error": "Done must be a boolean"})
        current_done = 1 if done else 0
        has_update = True
        
    if not has_update:
        conn.close()
        return JSONResponse(status_code=400, content={"error": "No valid fields to update"})
        
    conn.execute("UPDATE tasks SET title = ?, done = ? WHERE id = ?", (current_title, current_done, id))
    conn.commit()
    updated_row = conn.execute("SELECT * FROM tasks WHERE id = ?", (id,)).fetchone()
    conn.close()
    
    return format_task(updated_row)

@app.delete("/tasks/{id}", summary="Delete a task by ID")
def delete_task(id: int):
    """Delete a task by ID from the database and return 204 No Content."""
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (id,)).fetchone()
    if row is None:
        conn.close()
        return JSONResponse(status_code=404, content={"error": f"Task {id} not found"})
    
    conn.execute("DELETE FROM tasks WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return Response(status_code=204)

@app.get("/stats", summary="Task statistics")
def get_stats():
    """Retrieve task counts directly computed with SQL COUNT(*)."""
    conn = get_db_connection()
    total = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    done_count = conn.execute("SELECT COUNT(*) FROM tasks WHERE done = 1").fetchone()[0]
    open_count = conn.execute("SELECT COUNT(*) FROM tasks WHERE done = 0").fetchone()[0]
    conn.close()
    return {
        "total": total,
        "done": done_count,
        "open": open_count
    }

@app.post("/reset", summary="Reset database to default seed data")
def reset_tasks():
    """Reset the database tasks table back to the initial 3 example tasks."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='tasks'")
    seed_tasks = [
        ("Buy groceries", 0),
        ("Read a book", 1),
        ("Learn FastAPI", 0)
    ]
    cursor.executemany("INSERT INTO tasks (title, done) VALUES (?, ?)", seed_tasks)
    conn.commit()
    rows = cursor.execute("SELECT * FROM tasks ORDER BY id ASC").fetchall()
    conn.close()
    return {"message": "Task database has been reset to default example tasks", "tasks": [format_task(r) for r in rows]}