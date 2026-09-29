import os
import time
import base64
from dotenv import load_dotenv
from runwayml import RunwayML, TaskFailedError, TaskTimeoutError
from cost_tracking.context import CostTracker
from cost_tracking.media_cost import calculate_video_cost
from utils.retry_logic import is_retryable_error, wait_before_retry
from utils.logger import logger

load_dotenv()

runway_client = RunwayML(
    api_key = os.getenv("RUNWAYML_API_SECRET")

)

# VIDEO MODEL CONFIG
VIDEO_MODEL = "Runway Multi-Shot Recipe"


def generate_video(
        campaign,
        video_shots,
        output_path:str,
        campaign_run_id:int,
     
):

    size = "1280:720"
    seconds= 10
    max_retries = 3

    # -----------------------------------------
    # CREATE VIDEO JOB
    # -----------------------------------------


    for attempt in range(max_retries):
        try:

            total_duration = sum(
                shot["duration"] for shot in video_shots
            )

            if total_duration != seconds:
                raise ValueError(
                    f"Video shot durations must sum to {seconds} seconds."
                    f"but received {total_duration} seconds."
                )

            
            video_task = runway_client.recipes.multi_shot_video(
            version="2026-06",
            mode="custom",
            shots=video_shots,
            duration=seconds,
            ratio=size, 
            audio=True,
            )

            break

        except Exception as e:
            if not is_retryable_error(e):
                logger.exception(
                    "Video job creation failed"
                    
                )
                return None, "failed", VIDEO_MODEL

            if attempt == max_retries -1:
                logger.error(
                    "Video job creation failed after %s attempts.",
                    max_retries
                )

                return None, "failed",  VIDEO_MODEL

            wait_before_retry(attempt)

    logger.info(
            "Runway video generation job created: %s",
            video_task.id
        )


    # -----------------------------------------
    # WAIT FOR COMPLETION
    # -----------------------------------------

    try:

        result = video_task.wait_for_task_output(
            timeout=600
        )

    except TaskFailedError as e:
        logger.error(
            "Runway video generation failed: %s",
            e.task_details
        )

        return None, "failed",  VIDEO_MODEL

    except TaskTimeoutError:

        logger.error(
            "Runway video generation timed out after 10 minutes."
        )

        return None, "failed",  VIDEO_MODEL


    except Exception as e:
        logger.error(
            "Unexpected Runway video error: %s",
            type(e).__name__

        )

        return None, "failed",  VIDEO_MODEL

    logger.info(
        "Runway video generation completed."
    )


    # -----------------------------------------
    # GET GENERATED VIDEO URL
    # -----------------------------------------

    try:

        video_url = result.output[0]

        logger.info(
            "Runway video output received."
        )

    except(AttributeError, IndexError):

        logger.error(
            "Runway returned no video output."
        )

        return None, "failed",  VIDEO_MODEL



    # -----------------------------------------
    # DOWNLOAD VIDEO
    # -----------------------------------------
        
    for attempt in range(max_retries):
        try:
            import requests

            response = requests.get(video_url, 
                                    timeout=120)

            response.raise_for_status()

            with open(output_path, "wb") as f:
                f.write(response.content)

            break
            

        except Exception as e:
            if not is_retryable_error(e):
                logger.error(
                    "Video download failed: %s",
                    type(e).__name__)
                return None, "failed",  VIDEO_MODEL
                

            if attempt == max_retries -1 :
                logger.error(
                    "Video status retrieval failed after %s attempts:",
                    max_retries
                )
                return None, "failed",  VIDEO_MODEL

            wait_before_retry(attempt)
        

    logger.info("Video saved successfully: %s",
                output_path)


    # -------------------------
    # CALCULATE COST
    # -------------------------
    
    cost = calculate_video_cost(
    seconds=seconds,
    size=size,
    )

    # -------------------------
    # SAVE MEDIA USAGE
    # -------------------------
    
    tracker = CostTracker(campaign_run_id=campaign_run_id)

    tracker.record_media(media_type="video",
                            model= VIDEO_MODEL, 
                            cost=cost,
                            duration_seconds=seconds)

    return output_path, "generated",  VIDEO_MODEL


# VIDEO PROMPT HELPER

def build_video_shots(campaign):

    shots=[]

    for scene in campaign.video_scenes:

        prompt_parts=[]

        if scene.visual:
            prompt_parts.append(f"Visual:{scene.visual}")

        if scene.camera:
            prompt_parts.append(f"Camers: {scene.camera}")

        if scene.text:
            prompt_parts.append(f"On-screen text: {scene.text}")

        shot_prompt = ". ".join(prompt_parts)

        if len(shot_prompt) > 512:
            raise ValueError(
                f"Video scene prompt is too long: "
                f"{len(shot_prompt)} characters."
                f"Runway allows 512 character per shot."
            )

        shots.append({
            "prompt": shot_prompt,
            "duration": scene.duration}
        )

    return shots