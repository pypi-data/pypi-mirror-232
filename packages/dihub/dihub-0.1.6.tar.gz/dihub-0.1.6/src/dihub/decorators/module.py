from typing import List, Any, Callable, Union, Optional

from src.dihub.__internal.helpers import AnnotationOf
from src.dihub.constants import _MODULE_ANNOTATIONS
from src.dihub.types import Value, Providers, Modules, ModuleAnnotation


def __get_list_defaults(arr: List[Any]) -> List[Any]:
    if arr is None:
        return []

    return arr


def __process_module_decorator(cls: Value, imports: Modules, providers: Providers) -> Value:
    AnnotationOf(cls).set(_MODULE_ANNOTATIONS, ModuleAnnotation(
        imports=imports,
        providers=providers))

    return cls


def module(cls: Optional[Value] = None, /, *, imports: Optional[Modules] = None, providers: Optional[Providers] = None) -> Union[
    Callable[[Value], Value], Value]:
    def wrapper(_cls: Value) -> Value:
        return __process_module_decorator(_cls, __get_list_defaults(imports), __get_list_defaults(providers))

    if cls is None:
        return wrapper

    return wrapper(cls)
