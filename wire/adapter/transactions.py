import contextlib
import json
import typing

import aio_pika
from fastapi import APIRouter, FastAPI, HTTPException, Request
from ns.tdata import format, rabbit

router = APIRouter()


@router.post("/")
async def accept(request: Request):
    sender = request.state.lifespan[__spec__.name]["sender"]
    try:
        data = await request.json()
        td: format.proto.TransactionDataRequest = format.convert(data)
        await sender.send(td)
    except (
        json.decoder.JSONDecodeError,
        format.json_format.ParseError,
        AttributeError,
        AssertionError,
    ) as err:
        raise HTTPException(status_code=400, detail=str(err))
    except aio_pika.AMQPException:
        raise HTTPException(status_code=503)
    return "OK"


@contextlib.asynccontextmanager
async def lifespan(_: FastAPI) -> typing.AsyncIterator[dict]:
    async with rabbit.component(__spec__.name) as sender:
        yield {"lifespan": {__spec__.name: {"sender": sender}}}
