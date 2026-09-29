def validate_output(output, schema):
    if output is None:
        raise ValueError("LLM returned no structured output.")

    if not isinstance(output, schema):
        raise ValueError(
            f"Invalid LLM output type. "
            f"Expected {schema.__name__}, "
            f"got {type(output).__name__}"
        )

    return output