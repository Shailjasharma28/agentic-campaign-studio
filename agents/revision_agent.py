from llm.openai_client import call_llm, call_llm_structured
from utils.json_utils import extract_json
from schema_agents.agent_input_schemas import BrandProfile, CampaignOutput, EvaluationResult

class RevisionAgent():

    # BRAND REVISION:
    def brand_revision(self, state):
        user_input = state.user_input
        platform = state.platform
        brand = state.brand.model_dump()
        brand_evaluation = state.brand_context_evaluation.model_dump()

        prompt = f"""
        You are an expert brand strategist responsible for improving an existing
        brand profile.

        The brand profile has already been evaluated . Your task is to revise the brand based on the evaluation feedback 
        while preserving the parts that are already strong.

        USER QUERY
        {user_input}

        PLATFORM
        {platform}

        CURRENT BRAND
        {brand}

        BRAND CONTEXT EVALAUTION
        {brand_evaluation}

        REVISION INSTRUCTIONS:

        1. Carefully review the evaluation scores, strengths, weaknesses,
        and recommendations.

        2. Identify the specific weaknesses and recommendations that require
        improvement.

        3. Revise the brand to address those issues.

        4. Preserve strong elements of the existing brand unless changing them
        is necessary to improve overall coherence.

        5. Ensure the revised brand still satisfies the original user query
        and is appropriate for the specified platform.

        6. Do not make unnecessary changes simply for the sake of changing
        the brand.

        7. Do not invent information that conflicts with the user query or
        existing brand direction.

        The goal is to produce a stronger and more coherent version of the
        existing brand, not a completely different brand.

        Return the revised brand using the provided Brand schema.
        """

        revision_brand = call_llm_structured(prompt=prompt,
                                             schema=BrandProfile,
                                             component="revision_agent",
                                             campaign_run_id=state.campaign_run_id)
        return revision_brand


    # CAMPAIGN REVISION:
    def campaign_revision(self, state):
        user_input = state.user_input
        platform = state.platform
        brand = state.brand.model_dump()
        campaign = state.campaign.model_dump()
        campaign_evaluation = state.campaign_evaluation.model_dump()

        prompt = f"""
        You are an expert social media campaign strategist responsible for
    improving an existing campaign.

    The campaign has already been evaluated. Your task is to revise the
    campaign based on the evaluation feedback while preserving the parts
    that are already strong.

    USER QUERY:
    {user_input}

    PLATFORM:
    {platform}

    BRAND PROFILE:
    {brand}

    CURRENT CAMPAIGN:
    {campaign}

    CAMPAIGN EVALUATION:
    {campaign_evaluation}

    REVISION INSTRUCTIONS:

    1. Carefully review the evaluation scores, strengths, weaknesses,
    and recommendations.

    2. Identify the specific weaknesses and recommendations that require
    improvement.

    3. Revise the campaign to address those issues.

    4. Preserve strong elements of the existing campaign unless changing
    them is necessary for improvement.

    5. Ensure the revised campaign remains aligned with the brand.

    6. Ensure the revised campaign is appropriate for the specified platform.

    7. Ensure the revised campaign continues to satisfy the original
    user query.

    8. Do not make unnecessary changes simply for the sake of changing
    the campaign.

    9. Do not invent information that conflicts with the user query,
    brand profile, or existing campaign direction.

    The goal is to produce a stronger version of the existing campaign,
    not a completely different campaign.

Return the revised campaign using the provided Campaign schema.
"""

        revised_campaign= call_llm_structured(prompt=prompt,
                                              schema=CampaignOutput,
                                              component="revision_agent",
                                              campaign_run_id=state.campaign_run_id)


        return revised_campaign
        