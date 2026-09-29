import uuid
import gradio as gr 
from pathlib import Path
from langgraph_workflow.graph import run_workflow, agents
from ui.formatters import (format_brand, format_evaluation,
                           format_campaign, format_creative_blueprint,
                           format_campaign_cost)
from cost_tracking.campaign_cost import get_campaign_cost
from utils.logger import logger


# CONVERT PYDANTIC OBJECT >> DICT

def to_dict(value):
    if value is None:
        return {}

    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")

    if isinstance(value, dict):
        return value

    raise TypeError(
        f"Expected dict or Pydantic model, got {type(value)}"
    )


#===================================================
# START CAMPAIGN
#====================================================

def start_campaign(user_input, platform):

    if not user_input.strip():
        raise gr.Error("Please enter a campaign brief.")

    combined_input = user_input.strip()

  

    # Unique thread for this session
    thread_id = str(uuid.uuid4())

    try:
        result = run_workflow(
            user_input=combined_input, 
            platform=platform, 
            agents=agents, 
            thread_id=thread_id)

        # ======================================================== 
        # CHECK FOR BRAND CONTEXT INTERRUPT 
        # ========================================================

        if "__interrupt__" in result:

            interrupt_data = result["__interrupt__"]

            logger.info(
                "Brand context clarification interrupt received."

            )

            # Get the interrupt payload
            if interrupt_data:
                interrupt_value = interrupt_data[0].value
               
                questions = interrupt_value.get("questions", [])

                return(
                    "🟡 **Additional information required before creating the campaign.**", 
                      "\n".join(
                        f"{i}. {question}"
                        for i, question in enumerate(questions, start=1)
                    ),
                    "",
                    "",
                    "",
                    "",
                    "",          
                    thread_id,
                    questions, 
                )


        # ======================================================== 
        # NORMAL WORKFLOW RESULT 
        # ========================================================


        brand = to_dict(result.get("brand"))
        brand_eval = to_dict(result.get("brand_context_evaluation"))
        campaign = to_dict(result.get("campaign"))
        campaign_eval = to_dict(result.get("campaign_evaluation"))

    # Storing Thread ID for approval/revision
        return (
        "🟡 **Campaign ready for review** — review the AI-generated brand, content, and creative plan below." ,
        format_brand(brand), 
        format_evaluation(brand_eval),
        format_campaign(campaign,brand),
        format_creative_blueprint(campaign),
        format_evaluation(campaign_eval),
        thread_id)

    
    except Exception as e:
       raise gr.Error(str(e))


    
# ===================================================
# RESUME CAMPAIGN AFTER BRAND CONTEXT CLARIFICATION
# ===================================================

def continue_campaign(answers, thread_id, questions):
    if not thread_id:
        raise gr.Error("No active campaign found.")
    
    if not questions:
        raise gr.Error("No clarification questions found.")
    
    if not answers.strip():
        raise gr.Error(
            "Please provide the requested information."
        )

    try:
        answer_lines = [
            line.strip() for line in answers.splitlines()
            if line.strip()
        ]

        if len(answer_lines) != len(questions):
            raise gr.Error(
                f"Please provide exactly {len(questions)} answers, "
                f"One answer per line."
            )

        human_answers = dict(zip(questions, answer_lines))

        logger.info(
            "Mapped human clarification answers to brand context questions."
        )


        result = run_workflow(
            user_input="",
            platform="",
            agents=agents,
            human_response=human_answers,
            thread_id=thread_id,
        )


        #---------------------------------
        # WORKFLOW COMPLETED
        #---------------------------------

        brand = to_dict(result.get("brand"))
        brand_eval = to_dict(result.get("brand_context_evaluation"))
        campaign = to_dict(result.get("campaign"))
        logger.info("CAMPAIGN OBJECT: %s", campaign)

        campaign_eval = to_dict(result.get("campaign_evaluation"))

        logger.info(
            "Brand context clarification completed. Campaign workflow continued."
        )

        return (
            "🟡 **Campaign ready for review** — review the AI-generated brand, content, and creative plan below.",
            "",
            format_brand(brand),
            format_evaluation(brand_eval),
            format_campaign(campaign,brand),
            format_creative_blueprint(campaign),
            format_evaluation(campaign_eval),
            thread_id, 
            questions,
        )

    except Exception as e:
        raise gr.Error(str(e))


   
#===================================================
# HUMAN APPROVAL
#====================================================

def approve_campaign(feedback, thread_id):
    if not thread_id:
        raise gr.Error("No Active Campaign Found.")
    
    try:
        result = run_workflow(
             user_input="",
             platform="",
             agents=agents,
             human_response={
                 "decision":"approve",
                 "feedback":feedback or ""
             },
             thread_id=thread_id
        )
        image_path = result.get("image_path")
        video_path = result.get("video_path")

        cost_data = get_campaign_cost(
            campaign_run_id=result.get("campaign_run_id")
                                      )

        cost_display = format_campaign_cost(cost_data)

        if image_path:
            image_path = str(Path(image_path).resolve())

        if video_path:
            video_path = str(Path(video_path).resolve())


        return(
            "🟢 **Campaign approved** — your image and video assets have been generated.",
            image_path, video_path, cost_display

        )

    except Exception as e:
        raise gr.Error(str(e))

        

# ============================================================
# REQUEST REVISION
# ============================================================

def revise_campaign(feedback, thread_id):

    if not thread_id:
        raise gr.Error("No Active Campaign Found.")
    
    if not feedback.strip():
       raise gr.Error("Please provide revision feedback.")

    try:
        result = run_workflow(user_input="", platform="", agents=agents,
                            human_response={"decision":"revise",
                                            "feedback": feedback},
                                            thread_id=thread_id)

        brand = to_dict(result.get("brand"))
        campaign = to_dict(result.get("campaign"))
        campaign_eval = to_dict(result.get("campaign_evaluation"))
        return (
            "🔄 Revision requested. Please review the revised campaign",
            format_campaign(campaign,brand),
            format_creative_blueprint(campaign),
            format_evaluation(campaign_eval)
        )

    except Exception as e:
        raise gr.Error(str(e))

# ============================================================
# GRADIO UI
# ============================================================

with gr.Blocks(
    title="Agentic Campaign Studio"
) as demo:

    # ========================================================
    # HEADER
    # ========================================================

    gr.Markdown(
        """
        # 🤖 Agentic Campaign Studio

        ### AI-powered social media campaign generation

        Create → Evaluate → Review → Approve/Revise → Generate Assets
    """
    )

    #=====================================
    # SESSION STATE
    #=====================================

    thread_id = gr.State(value=None)

    #=====================================
    # CLARIFICATION QUESTION STATE
    #=====================================

    clarification_questions_state = gr.State(value=[])


    #=====================================
    # CAMPAIGN BRIEF
    #=====================================

    gr.Markdown("## 📝 Campaign Brief")

    user_input = gr.Textbox(
        label="Campaign Request",
        placeholder=("Create a social media campaign"
                        "for a sustainable skincare brand"),
                        lines=5, scale=3
    )

    platform=gr.Dropdown(label="Platform",
        choices=["Instagram", "Facebook", "Linkedin","X"],
        value="Instagram", scale=1
    )




    generate_button = gr.Button(
        "🚀 Generate Campaign",
    variant="primary"
)

    status = gr.Markdown()

    # ========================================================
    # BRAND CONTEXT CLARIFICATION
    # ========================================================

    gr.Markdown("## 🔎 Additional Information Required")

    clarification_questions = gr.Markdown()

    clarification_answers = gr.Textbox(
        label="Your Answers",
        placeholder=(
            "Answer each question clearly.\n\n"
            "Example:\n"
            "Brand name: Clean Skin\n"
            "Age group: 25-35\n"
            "Gender: Women\n"
            "Geography: India\n"
            "Language: Hindi\n"
            "Interests: Skincare, beauty, wellness\n"
            "Cultural context: Urban Indian audience"

        ), lines=10,
    )

    continue_button = gr.Button(
        "➡️ Continue Campaign",
         variant="primary"
    )

    # --------------------------------------------------------
    # BRAND
    # --------------------------------------------------------

    brand_output = gr.Markdown()

    # ========================================================
    # BRAND EVALUATION
    # ========================================================

    brand_evaluation_output = gr.Markdown()

    # --------------------------------------------------------
    # CAMPAIGN
    # --------------------------------------------------------
    

    campaign_output = gr.Markdown()
    # ========================================================
    # CAMPAIGN BLUEPRINT
    # ========================================================

    creative_blueprint_output = gr.Markdown()

    # ========================================================
    # CAMPAIGN EVALUATION
    # ========================================================

    campaign_evaluation_output = gr.Markdown()

    # --------------------------------------------------------
    # HUMAN APPROVAL
    # --------------------------------------------------------
    
    gr.Markdown("## 👤 Human Approval")

    feedback = gr.Textbox(
            label="Feedback",
            placeholder=(
                "Add feedback if you want the campaign revised..."
            ),
            lines=4
        )

    with gr.Row():

        approve_button = gr.Button(
            "✅ Approve Campaign",
            variant="primary"
        )

        revise_button = gr.Button(
            "🔄 Request Revision"
        )

       
    approval_status = gr.Markdown()

    # --------------------------------------------------------
    # GENERATED ASSETS
    # --------------------------------------------------------

    gr.Markdown("## 🎨 Generated Assets")

    with gr.Row():

        image_output = gr.Image(
            label="Generated Image",
            type="filepath"
        )

        video_output = gr.Video(
            label="Generated Video"
        )

    # --------------------------------------------------------
    # CAMPAIGN COST
    # --------------------------------------------------------

    gr.Markdown("## 💰 Campaign Cost")
    campaign_cost_output = gr.Markdown()


    # ========================================================
    # EVENTS
    # ========================================================
    
    # Generate Button
    generate_button.click(
        fn=start_campaign,
        inputs=[
            user_input,
            platform,
        ],
        outputs=[
            status,
            clarification_questions,
            brand_output,
            brand_evaluation_output,
            campaign_output,
            creative_blueprint_output,
            campaign_evaluation_output,
            thread_id,
            clarification_questions_state,
        ]
    )




    # Continue Button

    continue_button.click(
        fn=continue_campaign,
        inputs=[clarification_answers, thread_id,
                clarification_questions_state,],
        outputs=[
            status,
            clarification_questions,
            brand_output,
            brand_evaluation_output,
            campaign_output,
            creative_blueprint_output,
            campaign_evaluation_output,
            thread_id,
            clarification_questions_state,
        ],
    )

    # Approve Button
    approve_button.click(
        fn=approve_campaign,
        inputs=[
            feedback,
            thread_id
        ],
        outputs=[
            approval_status,
            image_output,
            video_output, campaign_cost_output
        ]
    )
    # Revise Button
    revise_button.click(
        fn=revise_campaign,
        inputs=[
            feedback,
            thread_id
        ],
        outputs=[
            approval_status,
            campaign_output,
            creative_blueprint_output,
            campaign_evaluation_output,
            
        ]
    )

    
# ============================================================
# LAUNCH
# ============================================================

if __name__ == "__main__":
    demo.launch()