from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Annotated
import datetime

class BaseSchema(BaseModel):
    model_config={"arbitrary_types_allowed":True,
                  "from_attributes": True,
        "populate_by_name": True,
        "json_encoders": {
            list: lambda v: v,   # prevent warnings for list fields
        }
    }

# ============================
# BRAND PROFILE
# ============================

class BrandProfile(BaseSchema):
    brand_name: Optional[str]=None

    # Brand Identity
    niche: Optional[str]=None
    positioning:Optional[str]=None
    products: Optional[List[str]]=None

    target_audience:Optional[str]=None

    # Markets & languages
    default_markets: Optional[List[str]] = None
    default_languages: Optional[List[str]] = None

    # Brand Voice
    tone_of_voice: Optional[str]=None

    # Visual identity
    brand_colors: Optional[List[str]]=None
    style_keywords: Optional[List[str]]=None


#============ Campaign Context=============

class CampaignContext(BaseSchema):
    age_group:Optional[str]=None
    gender: Optional[str] = None
    geography:Optional[str]=None
    language: Optional[str]=None
    interests:Optional[List[str]]=None
    cultural_context:Optional[str]=None


class BrandContextResult(BaseSchema):
    brand_name: Optional[str]=None
    brand_profile:Optional[BrandProfile]=None
    campaign_context:Optional[CampaignContext]=None
    missing_fields:List[str]= Field(default_factory=list)
    questions: List[str]=Field(default_factory=list)


#============ Campaign Output==============
class CampaignOutput(BaseSchema):
    # PLATFORM
    platform: Optional[str]=None

    # ================================
    # CONTENT IDEAS
    # ================================

    idea_title: Optional[str] =None
    idea_angle:Optional[str]=None
    idea_objective: Optional[str]=None

    
    # ================================
    # GENERATED CONTENT
    # ================================

    hook:Optional[str]=None
    caption:Optional[str]=None
    cta: Optional[str]=None
    hashtags: Optional[List[str]]=None


    # ================================
    # IMAGE 
    # ================================

    image_prompt:Optional[str]=None
    image_style:Optional[str]=None
    image_colors: Optional[List[str]]=None
    image_lighting: Optional[str]=None
    image_composition:Optional[str]=None
    image_mood:Optional[str]=None
    image_aspect_ratio:Optional[str]=None

    # VIDEO SCENES
    class VideoScene(BaseModel):
        visual: Optional[str] = None
        camera: Optional[str] = None
        text: Optional[str] = None
        duration: Optional[int] = Field(default=None, ge=1)

    # ================================
    # VIDEO BLUEPRINT
    # ================================
    
    video_hook: Optional[str]=None
    video_scenes:Optional[List[VideoScene]]=Field(
        default=None,
        min_length=3,
        max_length=5
    )
    video_voiceover:Optional[List[str]]=None
    video_transitions:Optional[List[str]]=None
    video_visual_style: Optional[str]=None
    video_aspect_ratio:Optional[str]=None
    video_mood:Optional[str]=None
    video_duration_seconds: Optional[int]=None


    # ================================
    # POST PACKAGE
    # ================================

    posting_instructions:Optional[str]=None

 
# =================== EVALUATION ==========


Score = Annotated[float, Field(ge=0,le=10)]
class EvaluationResult(BaseModel):
    
    scores: Dict[str, Score]
    overall_score: Score
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]


# =================== SYSTEM EVALUATION ==========

class SystemEvaluationResult(BaseSchema):

    # Quality Scores
    brand_quality_score:float = Field(ge=0, le=10, 
                                description="Overall quality of the generated brand profile.")


    campaign_quality_score:float=Field(ge=0, le=10, description="" \
    "Overall quality of the generated campaign")

    brand_campaign_consistency_score:float=Field(ge=0, le=10, 
                                      description="Consistency between the brand and the campaign")
    
    # Agent Performance Score
    brand_evaluation_score:float=Field(ge=0, le=10, description="How well evaluation agent evaluate brand profile.")
    campaign_evaluation_score:float=Field(ge=0, le=10, description="how well evaluation agent evaluate campaign.")

    revision_effectiveness_score: float=Field(ge=0, le=10,
                                        description="How effectively the revision improved " \
                                        "the requested content.")
    human_feedback_alignment_score:float=Field(ge=0, le=10, 
                                         description="How well the revision addressed the human feedback.")


    strengths:List[str]

    weaknesses:List[str]

    recommendations:List[str]    

# =================== DETERMINISTIC EVALUATION ==========

class DeterministicEvaluationResult(BaseModel):

    workflow_completion_score:float=Field(ge=0, le=10)
    asset_generation_score:float=Field(ge=0,le=10)

    brand_generation_success:bool
    brand_evaluation_success:bool
    campaign_generation_success:bool
    campaign_evaluation_success:bool

    image_generation_success:bool
    video_generation_success:bool

    human_approval_completed:bool
    revision_count:int


# =================== FINAL SYSTEM EVALUATION ==========

class FinalSystemEvaluation(BaseModel):


    # -------------------------
    # DETERMINISTIC METRICS
    # -------------------------

    workflow_completion_score: float = Field(ge=0, le=10)
    asset_generation_score: float = Field(ge=0, le=10)

    brand_generation_success: bool
    brand_evaluation_success: bool
    campaign_generation_success: bool
    campaign_evaluation_success: bool

    image_generation_success: bool
    video_generation_success: bool

    human_approval_completed: bool
    revision_count: int

    # -------------------------
    # LLM EVALUATION
    # -------------------------

    brand_quality_score:float=Field(ge=0, le=10)
    campaign_quality_score:float=Field(ge=0, le=10)
    brand_campaign_consistency_score:float=Field(ge=0, le=10)

    brand_evaluation_score: float = Field(ge=0, le=10)
    campaign_evaluation_score: float = Field(ge=0, le=10)
    revision_effectiveness_score: float = Field(ge=0, le=10)
    human_feedback_alignment_score: float = Field(ge=0, le=10)

    strengths: list[str]
    weaknesses: list[str]
    recommendations: list[str]

    # -------------------------
    # FINAL SYSTEM SCORE
    # -------------------------

    overall_score: float = Field(ge=0, le=10)