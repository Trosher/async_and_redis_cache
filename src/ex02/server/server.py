from asyncio import run as runasync
from asyncio import create_task
from logger.logger import Loger, logger
from task_obj.task_obj import task, url_list

from uuid import uuid4

from urllib.parse import urlparse

from aiohttp import ClientSession
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from uvicorn import run

import redis.asyncio as redis

app = FastAPI()
tasks = {}

@Loger
async def create_redis():
    redis_client = await redis.Redis()
    await redis_client.ping()
    return redis_client

@Loger
async def cash_redis(url, redis_client):
    try:
        domen = urlparse(url).netloc
        cache = await redis_client.get(domen)
        if cache is None:
            await redis_client.set(domen, 1)
        else:
            await redis_client.set(domen, int(cache)+1)
        return await redis_client.get(url)
    except Exception as e:
        logger.warning(e)
    
@Loger
async def request_sending(task_id: str, url: str):
    redis_client = await create_redis()
    cache = int(await cash_redis(url, redis_client))
    if cache is None:
        async with ClientSession() as session:
            try:
                async with session.get(url) as response:
                    tasks[task_id].result.append(response.status)
                    tasks[task_id].result_url.append(url)
                    await redis_client.set(url, response.status)
            except Exception as e:
                logger.warning(e)
                tasks[task_id].result.append(404)
                tasks[task_id].result_url.append(url)
                await redis_client.set(url, 404)
    else:
        tasks[task_id].result.append(cache)
        tasks[task_id].result_url.append(url)

@Loger
async def process_urls(task_id: str, urls: list[str]):
    ts = []
    for url in urls:
       ts.append(create_task(request_sending(task_id, url)))
    for t in ts:
        await t
    tasks[task_id].status = "ready"

@app.post("/api/v1/tasks/")
@Loger
def executing_request_by_specified_url(urls:url_list):
    task_id = str(uuid4())
    tasks[task_id] = task(id=task_id, status="running", result=[], result_url=[])
    runasync(process_urls(task_id, urls.urls))
    return JSONResponse(content=jsonable_encoder(tasks[task_id]),status_code=201)

@app.get("/api/v1/tasks/{received_task_id}")
@Loger
def get_status_task(received_task_id):
    return JSONResponse(content=jsonable_encoder(tasks[received_task_id]), status_code=200)

if __name__ == "__main__":
    logger.info("Starting server")
    run(app, host="127.0.0.1", port=8888, log_level="info")