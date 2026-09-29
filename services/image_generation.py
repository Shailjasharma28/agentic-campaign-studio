import os
import base64
import time
from dotenv import load_dotenv
from runwayml import RunwayML, TaskFailedError 

from cost_tracking.media_cost import calculate_image_cost
from cost_tracking.context import CostTracker
from utils.retry_logic import is_retryable_error, wait_before_retry
from utils.fallback import create_placeholder_image
from utils.logger import logger

load_dotenv()

runway_client = RunwayML(
    api_key = os.getenv("RUNWAYML_API_SECRET")

)

def generate_image(prompt:str, output_path:str, campaign_run_id:int):
    model = "gen4_image"
    ratio = "1024:1024"
    

    max_retries = 3

    for attempt in range(max_retries):
        try:
            response = runway_client.text_to_image.create(
                model=model,
                prompt_text=prompt,
                ratio=ratio,   
            )

            # Waiting for Runway task to finish
            result = response.wait_for_task_output()

            break

        except Exception as e:
            if not is_retryable_error(e):
                logger.exception(
                    "Image generation failed with non-retryable error"
                  
                )

                fallback_path = create_placeholder_image(
                    output_path
                )

                logger.warning("Using placeholder image fallback.")

                return ( fallback_path, "fallback", "local_fallback")
            

            if attempt == max_retries -1:
                logger.error(
                    "Image generation failed after %s attempts.",
                    max_retries
                )

                fallback_path = create_placeholder_image(
                    output_path
                )

                logger.warning("Using Placeholder image fallback.")

                return (
                    fallback_path, 
                    "fallback",
                    "local_fallback"
                )
            wait_before_retry(attempt)
            
    # -----------------------------------------
    # DOWNLOAD GENERATED IMAGE
    # -----------------------------------------
    
    image_url = result.output[0]

    try:
        import requests
        image_response = requests.get(image_url, timeout=60)

        image_response.raise_for_status()

        with open(output_path, "wb") as f:
            f.write(image_response.content)


    except Exception as e:
        logger.error(
            "Failed to download generated image: %s",
            type(e).__name__
        )

        fallback_path = create_placeholder_image(
            output_path
        )

        return (
                fallback_path,
                "fallback",
                "local_fallback"
        )


    
    
    # -------------------------
    # CALCULATE COST
    # -------------------------
    
    cost = calculate_image_cost(
    model=model,
    size=ratio,
    
)

    # -------------------------
    # SAVE MEDIA USAGE
    # -------------------------

    tracker = CostTracker(campaign_run_id=campaign_run_id)

    tracker.record_media(media_type="image",
                         model=model, 
                         cost=cost)

    
    return (output_path, "generated", "Runway")