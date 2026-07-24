from fastapi import FastAPI, Body
from fastapi.responses import JSONResponse, Response

app = FastAPI(
    title="Task API",
    description="A simple task management API built with FastAPI.",
    version="1.0"
)

tasks = [
    {"id": 1, "title": "Buy groceries", "done": False},
    {"id": 2, "title": "Read a book", "done": True},
    {"id": 3, "title": "Learn FastAPI", "done": False},
]

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

@app.get("/tasks", summary="List all tasks")
def get_tasks():
    """Retrieve the full list of task objects."""
    return tasks

@app.get("/tasks/{id}", summary="Get a task by ID")
def get_task(id: int):
    """Retrieve a single task object by its unique ID, or return 404 if not found."""
    for task in tasks:
        if task["id"] == id:
            return task
    return JSONResponse(status_code=404, content={"error": f"Task {id} not found"})

@app.post("/tasks", summary="Create a new task")
def create_task(payload: dict = Body(default={})):
    """Create a new task with a given title."""
    title = payload.get("title") if isinstance(payload, dict) else None
    if not title or not isinstance(title, str) or not title.strip():
        return JSONResponse(status_code=400, content={"error": "Title is required and cannot be empty"})
    
    next_id = max([t["id"] for t in tasks], default=0) + 1
    new_task = {
        "id": next_id,
        "title": title.strip(),
        "done": False
    }
    tasks.append(new_task)
    return JSONResponse(status_code=201, content=new_task)

@app.put("/tasks/{id}", summary="Update an existing task")
def update_task(id: int, payload: dict = Body(default={})):
    """Update title and/or done status for a task by ID."""
    if not isinstance(payload, dict) or not payload:
        return JSONResponse(status_code=400, content={"error": "Request body cannot be empty"})
    
    task_to_update = None
    for task in tasks:
        if task["id"] == id:
            task_to_update = task
            break
            
    if not task_to_update:
        return JSONResponse(status_code=404, content={"error": f"Task {id} not found"})
    
    has_update = False
    if "title" in payload:
        title = payload["title"]
        if not isinstance(title, str) or not title.strip():
            return JSONResponse(status_code=400, content={"error": "Title cannot be empty"})
        task_to_update["title"] = title.strip()
        has_update = True
        
    if "done" in payload:
        done = payload["done"]
        if not isinstance(done, bool):
            return JSONResponse(status_code=400, content={"error": "Done must be a boolean"})
        task_to_update["done"] = done
        has_update = True
        
    if not has_update:
        return JSONResponse(status_code=400, content={"error": "No valid fields to update"})
        
    return task_to_update

@app.delete("/tasks/{id}", summary="Delete a task by ID")
def delete_task(id: int):
    """Delete a task by ID and return 204 No Content."""
    for i, task in enumerate(tasks):
        if task["id"] == id:
            tasks.pop(i)
            return Response(status_code=204)
    return JSONResponse(status_code=404, content={"error": f"Task {id} not found"})