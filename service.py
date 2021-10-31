from asyncio import gather, get_event_loop, set_event_loop, new_event_loop
from itertools import chain
from logging import getLogger
from os import getenv
from random import randint
from time import sleep

import httpx
from flask import Flask, jsonify, make_response

app = Flask(__name__)

logger = getLogger(__name__)

SOURCES_PORT = getenv("SOURCES_PORT")


async def get_source(source_id):
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                f"http://127.0.0.1:{SOURCES_PORT}/source/{source_id}", timeout=2
            )
            data = resp.json()
        except httpx.ReadTimeout:
            data = []
        except Exception as e:
            logger.error(e)
            data = []
    return data


@app.route("/")
def root():
    try:
        loop = get_event_loop()
    except RuntimeError:
        loop = new_event_loop()
        set_event_loop(loop)
    result = loop.run_until_complete(gather(*[get_source(i) for i in range(1, 4)]))

    return jsonify(
        sorted(list(chain.from_iterable(result)), key=lambda item: item["id"])
    )


@app.route("/source/<source_id>")
def source(source_id):
    with open(f"sources/source{source_id}.json", "rt") as source_file:
        data = source_file.read()
    sleep(randint(0, 3))
    response = make_response(data)
    response.headers["Content-Type"] = "application/json"
    return response
