from langgraph.types import interrupt
from langgraph.runtime import Runtime

from langgraph_workflow.state import WorkflowState, AgentContext
from database.database import SessionLocal
from database.crud import *

from schema_agents.agent_input_schemas import (
    BrandProfile, CampaignContext, CampaignOutput, EvaluationResult)

from evaluation.deterministic_evaluation import evaluate_deterministic
from evaluation.combined_evaluation import combine_evaluations

from services.image_generation import generate_image
from services.video_generation import generate_video, build_video_shots

from utils.logger import logger


# ====================================
# DATABASE NODE:
# =====================================

def create_campaign_run_node(state:WorkflowState)->dict:
    db = SessionLocal()

    try:
        campaign_run = create_campaign_run(db=db, user_input=state.user_input,
                                           platform=state.platform)

        logger.info(
            "Campaign run created: campaign_run_id=%s",
            campaign_run.id
        )

        return {"campaign_run_id": campaign_run.id}

    finally:
        db.close()


# ====================================
# BRAND NODE:
# =====================================

def brand_context_node(state:WorkflowState, runtime:Runtime[AgentContext]) -> dict:
    agent = runtime.context.brand_context_agent
    logger.info(
        "Starting brand context processing: campaign_run_id=%s",
        state.campaign_run_id
    )

    result = agent.run_pipeline(query=state.user_input,
                               platform=state.platform,
                               campaign_run_id=state.campaign_run_id)

    logger.info(
        "Brand context agent completed: brand_name=%s",
        result.brand_name
    )

    campaign_context = result.campaign_context

    if result.questions:
        logger.info(
            "Brand context requires human clarification: question=%s",
            result.questions
        )


        human_answers = interrupt({
            "type": "brand_context_questions",
            "questions": result.questions,
            "missing_fields": result.missing_fields,
        })

        logger.info(
            "Human provided brand context answers."
        )

        # --------------------------------------------------
        # ADD HUMAN ANSWERS TO THE ORIGINAL USER INPUT
        # --------------------------------------------------

        updated_user_input = (
            f"{state.user_input}\n\n"
            f"Additional information provided by user:\n"
            f"{human_answers}"
        )

        logger.info(
            "Re-running brand context agent with human answer."
        )

        result = agent.run_pipeline(
            query=updated_user_input,
            platform=state.platform,
            campaign_run_id=state.campaign_run_id
        )

        logger.info(
            "Brand context re-processing completed: brand_name=%s",
            result.brand_name
        )

        campaign_context = result.campaign_context



   

    # If no brand name was provided in the result
    if not result.brand_name:
        logger.warning(
            "No brand name found in brand context result."
        )

        return {
            "brand": None,
            "brand_profile_id": None,
            "campaign_context": campaign_context
        }
    
    # Database Session creation
    db = SessionLocal()
    try:
        # Check for existing brand profile
        existing_brand = get_brand_profile_by_name(
            db, result.brand_name
        )

        if existing_brand:
            logger.info(
                "Existing brand profile found: brand_name=%s, id=%s",
                existing_brand.brand_name,
                existing_brand.id
            )

            brand = BrandProfile.model_validate(existing_brand)
            # Update the existing CampaignRun
            update_campaign_run(
                db,
                state.campaign_run_id,
                brand_profile_id=existing_brand.id,
                campaign_context=campaign_context.model_dump()
                if campaign_context else None,
            )
            
            return {
                "brand": brand,
                "brand_profile_id": existing_brand.id,
                "campaign_context":campaign_context,            }
        
        # --------------------------------------------------
        # CREATE NEW BRAND PROFILE
        # --------------------------------------------------

        logger.info("Brand profile not found. Creating new brand: %s",
            result.brand_name)

        brand_profile = create_brand_profile(
            db=db,
            brand_name=result.brand_name,
            niche=result.brand_profile.niche if result.brand_profile else None,
            positioning=result.brand_profile.positioning if result.brand_profile else None,
            products=result.brand_profile.products if result.brand_profile else None,
            target_audience=result.brand_profile.target_audience if result.brand_profile else None,
            default_markets=result.brand_profile.default_markets if result.brand_profile else None,
            default_languages=result.brand_profile.default_languages if result.brand_profile else None,
            tone_of_voice=result.brand_profile.tone_of_voice if result.brand_profile else None,
            brand_colors=result.brand_profile.brand_colors if result.brand_profile else None,
            style_keywords=result.brand_profile.style_keywords if result.brand_profile else None,
                                             )

        logger.info(
            "New brand profile created: brand+name=%s, id=%s",
            brand_profile.brand_name,
            brand_profile.id
        )

        brand = BrandProfile.model_validate(brand_profile)

        # --------------------------------------------------
        # UPDATE EXISTING CAMPAIGN RUN
        # --------------------------------------------------

        update_campaign_run(db, campaign_run_id=state.campaign_run_id,
                            brand_profile_id=brand_profile.id,
            campaign_context=campaign_context.model_dump()
            if campaign_context else None,
        ) 

        logger.info(
            "CampaignRun updated with brand_profile_id=%s",
              brand_profile.id)

        return {
            "brand": brand,
            "brand_profile_id": brand_profile.id,
            "campaign_context": campaign_context,
        }


    finally:
        db.close()




# ====================================
# BRAND EVALUATION NODE:
# =====================================

def brand_evaluation_node(state:WorkflowState, runtime:Runtime[AgentContext])-> dict:

    agent = runtime.context.evaluation_agent

    logger.info(
        "Starting brand evaluation: campaing_run_id=%s",
        state.campaign_run_id
    )

    brand_evaluation = agent.evaluate_brand(state)

    logger.info("Brand evaluation completed: overall_scroe=%s",
                brand_evaluation.overall_score)
    

    # Saving brand_evaluation in db
    db = SessionLocal()
    try:
        update_campaign_run(db=db, campaign_run_id=state.campaign_run_id,
                            brand_evaluation=brand_evaluation.model_dump())
    finally:
        db.close()

    return {"brand_context_evaluation": brand_evaluation, "revision_target":"brand"}

# ====================================
# CAMPAIGN NODE:
# =====================================

def campaign_node(state:WorkflowState, runtime:Runtime[AgentContext]):
    agent = runtime.context.campaign_agent

    campaign = agent.run_pipeline(
        user_input=state.user_input,
        brand=state.brand, 
        campaign_context=state.campaign_context,
        platform=state.platform, 
        campaign_run_id=state.campaign_run_id)

    # Saving Campaign in database
    db=SessionLocal()
    try:
        update_campaign_run(db=db, campaign_run_id=state.campaign_run_id,
                            campaign=campaign.model_dump()
                            )
    finally:
        db.close()

    return { "campaign": campaign}

# =========================================
# CAMPAIGN EVALUATION NODE:
# =========================================

def campaign_evaluation_node(state:WorkflowState, runtime:Runtime[AgentContext]):
    agent = runtime.context.evaluation_agent

    logger.info(
        "Starting campaign evaluation: campaign_run_id=%s",
        state.campaign_run_id
    )

    campaign_evaluation = agent.evaluate_campaign(state)

    logger.info(
        "Campaign evalaution completed: overall_score=%s",
        campaign_evaluation.overall_score
    )

    # Saving campaign_evaluation in db
    db = SessionLocal()
    try:
        update_campaign_run(db=db, campaign_run_id=state.campaign_run_id,
                                campaign_evaluation=campaign_evaluation.model_dump())
    finally:
        db.close()

    return { "campaign_evaluation": campaign_evaluation,
            "revision_target":"campaign"}

# =========================================
# REVISION NODE:
# =========================================

def revision_node(state:WorkflowState, runtime:Runtime[AgentContext]):
    agent  = runtime.context.revision_agent

    logger.info(
        "Revision started: target=%s, revision_number=%s",
        state.revision_target,
        state.revision_count +1, 
    )

    db = SessionLocal()

    try:
        # ==========================
        # BRAND REVISION HISTORY
        # ==========================
        if state.revision_target=="brand":
            # database previous content(brand)
            previous_content = state.brand.model_dump()

            revised_brand = agent.brand_revision(state)
            # databse revised content (brand)
            revised_content = revised_brand.model_dump()

            create_revision_history(db=db, campaign_run_id=state.campaign_run_id,
                                    revision_target="brand",
                                    revision_number=state.revision_count+1,
                                    human_feedback=state.human_feedback,
                                    previous_content=previous_content,
                                    revised_content=revised_content)

            update_campaign_run(db=db, campaign_run_id=state.campaign_run_id,
                                brand=revised_content,
                                revision_count=state.revision_count+1)

            return{"brand":revised_brand, "revision_count":state.revision_count+1}

    # ==========================
    # CAMPAIGN REVISION HISTORY
    # ==========================
        elif state.revision_target=="campaign":
            # database previous content (campaign)
            previous_content = state.campaign.model_dump()

            revised_campaign = agent.campaign_revision(state)

            # database revised content (campaign)
            revised_content=revised_campaign.model_dump()

            create_revision_history(db=db, campaign_run_id=state.campaign_run_id,
                                    revision_target="campaign",
                                    revision_number=state.revision_count+1,
                                    human_feedback=state.human_feedback,
                                    previous_content=previous_content,
                                    revised_content=revised_content)

            update_campaign_run(db=db, campaign_run_id=state.campaign_run_id,
                                campaign=revised_content,
                                revision_count=state.revision_count +1 )
            
            return {"campaign": revised_campaign, "revision_count":state.revision_count+1}


        else:
            raise ValueError(f"Invalid revision_target: {state.revision_target}")
    finally :
        db.close()
    
# =========================================
# HUMAN APPROVAL NODE:
# =========================================

def human_approval_node(state:WorkflowState):
    """
    Human Approval Checkpoint.

    The human can either:
    - Approve the campaign
    - Request another revision with feedback
    """

    # Human Response
    human_response = interrupt({
        "message": "Please review the generated campaign.",
        "decision_options": ["approve", "revise"],
        "feedback_instructions": ("If you choose 'revise' explain specifically what should be changed.")
    })
    decision = human_response.get("decision")
    feedback = human_response.get("feedback") or None

    logger.info(
        "Human decision received: decision=%s",
        decision,
    )

    # -----------------------------------------
    # SAVE HUMAN DECISION TO DATABASE
    # -----------------------------------------

    db = SessionLocal()
    try:
        update_campaign_run(db=db, campaign_run_id=state.campaign_run_id,
                            human_decision=decision, 
                            human_feedback=feedback,
                        )

    finally:
        db.close()

    # -----------------------------------------
    # UPDATE LANGGRAPH STATE
    # -----------------------------------------


    if decision == "approve":
        logger.info("Human approved campaign.")
        return {"human_decision": "approve",
                "human_feedback": feedback,
                "revision_target":None}
    
    elif decision == "revise":
        logger.info("Human requested campaign revision.")
        return {"human_decision": "revise", "human_feedback": feedback,
                "revision_target": "campaign"}
    else:
        logger.error(
            "Ivalid Human decision received: %s",
            decision
        )
        raise ValueError(
            f"Invalid human decision: {decision}"
        )

# =========================================
# ASSETS GENERATION NODE:
# =========================================

def generation_node(state:WorkflowState):

    #==========================================
    # VALIDATION
    #========================================== 

    if state.campaign is None:
        logger.error("Campaign is missing. Cannot generate assets.")
        raise ValueError("Campaign is required before generating assets.")

    if state.campaign.image_prompt is None:
        logger.error("Image prompt is missing. Cannot generate image.")
        raise ValueError("Image Prompt is missing from campaign")

    #==========================================
    # IMAGE GENERATION
    #========================================== 
    image_prompt = state.campaign.image_prompt

    logger.info("Starting Image Generation.")
    
    image_output_path = (f"generated_assets/"
                   f"campaign_{state.campaign_run_id}_image.png")

    image_path, image_status, image_provider = generate_image(prompt=image_prompt, output_path=image_output_path, campaign_run_id=state.campaign_run_id)

    logger.info("Image generation completed.")
    

    #=====================================
    # VIDEO GENERATION
    #=====================================

    logger.info("Starting Video Generation.")

    # Video shots generation

    video_shots = build_video_shots(state.campaign)

    video_output_path = (f"generated_assets/"
                  f"campaign_{state.campaign_run_id}_video.mp4")

    
    video_path, video_status, video_provider = generate_video(
                                campaign=state.campaign,
                                video_shots=video_shots,
                                output_path=video_output_path,
                                campaign_run_id=state.campaign_run_id,
                            )

    logger.info("Video Generation completed.")


    #=================================
    # VIDEO PROMPT FOR DATABASE RECORD
    #=================================

    video_prompt = "\n".join(
        f"Shot{i+1}: {shot['prompt']}"
        for i, shot in enumerate(video_shots)

    )


    #=================================
    # SAVING ASSETS TO DATABASE
    #=================================

    db=SessionLocal()
    try:
        image_asset = create_generated_asset(db=db, campaign_run_id=state.campaign_run_id,
                                       asset_type="image",
                                       prompt=image_prompt,
                                       file_path=image_path,
                                       provider=image_provider,
                                       status=image_status)

        video_asset = create_generated_asset(db=db,
                                             campaign_run_id=state.campaign_run_id,
                                             asset_type="video",
                                             prompt=video_prompt, file_path=video_path,
                                             provider=video_provider,
                                             status=video_status)

        image_asset_id = image_asset.id
        video_asset_id = video_asset.id
        
    finally:
        db.close()

    logger.info("Generated assets saved to database.")

    return {
        "image_path": image_path,
        "video_path": video_path
    }

# =========================================
# SYSTEM EVALUATION NODE:
# =========================================

def system_evaluation_node(state:WorkflowState,
                           runtime:Runtime[AgentContext]):

    agent  = runtime.context.system_evaluation_agent
    db= SessionLocal()

    try:
        # -----------------------------------------
        # GET REVISION HISTORY
        # -----------------------------------------

        revisions = (db.query(RevisionHistory)
                     .filter(RevisionHistory.campaign_run_id == state.campaign_run_id)
                     .order_by(RevisionHistory.revision_number)
                     .all())

        revision_history = []

        for revision in revisions:
            revision_history.append({
                "revision_number": revision.revision_number,
                "revision_target": revision.revision_target,
                "human_feedback": revision.human_feedback,
                "previous_content": revision.previous_content,
                "revised_content": revision.revised_content,
            })

        # -----------------------------------------
        # DETERMINISTIC EVALUATION
        # -----------------------------------------

        deterministic_result = evaluate_deterministic(
            state=state,
            revision_history=revision_history
        )

        # -----------------------------------------
        # LLM SYSTEM EVALUATION
        # -----------------------------------------


        llm_result = agent.evaluate(
            state=state,
            revision_history=revision_history
        )

        # -----------------------------------------
        # COMBINE BOTH
        # -----------------------------------------

        final_result = combine_evaluations(
            deterministic_result=deterministic_result,
            llm_result=llm_result
        )

        # -----------------------------------------
        # SAVE TO DATABASE
        # -----------------------------------------

        saved_evaluation = create_system_evaluation(
            db=db,
            campaign_run_id=state.campaign_run_id,
            result=final_result
        )

        logger.info("System evaluation completed.")
        logger.info(
            "System evaluation saved to database: campaign_run_id=%s",
            state.campaign_run_id
        )
    
        return {}

    finally:
        db.close()

