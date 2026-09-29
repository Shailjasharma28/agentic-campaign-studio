from schema_agents.agent_input_schemas import SystemEvaluationResult
from utils.json_utils import extract_json
from llm.openai_client import call_llm, call_llm_structured
from langgraph_workflow.state import WorkflowState

class SystemEvaluationAgent:
    def build_prompt(self, state:WorkflowState, revision_history):
        prompt = f"""
You are a System Evalaution Agent.

Evaluate the performance of an AI powered Social Media Campaign Generation system.

The system performs:
User Query:
- Brand Generation
- Brand Evaluation
- Brand Revision (if required)
- Campaign Generation
- Campaign Evaluation
- Campign Revision (if required)
- Human Approval/Revision
- Image Generation
- Video Generation

You are evaluating the PERFORMANCE OF THE SYSTEM, not only the final campaign.
Evaluate the overall system using the following information.

===============WORKFLOW DATA============

USER INPUT
{state.user_input}

PLATFORM
{state.platform}

================ BRAND ================
{state.brand.model_dump() if state.brand else None}

================ BRAND EVALUATION ================
{state.brand_context_evaluation.model_dump() if state.brand_context_evaluation else None}

================ CAMPAIGN ================
{state.campaign.model_dump() if state.campaign else None}

================ CAMPAIGN EVALUATION ================
{state.campaign_evaluation.model_dump() if state.campaign_evaluation else None}

================ HUMAN DECISION ================
{state.human_decision}

================ HUMAN FEEDBACK ================
{state.human_feedback}

================ REVISION TARGET ================
{state.revision_target}

================ REVISION COUNT ================
{state.revision_count}

================ IMAGE PATH ================
{state.image_path}

================ VIDEO PATH ================
{state.video_path}

================= REVISION HISTORY==============
{revision_history}

Evaluate the system across appropriate dimensions such as:

1- BRAND QUALITY
Evaluate the quality and usefulness of the generated brand profile.

2- CAMPAIGN QUALITY
Evaluate the quality, completeness and usefulness of the generated campaign.
 
3-BRAND-CAMPAIGN CONSISTENCY
Evaluate whether the campaign appropiately reflects the generated brand.

4- BRAND EVALUATION PERFROMANCE
Evaluate whether the brand evaluation identified meaningful weakness and 
provided useful recommendations.

5- CAMPAIGN EVALUATION PERFORMANCE
Evaluate whether the campaign evaluation identified meaningful issues and 
provided useful recommendations.

6- REVISION EFFECTIVENESS
If a revision occurred, evaluate whether the system meaningfully
improved the content based on the identified problem.
If no revision occurred, evaluate based on the available evidence.

7- HUMAN FEEDBACK ALIGNMENT
If human feedback was provided, evaluate whether the subsequent
revision addressed the human's requested changes.
If no human feedback was provided, score this dimension based on
the available evidence and do not assume that feedback existed.



For every score:

- Use a scale from 0 to 10.
- Base the score only on the information provided.
- Do not invent missing events or outputs.
- Explain important weaknesses and recommendations clearly.

Return the evaluation using the required structured output schema.
"""

        return prompt

    def evaluate(self, state:WorkflowState, revision_history)-> SystemEvaluationResult:
        prompt = self.build_prompt(state=state, revision_history=revision_history)
        data = call_llm_structured(prompt, schema=SystemEvaluationResult, component="system_evaluation_agent", 
                                   campaign_run_id=state.campaign_run_id)
        
        return data
