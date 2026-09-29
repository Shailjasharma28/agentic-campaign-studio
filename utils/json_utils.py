import json
import re

def extract_json(raw:str):
    """
    Extracts valid JSON from LLM Output.
    Handles 
    -plain JSON
    -JSON inside markdown code fences
    - extra text before/after JSON
    - multi-line JSON
    """

    if not isinstance(raw, str):
        raw = raw.content

    raw = raw.strip()

    # Remove markdown code fences
    raw = re.sub(r"```json\s*", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"```\s*", "", raw)

    raw = raw.strip()

    print("\n========== CLEANED LLM OUTPUT ==========")
    print(raw)
    print("=========================================")

    
    # First Attempt: Direct JSON load
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    object_match = re.search(r"\{.*\}", raw, re.DOTALL)

    if object_match:
        json_text = object_match.group()

        json_text = re.sub(
        r'(:\s*)\\"',
        r'\1"',
        json_text
    )

        json_text = re.sub(
        r'\\"(\s*[,}])',
        r'"\1',
        json_text
    )
        try:
            return json.loads(json_text)
        
        except json.JSONDecodeError as e:
            print("\n========== JSON PARSING FAILED ==========")
            print(e)
            print("\nJSON AFTER CLEANING:")
            print(json_text)
            print("=========================================")
            print("JSON object found but invalid.")
            print(e)

        
    raise ValueError("LLM did not return any JSON")