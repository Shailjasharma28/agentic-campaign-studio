from utils.json_utils import extract_json
from llm.openai_client import call_llm
from schema_agents.agent_input_schemas import BrandProfile, CampaignOutput, EvaluationResult
from langgraph_workflow.state import WorkflowState


class EvaluationAgent():
    # BRAND EVALUATION
    def evaluate_brand(self, state:WorkflowState):
        user_input = state.user_input
        brand = state.brand.model_dump()
        campaign_context = (state.campaign_context.model_dump() 
        if state.campaign_context else None)


        prompt=  f"""
        You are an expert brand strategist and brand evaluator.
        Your task is to evaluate the brand profile created for the user's
        request.
        USER QUERY:
        {user_input}

        BRAND PROFILE:
        {brand}

        CAMPAIGN CONTEXT:
        {campaign_context}

        EVALUATION SCOPE
        ==================
        Evaluate the quality, accuracy, completeness and internal consistency
        of the BRAND PROFILE and CAMPAIGN CONTEXT as outputs of the brand context
        extraction process.
         
        The CAMPAIGN CONTEXT contains campaign-specific information and 
        should be used only to understand the intended audience and campaing requirements
        when relevant.

        Do NOT treat campaign-specific information as permanent brand identity.

        Do NOT penalize the brand profile for information that was not provided
        by the user and is not reasonably expected to exist in the brand profile.

        EVALUATION CRITERIA
        =====================


        Evaluate the brand on a scale of 0 to 10 using ONLY these criteria
       
        1. brand_clarity
        How clearly does the brand profile communicate what it is, 
        what it offers, what it stands for based on the information provided.
        

        2. audience_fit
        How well does the brand's stated target audience align
        with the intended target audience when such information is explicitly available.

        3. differentiation
        How clearly is the brand differentiated from competitors or alternatives
        based on the information provided?

        4. positioning
        How strong, relevant, and coherent is the brand positioning?

        5. brand_voice
        How appropriate, distinctive, and consistent is the proposed brand voice?

        6. brand_consistency
        How consistently do the available brand identity, positioning, audience,
        messaging, and voice work together?

        SCORING:
        =========

        - 0 = extremely poor
        - 5 = average / needs significant improvement
        - 10 = excellent
        
        Calculate overall_score as the average of the six criterion scores.

        Do not artificially increase the score because information is missing.
        At the same time, do not penalize the brand for information that the user never provided.
        
        Also provide:
        =============

        - strengths: identify the strongest aspects of the brand
        - weaknesses: identify specific problems, inconsistencies or meaningful gaps in the
        information that was actually provided.

        - recommendations: provide actionable improvements that would strengthen the brand profile.


        IMPORTANT RULES:
        ==================

        - Evaluate the brand profile AND campaign context against the information
            explicitly provided in the user's request.
        - Compare them against the information 
            explicitly provided in the user's request.
        - Do NOT invent additional brand or campaign information.
        - Do NOT assume missing information is incorrect simply because it was not
            provided by the user.
        - Verify that explicitly provided information has been accurately captured
            and assigned to the correct field.
        - Verify that stable brand information is stored in the brand profile and
            campaign-specific information is stored in campaign context.

        
        OUTPUT STRUCTURE:
        ==================

        {{
        scores: {{
                "brand_clarity": 0,
                "audience_fit": 0,
                "differentiation": 0,
                "positioning": 0,
                "brand_voice": 0,
                "brand_consistency": 0
        }},
        overall_score: 0,
        strengths:["...","...","..."],
        weaknesses: ["...","...","..."],
        recommendations: ["...","...","..."]
        }}
        Return ONLY valid JSON.
        Do not include markdown.
        Do not include ```json.
        """
        

        raw = call_llm(prompt, component="evaluation_agent", campaign_run_id=state.campaign_run_id)
        data = extract_json(raw)
        return EvaluationResult(**data)
        


    def evaluate_campaign(self, state:WorkflowState):
        user_input = state.user_input
        platform = state.platform
        brand_dict = state.brand.model_dump()
        campaign_context = (state.campaign_context.model_dump() 
                            if state.campaign_context else None)
        campaign_dict = state.campaign.model_dump()

        prompt = f"""
        
        You are an expert social media strategist and campaign evaluator.
        
        Your task is to critically evaluate the generated social media campaign
        against the user's request, brand profile, campaign context and 
        selected platform.

        USER QUERY: 
        {user_input}

        SELECTED PLATFORM:
        {platform}

        BRAND PROFILE:
        {brand_dict}

        CAMPAIGN CONTEXT:
        {campaign_context}
        
        GENERATED CAMPAIGN:
        {campaign_dict}
        
        EVALUATION OBJECTIVE
        ======================

        Determine how well the generated campaign fulfills the user's request while
        remaining aligned with the brand profile, campaign context,
        requested language and selected platform.

        Evaluate the campaign as a COMPLETE campaign package, including:

        -campaign idea
        - hook
        - caption
        - hashtags
        - image direction
        - video direction
        - posting instructions

        EVALUATION CRITERIA
        =====================

        Evaluate the campaign on a scale of 0-10 using ONLY these criteria.

        1. brand_alignment 
        
        How well does the campaign align with the brand's: 
        - identity 
        - niche 
        - positioning 
        - products 
        - target audience 
        - tone of voice 
        - brand colors 
        - style keywords
       
         when those attributes are available?
        Do not penalize the campaign for optional brand information that was not provided.
    
        2. audience_relevance 
        How relevant is the campaign to the intended target audience? 
        Consider the audience information available in the brand profile and campaign context, including:
        - age group 
        - gender 
        - geography 
        - interests 
        
        when provided. 

        Do not invent audience characteristics that are not provided.
        
        3. platform_fit 
        How appropriate is the campaign for the specified platform? 
        Consider: 

        - content format 
        - communication style 
        - expected audience behavior
        - platform-appropriate creative structure 
        - image/video format 
        - aspect ratio 
        - content length 
        - CTA suitability 
        
        Evaluate against the selected platform: 

        {platform}

        4. content_quality 
        How clear, engaging, valuable, persuasive and well-structured is the generated campaign content?
        
        Consider: 
        
        - idea quality 
        - hook strength 
        - caption quality 
        - CTA effectiveness
        - hashtag relevance 
        - clarity 
        - persuasiveness 
        - usefulness to the intended audience

        5. visual_consistency 
        How well does the image and video direction reflect the brand and the campaign concept?
         
        Evaluate: 
        - image prompt 
        - image style 
        - image colors 
        - lighting 
        - composition 
        - image mood 
        - video hook 
        - video scenes 
        - video visual style 
        - video mood 
        - video transitions 
        
        The visual directions should be specific to the brand and campaign.
        
        Do not give a high score to generic visual prompts that could apply to almost any brand.
        

        6. campaign_coherence 
        How well do all campaign elements communicate the SAME campaign idea? 
        
        Evaluate consistency between: 
        
        - idea 
        - objective 
        - hook 
        - caption 
        - CTA 
        - hashtags 
        - image direction 
        - video direction 
        - posting instructions

        The image and video should support the same campaign concept 
        rather than introducing unrelated creative ideas.

        7. context_alignment 
        
        How well does the campaign use the campaign-specific context? 
        Evaluate whether the generated campaign appropriately reflects the explicitly provided: 
        - geography 
        - age group 
        - gender 
        - interests 
        - cultural context 
        - campaign language when available. 
        
        Campaign context should influence the campaign's messaging and creative direction where relevant.
        
        Do not invent campaign context that was not provided. 
        
        Do not penalize the campaign for optional context that was not supplied.
        

        8. language_alignment 
        
        How accurately does the generated campaign follow the requested campaign language? 
        
        If campaign_context.language is explicitly provided, verify that the following user-facing fields are generated in that language: 
        - hook 
        - caption 
        - CTA 
        - hashtags 
        - video_hook 
        - video_scenes.text 
        - video_voiceover 
        - posting_instructions
         
        Pay particular attention to video_voiceover.
        The voiceover must be generated in the requested campaign language and must naturally correspond to the visual scenes and campaign message. 
        
        Do NOT give a high language_alignment score if the campaign is mostly correct but the voiceover is generated in the wrong language. 
        
        If campaign_context.language is not provided, evaluate whether the campaign appropriately follows the language of the user's request.
         
        Do not penalize image_prompt or technical creative-direction fields merely because they are written in English, when they are intended for downstream creative-generation systems.


        SCORING ======= 
        
        - 0 = extremely poor 
        - 5 = average / needs significant improvement 
        - 10 = excellent 
        
        Calculate overall_score as the arithmetic average of ALL eight criterion scores.
        Do not artificially increase scores because the campaign is well-written.
        A campaign should receive a high score only when it is: 
        - aligned with the user's request 
        - aligned with the brand 
        - relevant to the campaign audience 
        - appropriate for the platform 
        - context-aware 
        - language-compliant 
        - visually consistent 
        - internally coherent

        ALSO PROVIDE
        =============

        strengths:
        Identify the strongest aspects of the generated campaign.

        weakness:
        Identify specific problems, mismatches, omissions or inconsistencies.

        recommendations:
        Provide actionable improvements that would meaningfully improve the campaign.

        IMPORTANT RULES =============== 
        - Evaluate the GENERATED CAMPAIGN, not the quality of the brand itself. 
        - Compare the campaign against the USER REQUEST, BRAND PROFILE, CAMPAIGN CONTEXT and PLATFORM. 
        - Treat the brand profile as the source of truth for stable brand identity. 
        - Treat campaign context as the source of truth for campaign-specific targeting and requirements. 
        - Treat the user request as the source of truth for the requested campaign objective and explicit requirements. 
        - Do NOT invent information that is not present in the user request, brand profile, campaign context or platform. 
        - Do NOT penalize missing information when it was never provided. - Be critical and objective. 
        - Do not give high scores simply because the campaign is grammatically correct or well-written. 
        - Check whether the image and video directions are actually specific to the brand and campaign. 
        - Check whether the campaign language is correctly followed. 
        - Check whether video_voiceover follows the requested language. 
        - Return the result using the provided EvaluationResult schema.
        
        OUTPUT STRUCTURE
        ==================

        {{
            "scores": {{
             "brand_alignment": 0,
                "audience_relevance": 0,
                "platform_fit": 0,
                "content_quality": 0,
                "visual_consistency": 0,
                "campaign_coherence": 0,
                "context_alignment":0,
                 "language_alignment": 0                     
                   }},

            "overall_score": 0,
            "strengths":["...","...","..."],
            "weaknesses": ["...","...","..."],
            "recommendations": ["...","...","..."]
            }}
            
        Return ONLY valid JSON.
        Do not include markdown.
        Do not include ```json.
        """

        raw = call_llm(prompt, 
                       component="evaluation_agent", 
                       campaign_run_id=state.campaign_run_id)

        data = extract_json(raw)
        
        return EvaluationResult(**data)
