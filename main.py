from fastapi import FastAPI
from modules.users.routes.createUser import router as create_router
from modules.users.routes.readUser import router as read_router
from modules.users.routes.updateUser import router as update_router
from modules.users.routes.deleteUser import router as delete_router

app = FastAPI(title="Tugas 2 - CRUD Users (tanpa JWT)")

# daftar router
app.include_router(create_router, prefix="/users", tags=["users"])
app.include_router(read_router,   prefix="/users", tags=["users"])
app.include_router(update_router, prefix="/users", tags=["users"])
app.include_router(delete_router, prefix="/users", tags=["users"])

@app.get("/", tags=["health"])
def root():
    return {"status": "ok"}