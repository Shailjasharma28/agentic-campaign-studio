MODEL_PRICING = {
    "gpt-4.1-mini": {
        "input": 0.40,
        "output": 1.60,
    }
}

def calculate_llm_cost(model, input_tokens, output_tokens):

    pricing = MODEL_PRICING.get(model)

    if pricing is None:
        raise ValueError(
            f"No pricing information available for model: {model}"
        )

    input_cost = ( input_tokens/ 1_000_000) * pricing["input"]

    output_cost = ( output_tokens /1_000_000) * pricing["output"]

    total_cost = input_cost + output_cost
    return total_cost