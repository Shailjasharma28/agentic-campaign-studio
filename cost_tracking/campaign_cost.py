from decimal import Decimal
from database.database import SessionLocal
from database.models import LLMUsage, MediaUsage

def get_campaign_cost(campaign_run_id:int):
    db = SessionLocal()

    try:
        llm_cost = (
            db.query(LLMUsage.cost).filter(LLMUsage.campaign_run_id==campaign_run_id)
            .all()
        )

        media_cost = (db.query(MediaUsage.cost)
                      .filter(MediaUsage.campaign_run_id==campaign_run_id)
                      .all())


        total_llm_cost = sum(
            (row[0] for row in media_cost), Decimal("0")
        )

        total_media_cost = sum(
            (row[0] for row in media_cost),
            Decimal("0")
        )
        # Total campaign cost
        total_cost = total_llm_cost + total_media_cost

        # Cost Percentages
        llm_percentage = (
            total_llm_cost / total_cost * Decimal("100") if total_cost else Decimal("0")
        )

        media_percentage = ( 
            total_media_cost / total_cost * Decimal("100")
            if total_cost else Decimal("0")

        )

        return{
            "llm_cost": total_llm_cost,
            "media_cost": total_media_cost,
            "total_cost": total_cost,
            "llm_percentage": llm_percentage,
            "media_percentage": media_percentage}

    finally:
        db.close()