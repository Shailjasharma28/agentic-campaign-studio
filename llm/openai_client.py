import os
from dotenv import load_dotenv
from openai import OpenAI
from cost_tracking.context import CostTracker
from cost_tracking.calculate_llm_cost import calculate_llm_cost
from utils.retry_logic import is_retryable_error, wait_before_retry
from utils.validation import validate_output
from utils.logger import logger

# Loading API keys from environment variables:
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)


# COST TRACKING HELPER

def _track_llm_usage(
        response, model, component, campaign_run_id
):
    input_tokens = response.usage.prompt_tokens
    output_tokens = response.usage.completion_tokens
    total_tokens = response.usage.total_tokens

    cost = calculate_llm_cost(model=model, input_tokens=input_tokens,
                              output_tokens=output_tokens)
    
    if campaign_run_id is not None:
        
        tracker = CostTracker(campaign_run_id=campaign_run_id)

        tracker.record_llm(component=component, model=model,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    total_tokens=total_tokens,cost=cost)

    else:
        logger.warning(
            "No campaign_run_id provided. "
            "LLM usage was not recorded."
        )
            
#=====================================
# CALLING LLM
#=====================================

def call_llm(prompt, model="gpt-4.1-mini", component=None,
             campaign_run_id=None):
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model, 
                messages=[{"role":"user", "content":prompt}],
                timeout=60)
            break

        except Exception as e:

            if not is_retryable_error(e):
                raise

            if attempt == max_retries -1:
                raise

            wait_before_retry(attempt)

    _track_llm_usage(
        response=response,
        model=model,
        component=component,
        campaign_run_id=campaign_run_id
    )

    logger.info(
        "LLM request completed: component=%s, model=%s",
        component, 
        model,
    )

    return response.choices[0].message.content


#==========================================
# LLM FUNCTION FOR STRUCTURED OUTPUT SCHEMA
#===========================================

def call_llm_structured(prompt, schema, model="gpt-4.1-mini", 
                        component=None, campaign_run_id=None):

    
    max_retries = 3 

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.parse(
                    model=model,
                    messages=[{"role":"user", "content":prompt}],
                    response_format=schema,
                    timeout=60)
            break

        except Exception as e:

            if not is_retryable_error(e):
                raise
            if attempt == max_retries -1:
                raise

            wait_before_retry(attempt)

    _track_llm_usage(
        response=response,
        model=model,
        component=component,
        campaign_run_id=campaign_run_id
    )
    
    parsed_output = response.choices[0].message.parsed
    validated_output = validate_output(parsed_output, schema)
    logger.info(
            "Structured LLM request completed: component=%s, model=%s",
            component, 
            model,
        )

    return validated_output