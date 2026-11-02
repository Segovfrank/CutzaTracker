def filter_arg(op: str, prop: str, arg_value: int | float | str) -> dict:
    return {
        "op": op,
        "args": [
            {
                "property": prop
            },
            arg_value
        ]
    }