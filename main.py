from fastapi import FastAPI
import logging
from db_config import Database

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

app = FastAPI()


@app.get("/keys/{key}")
async def read_item(key: int):
    conn = Database()
    res = conn.insert(start=True, value=key)
    logger.info(res)
    return {"key": key}
