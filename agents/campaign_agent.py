from utils.json_utils import extract_json
from llm.openai_client import call_llm, call_llm_structured
from datetime import datetime, timezone
from schema_agents.agent_input_schemas import BrandProfile, CampaignContext,CampaignOutput


class CampaignAgent():
    def build_prompt(self,
                     user_input:str,
                     brand:BrandProfile, 
                     campaign_context:CampaignContext,
                     platform:str
                     )-> str:
        brand = brand.model_dump()
        campaign_context = campaign_context.model_dump()

        prompt =f"""
        You are an expert social media campaign strategist and 
        multilingual campaign creative director.

        Create ONE complete, coherent social media campaign using 
        ALL of the source of information.
        USER REQUEST:
        {user_input}

        BRAND PROFILE:
        {brand}

        CAMPAIGN CONTEXT:
        {campaign_context}

        SELECTED PLATFORM: 
        {platform}

        INFORMATION PRIORITY
        ==========================

        1- USER REQUEST
        -This is the source of truth for what the user wants to accomplish.
        - Preserve the user's intended objective and campaign requirements.
        - Do not replace of ignore an explicit user request.

        2- BRAND PROFILE
        -This is the source of truth for stable brand identity.
        - Use the brand name, niche, positioning, products, target audience,
        markets, languages, tone of voice, brand colors and style keywords.
        - Maintain consistent brand identity across the campaign, image direction and video direction.
        - Do NOT invent brand information that is not provided.

        3- CAMPAIGN CONTEXT
        -This is the source of truth for campaign- specific targeting.
        - Use age group, gender, geography, language, interests and cultural context
        when they are provided.
        - Campaign-specific context should influence the creative concept,
        messgaing, visual direction and video direction.
        - Do NOT invent demographic or cultural information.

        4- PLATFORM
        - Adapt the campaign appropiately for the selected platform.
        - Do not confuse the platform with the campaign language.

        MULTILINGUAL INPUT AND OUTPUT 
        ============================= 
        - The user request may be written in any language. 
        - The user request may contain mixed-language or multilingual text. 
        - Understand the user's meaning and intent regardless of the input language. 
        - Do NOT require the user to provide the request in English. 
        - Preserve important brand names, product names and proper nouns appropriately.

        LANGUAGE RULE: 
        - If campaign_context.language is explicitly provided, generate the user-facing campaign content in that language. 
        - The following user-facing fields must follow the requested campaign language: 
        * hook 
        * caption
        * cta 
        * hashtags 
        * video_hook 
        * video_scenes.text 
        * video_voiceover 
        * posting_instructions 
        - If campaign_context.language is not provided, use the language of the user's request when appropriate. 
        - Do not invent a requested language when none is specified.

        CREATIVE GENERATION PROMPTS: 
        - image_prompt and video creative-direction fields should be written clearly and consistently for downstream creative-generation systems. 
        - Keep these prompts detailed enough to reflect the brand identity, campaign context, target audience, visual style and campaign concept.
        - Do NOT produce generic image or video prompts when relevant brand information is available.
    
    
    YOUR TASK:

    CAMPAIGN IDEA
    ==============
    Create:
    - idea title
    - idea angle
    - idea objective

    The campaign idea must clearly connect
    the user's request with the brand and campaign context.


    GENERATED CONTENT
    ==================
    Create:
    - hook
    - caption
    - CTA
    - hashtags

    The content must:
    - match the brand's tone of voice.
    - reflect the campaign objective.
    - address the campaign audience.
    - respect the campaign geographu and cultural context when provided.
    - use the requested campaign language.


    IMAGE DIRECTION
    ================
    Create:
    - image prompt
    - image style
    - colors
    - lighting
    - composition
    - mood
    - aspect ratio

    The image direction must be directly derived from the campaign.

    The image prompt should incorporate relevant:
    - brand identity
    - products
    - visual style
    - brand colors
    - target audience
    - geography/cultural context when provided.
    - campaign concpet

    Avoid generic stock-photo-style prompts.


    VIDEO DIRECTION
    ===============
    Create:
    - video hook
    - 3-5 scenes
    - voiceover
    - transitions
    - visual style
    - aspect ratio
    - mood
    - duration

    SCENE REQUIREMENT:
    - Generate between 3 and 5 video scenes.
    - Every video scene must contribute to the SAME campaign concept.
    - Each scene should represent a distinct visual moment in the campaign.
    - Scenes must form a logical narrative sequence.
    - Do not create unrelated or repetitive scenes.
    - Each scene must include:
        - Visual
        - Camera
        - on-screen text
        - duration
    - Keep individual scene descriptions concise enough for downstream
        video generation.

    VIDEO DURATION REQUIREMENT:
    - The total video_duration_seconds FIXED at exactly 10 seconds.
    - Generate 3–5 scenes whose individual durations sum EXACTLY to 10 seconds.
    - The sum of all scene durations MUST be 10 seconds.
    - Do not generate scenes whose combined duration exceeds or falls short of the requested duration.
    - Distribute the available duration naturally across the scenes.
    - Do not truncate, omit, or merge scenes after generation.

        
    The video direction should reflect:
    - brand identity
    - campaign objective
    - target audience
    - products
    - visual style
    - cultural context when provided
    - requested campaign language for user-facing text and voiceover

    LANGUAGE REQUIREMENT FOR VIDEO:
    ===============================
    - video_hook must be generated in the requested campaign language.
    - video_scenes.text must be generated in the requested campaign language.
    - video_voiceover must be generated in the requested campaign language.
    - Do NOT generate the voiceover in English unless English is the requested
    campaign language.
    - The voiceover must correspond naturally to the visual scenes and communicate
    the same campaign messages.


    POSTING INSTRUCTIONS
    ====================
 
    Provide practical posting instructions appropriate 
    for the selected platform and the generated campaign.


    CONSISTENCY REQUIREMENTS:
    ===========================

    - Create ONE campaign idea only.
    - All campaign elements must belong to the same campaign.
    - The hook, caption, CTA, image and video must communicate the same core campaign idea.
    - Maintain consistency between the brand, content, image and video directions.
    - Do not create multiple alternative campaigns.
    - Do not invent missing brand information.
    - Do not invent missing campaign context.
    - Do not confuse brand-level information with campaign-specific information.
    
    OUTPUT FORMAT:
    ================

    - Return ONLY valid JSON.
    - Do NOT use markdown.
    - Do NOT use ```json.
    - Do NOT include explanations outside the JSON.
    - Use normal double quotes (") around JSON string values.
    - Do NOT write \" at the beginning or end of string values.
    - Escape quotation marks only when they appear INSIDE a string value

    Respond ONLY in valid JSON using exactly this structure:

    {{ "platform": "{platform}",
        "idea_title": "...",
        "idea_angle": "...",
        "idea_objective": "...",

        "hook": "...",
        "caption": "...",
        "cta": "...",
        "hashtags": ["...", "...", "..."],

        "image_prompt": "...",
        "image_style": "...",
        "image_colors": ["...", "...", "..."],
        "image_lighting": "...",
        "image_composition": "...",
        "image_mood": "...",
        "image_aspect_ratio": "...",

        "video_hook": "...",
        "video_scenes": [
            {{
                "visual": "...",
                "camera":"...",
                "text": "...",
                "duration": 3
            }}
        ],
        "video_voiceover": ["..."],
        "video_transitions": ["..."],
        "video_visual_style": "...",
        "video_aspect_ratio": "...",
        "video_mood": "...",
        "video_duration_seconds": 12,

        "posting_instructions": "..."
    }}
    """
        return prompt

    def run_pipeline(self,
                    user_input:str,
                    brand:BrandProfile, 
                    campaign_context:CampaignContext,
                    platform:str, 
                    campaign_run_id:int)-> CampaignOutput:
        
        prompt = self.build_prompt(
            user_input=user_input,
            brand=brand, 
            campaign_context=campaign_context,
            platform=platform)
        data = call_llm_structured(prompt, 
                                   schema=CampaignOutput,
                                   component="campaign_agent", 
                                   campaign_run_id=campaign_run_id
                                   )

        
        print(data)

        return data

    