import contextlib

from fastapi import FastAPI

from . import transactions


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    async with contextlib.AsyncExitStack() as stack:
        agg = {}
        for mod in (transactions,):
            resources = await stack.enter_async_context(mod.lifespan(app))
            agg.setdefault("lifespan", {}).update(resources["lifespan"])
        yield agg


app = FastAPI(lifespan=lifespan)
app.include_router(transactions.router)
