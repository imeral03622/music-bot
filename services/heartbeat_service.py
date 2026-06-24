import asyncio
import json
import os
import time

STATUS_FILE = "data/status.json"


def save_status(
    last_seen=None,
    clean_shutdown=False
):

    os.makedirs(
        "data",
        exist_ok=True
    )

    data = {
        "last_seen": (
            last_seen
            if last_seen is not None
            else int(time.time())
        ),
        "clean_shutdown": clean_shutdown
    }

    with open(
        STATUS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4
        )


def load_status():

    if not os.path.exists(
        STATUS_FILE
    ):
        return None

    with open(
        STATUS_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


async def heartbeat_loop():

    while True:

        save_status(
            clean_shutdown=False
        )

        await asyncio.sleep(60)