from fastapi import FastAPI
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from presentation.api.interview_ready_controller import interview_router

from infrastructure.database.mongo_connection import mongo_connection
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await mongo_connection.connect()
    yield
    await mongo_connection.disconnect()


app = FastAPI(
    title="Interview Ready Service",
    description="Microservicio para simulación de entrevistas de comportamiento",
    version="1.0.0",
    lifespan=lifespan
)


app.include_router(
    router=interview_router,
    prefix="/api/v1",
    
)

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the Interview Ready Service API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8003, reload=True)
