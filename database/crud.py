from typing import Optional
from database.models import BrandProfile, CampaignRun, GeneratedAsset, RevisionHistory, SystemEvaluation


#==========================
# BRAND PROFILE CRUD
#==========================
def create_brand_profile(db, brand_name, niche=None, 
                         positioning=None,
                         products=None,
                         target_audience=None,
                         default_markets=None,
                         default_languages=None,
                         tone_of_voice=None,
                         brand_colors=None, 
                         style_keywords=None):
    
    brand_profile = BrandProfile(
        brand_name=brand_name,
        niche=niche,
        positioning=positioning,
        products=products,
        target_audience=target_audience,
        default_markets=default_markets,
        default_languages=default_languages,
        tone_of_voice=tone_of_voice,
        brand_colors=brand_colors,
        style_keywords=style_keywords,
    )

    db.add(brand_profile)
    db.commit()
    db.refresh(brand_profile)

    return brand_profile

def get_brand_profile_by_id(db, brand_profile_id):
    return db.get(BrandProfile, brand_profile_id)
    
def get_brand_profile_by_name(db, brand_name):
    return (
        db.query(BrandProfile)
        .filter(BrandProfile.brand_name == brand_name)
        .first()
    )

def update_brand_profile(db, brand_profile_id, **updates):
    brand_profile = db.get(BrandProfile, brand_profile_id)

    if brand_profile is None:
        raise ValueError(
            f"BrandProfile [brand_profile_id] not found."

        )

    for field, value in updates.items():
        setattr(brand_profile, field, value)

    db.commit()
    db.refresh(brand_profile)
    return brand_profile


#===============================
# CAMPAIGN RUN FUNCTIONS
#===============================

def create_campaign_run(db, user_input, platform,
                        brand_profile_id=None,
                        campaign=None):
    campaign_run = CampaignRun(user_input=user_input, 
                               platform=platform, 
                               brand_profile_id=brand_profile_id,
                               campaign=campaign,
                               status= "in_progress")
    db.add(campaign_run)
    db.commit()
    db.refresh(campaign_run)
    return campaign_run

def get_campaign_run(db, campaign_run_id):
    return db.get(CampaignRun, campaign_run_id)

def update_campaign_run(db, campaign_run_id, **updates):
    campaign_run = db.get(CampaignRun, campaign_run_id)

    if campaign_run is None:
        raise ValueError(
            f"CampaignRun {campaign_run_id} not found."
        )

    for field, value in updates.items():
        setattr(campaign_run, field, value)

    db.commit()
    db.refresh(campaign_run)

    return campaign_run

#=================================
# REVISION HISTORY FUNCTIONS
#=================================

def create_revision_history(db, campaign_run_id, revision_target,
                            revision_number, human_feedback, previous_content,
                             revised_content ):
    revision = RevisionHistory(campaign_run_id=campaign_run_id,
                               revision_target=revision_target,
                               revision_number=revision_number,
                               human_feedback=human_feedback,
                               previous_content=previous_content,
                               revised_content=revised_content)

    db.add(revision)
    db.commit()
    db.refresh(revision)

    return revision


#=============================    
# GENERATED ASSET FUNCTION
#==============================
def create_generated_asset(db, campaign_run_id,
                           asset_type,
                           prompt,
                           file_path=None, provider=None, status="generated"):

    asset = GeneratedAsset(campaign_run_id=campaign_run_id,
                           asset_type=asset_type,
                           prompt=prompt,
                           file_path=file_path,
                           provider=provider,
                           status=status)

    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset

#=============================
# SYSTEM EVALUATION FUNCTION
#=============================

def create_system_evaluation(db, campaign_run_id, result):

    evaluation = SystemEvaluation(
        campaign_run_id = campaign_run_id,
        overall_score = result.overall_score,

        workflow_completion_score=result.workflow_completion_score,
        asset_generation_score=result.asset_generation_score,

        brand_generation_success=result.brand_generation_success,
        brand_evaluation_success=result.brand_evaluation_success,
        campaign_generation_success=result.campaign_generation_success,
        campaign_evaluation_success=result.campaign_evaluation_success,

        image_generation_success=result.image_generation_success,
        video_generation_success=result.video_generation_success,

        human_approval_completed=result.human_approval_completed,
        revision_count=result.revision_count,

        brand_quality_score=result.brand_quality_score,
        campaign_quality_score=result.campaign_quality_score,
        brand_campaign_consistency_score=result.brand_campaign_consistency_score,

        brand_evaluation_score=result.brand_evaluation_score,
        campaign_evaluation_score=result.campaign_evaluation_score,
        revision_effectiveness_score=result.revision_effectiveness_score,
        human_feedback_alignment_score=result.human_feedback_alignment_score,

        strengths=result.strengths,
        weaknesses=result.weaknesses,
        recommendations=result.recommendations
    )

    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)

    return evaluation

#==============================
# SYSTEM EVALUATION RETRIEVAL
#============================== 

def get_system_evaluation(db, campaign_run_id:int):
    return(db.query(SystemEvaluation)
           .filter(SystemEvaluation.campaign_run_id==campaign_run_id)
           .first())