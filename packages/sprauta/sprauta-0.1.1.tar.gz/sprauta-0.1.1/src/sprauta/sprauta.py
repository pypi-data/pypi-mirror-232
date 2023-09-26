"""Sprauta."""

import contextlib
import inspect
import sys
from typing import Callable, ContextManager, Dict, List, Optional, TypeVar

from typing_extensions import Annotated, TypeAlias, get_args, get_origin

T = TypeVar("T")

DependencyOverwritesT: TypeAlias = Dict[Callable[..., T], Callable[..., T]]


class Depends:
    def __init__(self, dependency: Callable[..., T], *, use_cache: bool = True):
        self.dependency = dependency
        self.use_cache = use_cache


def resolve_dependency(
    param: inspect.Parameter, *, type_dependencies: Dict[type, Depends]
) -> Optional[Depends]:
    annotation = param.annotation

    if get_origin(param.annotation) is Annotated:
        annotation, *metadata = get_args(annotation)

        for meta in metadata:
            if isinstance(meta, Depends):
                return meta

    return type_dependencies.get(annotation)


def _call(
    func: Callable[..., T],
    *,
    cache: Dict,
    overwrites: Dict,
    type_dependencies: Dict[type, Depends],
    resources: list,
) -> T:
    """Call func with dependency injection."""

    args = []
    kwargs = {}

    for param in inspect.signature(func).parameters.values():
        dep = resolve_dependency(param, type_dependencies=type_dependencies)

        if dep is None:
            msg = "unresolved dependency"
            raise RuntimeError(msg)

        dep_func = overwrites.get(dep.dependency, dep.dependency)

        if dep.use_cache and dep_func in cache:
            value = cache[dep_func]
        else:
            if inspect.isgeneratorfunction(dep_func):
                resource = _call(
                    contextlib.contextmanager(dep_func),
                    cache=cache,
                    overwrites=overwrites,
                    type_dependencies=type_dependencies,
                    resources=resources,
                )
                value = resource.__enter__()
                resources.append(resource)
            else:
                value = _call(
                    dep_func,
                    cache=cache,
                    overwrites=overwrites,
                    type_dependencies=type_dependencies,
                    resources=resources,
                )

            if dep.use_cache:
                cache[dep_func] = value

        if param.kind == inspect.Parameter.POSITIONAL_ONLY:
            args.append(value)

        else:
            kwargs[param.name] = value

    return func(*args, **kwargs)


def call(
    func: Callable[..., T],
    *,
    overwrites: Optional[Dict] = None,
    type_dependencies: Optional[Dict[type, Depends]] = None,
) -> T:
    """Call func after resolving its dependencies."""

    resources: List[ContextManager] = []

    try:
        value = _call(
            func,
            cache={},
            overwrites=overwrites or {},
            type_dependencies=type_dependencies or {},
            resources=resources,
        )

        while resources:
            resources.pop().__exit__(None, None, None)

        return value

    except BaseException:
        exc_info = sys.exc_info()

        while resources:
            with contextlib.suppress(BaseException):
                resources.pop().__exit__(*exc_info)
        raise
