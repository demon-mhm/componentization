import contextlib
import functools
import inspect
import types
import typing


class AsyncStateProxy:
    """Wrapper class for module-based components."""

    name: str
    _interface: dict[str, typing.Callable]
    _members: dict[str, typing.Any]

    def __init__(
        self,
        module: types.ModuleType,
        **dependencies: dict[str, typing.Any],
    ):
        self._members = {
            key: functools.partial(
                fn,
                **{
                    key: dep
                    for key, dep in dependencies.items()
                    if key in inspect.signature(fn).parameters
                },
            )
            for key, fn in inspect.getmembers(module)
            if inspect.isfunction(fn)
            and any(d in inspect.signature(fn).parameters for d in dependencies)
        }
        # expose dependencies as state attributes
        for key, value in dependencies.items():
            setattr(self, key, value)

    def __getattr__(self, key: typing.Any) -> typing.Any:
        return self._members[key]


class AsyncStateRequest:
    _module: types.ModuleType
    _dependencies: dict[str, typing.Callable[[str], typing.Any]]

    def __init__(self, module: types.ModuleType, **dependencies):
        self._module = module
        self._dependencies = dependencies

    @contextlib.asynccontextmanager
    async def __call__(self, name: str) -> typing.AsyncIterator[AsyncStateProxy]:
        assert self._module.__spec__
        spec = ":".join([name, self._module.__spec__.name])
        deps = {}
        async with contextlib.AsyncExitStack() as stack:
            for key, dep in self._dependencies.items():
                if isinstance(dep, typing.Callable):
                    dep = dep(spec)
                    if isinstance(dep, typing.AsyncContextManager):
                        dep = await stack.enter_async_context(dep)
                    elif isinstance(dep, typing.Awaitable):
                        dep = await dep
                deps.update({key: dep})
            yield AsyncStateProxy(self._module, **deps)
