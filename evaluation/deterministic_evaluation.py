from langgraph_workflow.state import WorkflowState
from schema_agents.agent_input_schemas import DeterministicEvaluationResult

# Calculating Workflow Score:

def calculate_workflow_score(state):
    checks = [state.brand is not None,
              state.brand_context_evaluation is not None,
              state.campaign is not None,
              state.campaign_evaluation is not None,
              state.human_decision is not None,]

    return sum(checks)/len(checks) * 10

# Calcluating Assets Score 
def calculate_asset_score(state):
    checks = [
        state.image_path is not None, 
        state.video_path is not None,
    ]

    return sum(checks)/len(checks) * 10


def evaluate_deterministic(state, revision_history):

    return DeterministicEvaluationResult(
        workflow_completion_score= calculate_workflow_score(state),
        asset_generation_score=calculate_asset_score(state),

        brand_generation_success=state.brand is not None,
        brand_evaluation_success=state.brand_context_evaluation is not None,
        campaign_generation_success=state.campaign is not None,
        campaign_evaluation_success=state.campaign_evaluation is not None,

        image_generation_success=   state.image_path is not None,
        video_generation_success= state.video_path is not None,

        human_approval_completed=state.human_decision is not None,

        revision_count = len(revision_history)
    )

