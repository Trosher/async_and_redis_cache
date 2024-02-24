from asyncio import run as runasync
from asyncio import create_task
from re import T
from tkinter import E
from logger.logger import Loger, logger
from task_obj.task_obj import task, url_list

from uuid import uuid4

from aiohttp import ClientSession
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from uvicorn import run

app = FastAPI()
tasks = {}

@Loger
async def request_sending(task_id: str, url: str):
    async with ClientSession() as session:
        try:
            async with session.get(url) as response:
                tasks[task_id].result.append(response.status)
                tasks[task_id].result_url.append(url)
        except Exception as e:
            print(e, url)
            tasks[task_id].result.append(404)
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