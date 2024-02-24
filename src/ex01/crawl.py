from ast import Await
from server.logger.logger import Loger, logger
from argparse import ArgumentParser
from pydantic import AnyHttpUrl
from aiohttp import ClientSession
import asyncio

@Loger
def createArgParser():
     parser = ArgumentParser(prog="ServerClient", 
                             description="At startup it accepts a list of url's to be sent to\
                                          the server for processing",
                             epilog="The client will not be started without url arguments")
     parser.add_argument("url_list", nargs = '+', type = AnyHttpUrl,
                         help = "Argument url list")
     return parser

@Loger
async def query_task(session, task_id):
    while True:
        async with session.get(f"http://localhost:8888/api/v1/tasks/{task_id}") as response:
            task = await response.json()
            if task["status"] == "ready":
                break
            else:
                await asyncio.sleep(1)
    return task

async def print_results(task):
    for code, url in zip(task["result"], task["result_url"]):
        print(f"{code}\t{url}")

@Loger
async def start_client(url_list):
    async with ClientSession() as session:
        async with session.post("http://localhost:8888/api/v1/tasks/", json={"urls":url_list}) as response:
            task_id = (await response.json())["id"]
            task = await query_task(session, task_id)
            await print_results(task)

@Loger
def main():
    parser = createArgParser()
    args = [str(param) for param in parser.parse_args().url_list]
    asyncio.run(start_client(args))
    
if __name__ == "__main__":
    logger.info("Starting client")
    main()