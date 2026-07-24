from fastapi import FastAPI, Body
from fastapi.responses import JSONResponse, Response

app = FastAPI()

tasks = [
    {"id": 1, "title": "Buy groceries", "done": False},
    {"id": 2, "title": "Read a book", "done": True},
    {"id": 3, "title": "Learn FastAPI", "done": False},
]

@app.get("/")
def read_root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/tasks")
def get_tasks():
    return tasks

@app.get("/tasks/{id}")
def get_task(id: int):
    for task in tasks:
        if task["id"] == id:
            return task
    return JSONResponse(status_code=404, content={"error": f"Task {id} not found"})

@app.post("/tasks")
def create_task(payload: dict = Body(default={})):
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

@app.put("/tasks/{id}")
def update_task(id: int, payload: dict = Body(default={})):
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

@app.delete("/tasks/{id}")
def delete_task(id: int):
    for i, task in enumerate(tasks):
        if task["id"] == id:
            tasks.pop(i)
            return Response(status_code=204)
    return JSONResponse(status_code=404, content={"error": f"Task {id} not found"})