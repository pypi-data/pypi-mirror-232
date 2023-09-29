from typing import Callable, List, Iterable, Any


def filtered(func: Callable, iterable: Iterable):
    return type(iterable)(filter(func, iterable))


def select_items(items: Iterable, inverse: bool = False, **kwargs) -> List:
    res = []
    if kwargs:
        for item in items:
            selected = True
            for k, v in kwargs.items():
                item_v = item.get(k) if hasattr(item, "get") else getattr(item, k, None)
                if (item_v != v and not inverse) or (item_v == v and inverse):
                    selected = False
                    break
            if selected:
                res.append(item)
    return res


def select_item(items: Iterable, inverse: bool = False, **kwargs) -> Any | None:
    res = select_items(items, inverse, **kwargs)
    if res:
        return res[0]
