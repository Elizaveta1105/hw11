import redis.asyncio as redis
from fastapi import FastAPI

from src.conf.config import config
from src.routes import contacts, auth, user
from fastapi_limiter import FastAPILimiter
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.include_router(auth.router, prefix='/api')
app.include_router(contacts.router, prefix='/api')
app.include_router(user.router, prefix='/api')


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    r = await redis.Redis(host=config.REDIS_DOMAIN, port=config.REDIS_PORT, db=0, encoding="utf-8",
                          decode_responses=True)
    await FastAPILimiter.init(r)


@app.get("/")
def read_root():
    return {"message": "Hello World"}
