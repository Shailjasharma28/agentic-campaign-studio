
from database.models import LLMUsage, MediaUsage
from database.database import SessionLocal

# COST TRACKER CLASS

class CostTracker:

    def __init__(self,campaign_run_id):
        
        self.campaign_run_id = campaign_run_id

    # =====================================
    # RECORD LLM USAGE
    # =====================================

    def record_llm(
            self, component, model, input_tokens, output_tokens,
            total_tokens, cost
    ):
    
        db = SessionLocal()
        try:
            usage = LLMUsage( 
                campaign_run_id=self.campaign_run_id,
                component = component,
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                cost=cost

            )

            db.add(usage)
            db.commit()
            db.refresh(usage)

            print("\n========== LLM USAGE SAVED ==========")
            print("Usage ID:", usage.id)
            print("Campaign:", self.campaign_run_id)
            print("Component:", component)
            print("Model:", model)
            print("Input tokens:", input_tokens)
            print("Output tokens:", output_tokens)
            print("Total tokens:", total_tokens)
            print("Cost:", cost)

            return usage
        finally:
            db.close()


    # =====================================
    # RECORD IMAGE/VIDEO MEDIA USAGE
    # =====================================

    def record_media(self, media_type, model, cost, duration_seconds=None):
        db=SessionLocal()
        try:
            usage = MediaUsage(
                campaign_run_id=self.campaign_run_id,
                media_type=media_type,
                model=model,
                duration_seconds=duration_seconds,
                cost=cost

            )

            db.add(usage)
            db.commit()
            db.refresh(usage)

            print("\n========== MEDIA USAGE SAVED ==========")
            print("Usage ID:", usage.id)
            print("Campaign:", self.campaign_run_id)
            print("Media Type:", media_type)
            print("Model:", model)
            print("Duration:", duration_seconds)
            print("Cost:", cost)

            return usage

        finally:
            db.close()
    

