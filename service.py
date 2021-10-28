from asyncio import sleep, gather, get_event_loop, set_event_loop,  new_event_loop
from itertools import chain
import json
from logging import getLogger
from random import randint

from flask import Flask, jsonify

app = Flask(__name__)

logger = getLogger(__name__)


async def read_file(file_name, timeout=0):
    if timeout >= 2:
        raise Exception
    with open(file_name, "rt") as source_file:
        data = json.load(source_file)
    await sleep(timeout)
    return data


async def get_source(file_name):
    try:
        data = await read_file(file_name, randint(0, 3))
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
    result = loop.run_until_complete(
        gather(
            *[get_source(f"sources/source{i}.json") for i in range(1, 4)]
        )
    )
    return jsonify(sorted(list(chain.from_iterable(result)), key=lambda item: item["id"]))
