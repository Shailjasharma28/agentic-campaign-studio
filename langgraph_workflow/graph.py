from langgraph.graph import StateGraph, END, START
from langgraph.types import Command
from langgraph.checkpoint.memory import MemorySaver
from langgraph_workflow.state import WorkflowState, AgentContext
from langgraph_workflow.nodes import (create_campaign_run_node, brand_context_node, brand_evaluation_node,
    campaign_node,
    campaign_evaluation_node, 
    revision_node,
    human_approval_node,
    generation_node,
    system_evaluation_node)
from langgraph_workflow.config import REVISION_THRESHOLD,MAX_BRAND_REVISIONS, MAX_CAMPAIGN_REVISIONS
from agents.brand_context_agent import BrandContextAgent
from agents.campaign_agent import CampaignAgent
from agents.evaluation_agent import EvaluationAgent
from agents.revision_agent import RevisionAgent
from agents.system_evaluation_agent import SystemEvaluationAgent
from utils.logger import logger

graph=StateGraph(WorkflowState, context_schema=AgentContext)
checkpointer = MemorySaver()

# ---------------------
# REVISION ROUTER:
# --------------------- 

def revision_router(state:WorkflowState):

    if state.revision_target == "brand":
        logger.info("Revision target: brand")
        return "brand_evaluation"

    if state.revision_target == "campaign":
        logger.info("Revision target: campaign")
        return "campaign_evaluation"

    logger.warning("NO valid revision target found. Routing to human approval.")
    return "human_approval"



# ---------------------
# BRAND EVALUATION ROUTER:
# ---------------------

def brand_evaluation_router(state:WorkflowState):
    brand_evaluation = state.brand_context_evaluation

    brand_score = getattr(brand_evaluation, "overall_score", None)
    # Safe Check
    if brand_score is None:
        logger.warning(
            "Brand Evaluation has no overall score. "
            "Routing to campaign."
        )
        return "campaign"
    
    logger.info(
        "Brand Evaluation: score=%s/10, revision=%s%s",
        brand_score,
        state.revision_count,
        MAX_BRAND_REVISIONS,
    )

    # CASE 1- Score is GOOD enough

    if brand_score >= REVISION_THRESHOLD:
        logger.info(
            "Brand score meets threshold. Processing to campaign."
        )
        return "campaign"

    # CASE 2- Score is below threshold

    if brand_score < REVISION_THRESHOLD:
        if state.revision_count < MAX_BRAND_REVISIONS:
            logger.info(
                "Brand score below threshold. "
                "Revision required."
            )
            return "revision"

        # CASE 3- Score still below threshold but maximum revisions have been used.
        logger.warning(
            "Maximum brand revision reached. "
            "Proceeding to campaign."
        )
        return "campaign"


# ---------------------
# CAMPAIGN EVALUATION ROUTER:
# ---------------------
def campaign_evaluation_router(state:WorkflowState):
    campaign_evaluation = state.campaign_evaluation

    # Safe check 
    if campaign_evaluation is None:
        logger.warning(
            "No campaign evaluation found. "
            "Routing to human approval."
        )
        return "human_approval" 

    campaign_score = getattr(campaign_evaluation, "overall_score", None)

    if campaign_score is None:
        logger.warning(
                    "Campaign Evaluation has no overall score. "
                    "Routing to human approval."
                )
        return "human_approval"

    logger.info(
        "Campaign evaluation: score=%s/10, revision=%s%s",
        campaign_score,
        state.revision_count,
        MAX_CAMPAIGN_REVISIONS,
    )
    # CASE 1- Score is GOOD enough

    if campaign_score >= REVISION_THRESHOLD:
        logger.info(
            "Campaign score meets threshold. "
            "Proceeding to human approval."
        )
        return "human_approval"

    # CASE 2- Score is below threshold

    if campaign_score < REVISION_THRESHOLD:
        if state.revision_count < MAX_CAMPAIGN_REVISIONS:
            logger.info(
                "Campaign score below threshold. "
                "Revision required."
            )
            return "revision"

        # CASE 3- Score still below threshold but maximum revisions have been used.
        logger.warning(
            "Maximum campaign revisions reached. "
            "Proceeding to human approval."
        )
        return "human_approval"



# ------------------------
# HUMAN APPROVAL ROUTER
#-------------------------

def human_decision_router(state:WorkflowState):
    print("ENTERING HUMAN DECISION ROUTER")
    decision = state.human_decision
    logger.info(
        "Human decision received: %s",
        decision,
    )
    if state.human_decision == "revise":
        logger.info(
            "Human requested revision."
        )
        return "revision"
    
    elif state.human_decision == "approve":
        logger.info(
            "Human approved campaign: Proceeding to generation."
        )
        return "generation"
    
    else:
        logger.error(
            "Invalid human decision: %s",
            decision,
        )
        raise ValueError(f"Inavlid Human Decision: {state.human_decision}")


# ------------------------
# BUILD THE GRAPH
#-------------------------

def build_graph():
    # Add Nodes:
    graph.add_node("brand_context", brand_context_node)
    graph.add_node("create_campaign_run", create_campaign_run_node)
    graph.add_node("brand_evaluation", brand_evaluation_node)
    graph.add_node("campaign", campaign_node)
    graph.add_node("campaign_evaluation", campaign_evaluation_node)
    graph.add_node("revision", revision_node)
    graph.add_node("human_approval", human_approval_node)
    graph.add_node("generation",generation_node)
    graph.add_node("system_evaluation", system_evaluation_node)

    # Add edges:
    graph.add_edge(START, "create_campaign_run")
    graph.add_edge("create_campaign_run", "brand_context")
    graph.add_edge("brand_context", "brand_evaluation")
    graph.add_conditional_edges("brand_evaluation", brand_evaluation_router, {"revision":"revision", "campaign":"campaign"})
    graph.add_edge("campaign", "campaign_evaluation")
    graph.add_conditional_edges("campaign_evaluation", campaign_evaluation_router, {"revision":"revision", "human_approval":"human_approval"},)
    graph.add_conditional_edges("revision", revision_router, {
        "brand_evaluation":"brand_evaluation",
        "campaign_evaluation":"campaign_evaluation",
        "human_approval": "human_approval"})
   

    # HUMAN APPROVAL -> END
    graph.add_conditional_edges("human_approval", human_decision_router,
                                {"revision": "revision",
                                 "generation": "generation"})
    
    
    graph.add_edge("generation", "system_evaluation")
    graph.add_edge("system_evaluation", END)
    # Compile graph
    return graph.compile(checkpointer=checkpointer)

#CREATING THE GRAPH ONCE
app = build_graph()


# RUN WORKFLOW
def run_workflow(user_input, platform,agents, human_response=None,thread_id=None):

    if thread_id is None:
        raise ValueError("thread_id is required.")
    
    config={"configurable":{"thread_id":thread_id}}

    # Initial state (FIRST RUN)
    if human_response is None:
        initial_state={
            "user_input": user_input,
            "platform": platform,
        }
        logger.info("Startign campaign workflow..")
        return app.invoke(initial_state, config=config, context=AgentContext(**agents))

    # Resume after human decision
    else:
        logger.info("Resuming campaign workflow after human decision.")
        return app.invoke(
            Command(resume=human_response),
            config=config,
            context=AgentContext(**agents) 
        )

brand_context_agent = BrandContextAgent()
campaign_agent = CampaignAgent()
evaluation_agent = EvaluationAgent()
revision_agent = RevisionAgent()
system_evaluation_agent = SystemEvaluationAgent()


agents = {

    "brand_context_agent": brand_context_agent,
    "campaign_agent": campaign_agent,
    "evaluation_agent": evaluation_agent,
    "revision_agent": revision_agent,
    "system_evaluation_agent": system_evaluation_agent,
}


