from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from routers import v1_router

from sqlalchemy import create_engine


# engine = create_engine('postgresql://your_username:your_password@localhost:5432/your_database')
app = FastAPI(
    title="Book Library App",
    description="Приложение для ШАД",
    version="0.0.1",
    default_response_class=ORJSONResponse,
    responses={404: {"description": "Not Found!"}}
)

app.include_router(v1_router)


@asynccontextmanager
async def lifespan(app: FastAPI):
    ic("I am ok!")
    global_init()
    await create_db_and_tables()
    yield
    
