from typing import Optional, Any, Literal
from dataclasses import dataclass
from pydantic import BaseModel
from schema_agents.agent_input_schemas import (BrandProfile, 
CampaignContext,
CampaignOutput, 
EvaluationResult)


class WorkflowState(BaseModel):
    user_input: Optional[str]=None
    platform:Optional[str]=None

    # brand
    brand: Optional[BrandProfile]=None
    # DB Brand Profile ID
    brand_profile_id: Optional[int]=None



    # Campaign-specific context
    campaign_context: Optional[CampaignContext]=None

    # brand evaluation
    brand_context_evaluation: Optional[EvaluationResult]=None

    # campaign
    campaign: Optional[CampaignOutput]=None
    # DB Campaign Run ID
    campaign_run_id:Optional[int]=None

    # Evaluation Result
    campaign_evaluation: Optional[EvaluationResult] = None

    # Revision Counter
    revision_count: int = 0

    # Revision target
    revision_target: Optional[str]=None

    # Human Approval/ Feedback
    human_decision:Optional[Literal["approve", "revise"]] = None
    human_feedback: Optional[str] = None

    

    # Image and Video Path
    image_path: Optional[str]=None
    video_path: Optional[str]=None

# AGENT CONTEXT
@dataclass
class AgentContext:
        brand_context_agent: Any
        campaign_agent:Any
        evaluation_agent: Any
        revision_agent: Any
        system_evaluation_agent:Any
