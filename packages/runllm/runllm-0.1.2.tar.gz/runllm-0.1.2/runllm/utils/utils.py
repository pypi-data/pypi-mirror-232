def format_header_for_print(header: str) -> str:
    """Used to print the header of a section in "describe()" with a consistent length.

    Sandwiches the "header" argument with a repeating sequence of "="s. Eg.

    ============================ "Embed" Primitive ==========================
    [       prefix len          ]
    [                              full_len                                   ]
    """
    prefix_len = 20
    full_len = 80
    return f"{'=' * prefix_len} {header} {'=' * max(0, full_len - prefix_len - len(header))}"
