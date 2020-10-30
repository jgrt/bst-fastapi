import asyncio
from aiohttp import ClientSession
import time
import json


async def fetch(url):
    async with ClientSession() as session:
        async with session.get(url) as response:
            return await response.read()


async def run(keys):
    tasks = [fetch(f"http://localhost:4859/keys/{key}") for key in keys]

    start = time.time()
    await asyncio.gather(*tasks)
    end = time.time()
    return end - start


async def benchmark():
    num_requests = [1, 10, 100, 1000, 10000]
    num_tries = 1
    results = []
    for num_request in num_requests:
        keys = list(range(num_request))
        time_taken = []
        for num_try in range(num_tries):
            time_taken_ = await run(keys=keys)
            time_taken.append(time_taken_)

        results.append(time_taken)
    resp = list(zip(results, num_requests))
    t = time.localtime()
    ctime = time.strftime("%H:%M:%S", t)
    with open(f"benchmark_{ctime}.json", "w") as fn:
        json.dump(resp, fn)
    return resp


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(benchmark())
    loop.run_until_complete(future)
