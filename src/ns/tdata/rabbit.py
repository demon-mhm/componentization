import contextlib
import os
import sys

import aio_pika

from ns.component import AsyncStateRequest

from . import events
from .integration_pb2 import TransactionDataRequest


@contextlib.asynccontextmanager
async def exchange(tag: str):
    connection = await aio_pika.connect_robust(
        os.getenv("RABBITMQ_DSN"), client_properties={"connection_name": tag}
    )
    async with connection:
        channel = await connection.channel()
        exchange = await channel.declare_exchange(**events.exchange)
        yield exchange


async def send(td: TransactionDataRequest, exchange: aio_pika.abc.AbstractExchange):
    await exchange.publish(
        aio_pika.Message(td.SerializeToString()),
        routing_key=events.route(td),
    )


component = AsyncStateRequest(sys.modules[__name__], exchange=exchange)
