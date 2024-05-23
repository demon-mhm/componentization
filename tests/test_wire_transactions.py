from unittest.mock import patch

from starlette.testclient import TestClient

from ns.tdata import format, rabbit
from wire.adapter.main import app


def test_transactions():
    td_minimal = {
        "View": {
            "_StoreId": "test",
            "_transactionKind": "test",
        },
    }
    td_minimal_proto = format.convert(td_minimal)
    with (
        patch.object(rabbit.events, "route", wraps=rabbit.events.route) as route,
        TestClient(app=app) as client,
    ):
        response = client.post("/")
        assert response.status_code == 400
        response = client.post("/", json="not-json")
        assert response.status_code == 400
        response = client.post("/", json={"bad": "json"})
        assert response.status_code == 400
        response = client.post("/", json=td_minimal)
        assert response.status_code == 200, response.json()
        route.assert_called_with(td_minimal_proto)
