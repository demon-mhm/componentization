from . import integration_pb2

exchange = {"name": "tdata", "type": "topic", "durable": True}


def route(
    td: integration_pb2.TransactionDataRequest | None = None,
    store_id: str | None = None,
    transaction_kind: str | None = None,
) -> str:
    assert td is not None or all((store_id, transaction_kind))
    store_id = store_id or str(td.View._StoreId).removeprefix("643")
    transaction_kind = transaction_kind or td.View._transactionKind
    return f"tdata.{store_id}.{transaction_kind}"
