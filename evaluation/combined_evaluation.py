from schema_agents.agent_input_schemas import FinalSystemEvaluation

def combine_evaluations(deterministic_result, llm_result):

    overall_score = (
        deterministic_result.workflow_completion_score * 0.20+
        deterministic_result.asset_generation_score *0.10+
        llm_result.brand_quality_score * 0.15 +
        llm_result.campaign_quality_score * 0.20 +
        llm_result.brand_campaign_consistency_score * 0.15 +
        llm_result.revision_effectiveness_score * 0.10 +
        llm_result.human_feedback_alignment_score * 0.10
    )

    return FinalSystemEvaluation(
        workflow_completion_score=deterministic_result.workflow_completion_score,
        asset_generation_score=deterministic_result.asset_generation_score,

        brand_generation_success=deterministic_result.brand_generation_success,
        brand_evaluation_success=deterministic_result.brand_evaluation_success,
        campaign_generation_success=deterministic_result.campaign_generation_success,
        campaign_evaluation_success=deterministic_result.campaign_evaluation_success,

        image_generation_success=deterministic_result.image_generation_success,
        video_generation_success=deterministic_result.video_generation_success,

        human_approval_completed=deterministic_result.human_approval_completed,
        revision_count=deterministic_result.revision_count,

        brand_quality_score=llm_result.brand_quality_score,
        campaign_quality_score=llm_result.campaign_quality_score,
        brand_campaign_consistency_score=llm_result.brand_campaign_consistency_score,

        brand_evaluation_score=llm_result.brand_evaluation_score,
        campaign_evaluation_score=llm_result.campaign_evaluation_score,
        revision_effectiveness_score=llm_result.revision_effectiveness_score,
        human_feedback_alignment_score=llm_result.human_feedback_alignment_score,

        strengths=llm_result.strengths,
        weaknesses=llm_result.weaknesses,
        recommendations=llm_result.recommendations,

        overall_score=round(overall_score, 2)


    )