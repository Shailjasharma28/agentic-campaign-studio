from sqlalchemy import DateTime, ForeignKey, MetaData, Table, Column, Integer,JSON, String, Text
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Mapped, mapped_column, relationship
from datetime import datetime, timezone
from typing import Optional, List
from database.database import Base
from decimal import Decimal
from sqlalchemy import Numeric


# =========================================================
# BRAND PROFILE
# =========================================================

class BrandProfile(Base):
    __tablename__ = "brand_profiles"

    id:Mapped[int]=mapped_column(Integer, primary_key=True)

    brand_name:Mapped[str]=mapped_column(String, nullable=False,
                                         index=True)

    niche:Mapped[str]=mapped_column(Text,nullable=True)

    positioning:Mapped[Optional[str]]=mapped_column(
        Text, nullable=True
    )

    products:Mapped[Optional[list]]=mapped_column(JSON, nullable=True)


    target_audience:Mapped[Optional[str]]=mapped_column(
        Text, nullable=True
    )

    default_markets:Mapped[Optional[list]]=mapped_column(
        JSON, nullable=True
    )

    default_languages:Mapped[Optional[list]]=mapped_column(
        JSON, nullable=True
    )

    tone_of_voice: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    brand_colors: Mapped[Optional[list]] = mapped_column(
        JSON,
        nullable=True
    )

    style_keywords: Mapped[Optional[list]] = mapped_column(
        JSON,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationship: One brand -> many campaign runs
    campaign_runs = relationship(
        "CampaignRun", back_populates="brand_profile"

    )





class CampaignRun(Base):
    __tablename__ = "campaign_runs"

    id:Mapped[int]=mapped_column(Integer, primary_key=True)

    # User Input
    user_input:Mapped[str]=mapped_column(
        Text, nullable=False
    )
    platform:Mapped[str]=mapped_column(String, nullable=False)

    # Brand
    brand_profile_id:Mapped[Optional[int]]=mapped_column(
        ForeignKey("brand_profiles.id"),nullable=True, index=True
    )

    brand_profile=relationship("BrandProfile", 
                               back_populates="campaign_runs")

    # Campaign-context
    campaign_context:Mapped[Optional[dict]]=mapped_column(
        JSON, nullable=True
    )


    # Brand and Context Evaluation
    brand__context_evaluation:Mapped[Optional[dict]]=mapped_column(JSON, nullable=True)


    # Campaign
    campaign:Mapped[Optional[dict]]=mapped_column(JSON, nullable=True)

    campaign_evaluation:Mapped[Optional[dict]]=mapped_column(JSON, nullable=True)

    # Revision/Human Approval
    revision_count :Mapped[int]=mapped_column(Integer, default=0)
    revision_target:Mapped[Optional[str]]=mapped_column(String, nullable=True)

    human_decision: Mapped[Optional[str]]=mapped_column(String, nullable=True)
    human_feedback:Mapped[Optional[str]]=mapped_column(Text, nullable=True)

    # Workflow Status
    status: Mapped[str]=mapped_column(String, default="in_progress")

    created_at : Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda:datetime.now(timezone.utc)
    )
    updated_at : Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda:datetime.now(timezone.utc),
        onupdate=lambda:datetime.now(timezone.utc)

    )


# REVISION HISTORY

class RevisionHistory(Base):
    __tablename__ = "revision_history"

    id:Mapped[int]=mapped_column(Integer, primary_key=True)

    campaign_run_id:Mapped[int]=mapped_column(ForeignKey("campaign_runs.id"),nullable=False)

    revision_target :Mapped[str]=mapped_column(String, nullable=False)

    revision_number:Mapped[int]=mapped_column(Integer, default=0)

    human_feedback:Mapped[Optional[str]]=mapped_column(Text, nullable=True)

    previous_content:Mapped[Optional[dict]]=mapped_column(JSON, nullable=True)
    revised_content:Mapped[Optional[dict]]=mapped_column(JSON, nullable=True)

    created_at : Mapped[datetime] = mapped_column(
            DateTime(timezone=True),
            default=lambda:datetime.now(timezone.utc)
        )
    updated_at : Mapped[datetime] = mapped_column(
            DateTime(timezone=True),
            default=lambda:datetime.now(timezone.utc),
            onupdate=lambda:datetime.now(timezone.utc)
    
        )


# GENERATED ASSET

class GeneratedAsset(Base):
    __tablename__ = "generated_assets"

    id :Mapped[int]=mapped_column(Integer, primary_key=True)

    campaign_run_id: Mapped[int]=mapped_column(Integer, ForeignKey("campaign_runs.id"),nullable=False)

    asset_type :Mapped[str]=mapped_column(String, nullable=False)
    prompt:Mapped[Optional[str]]=mapped_column(Text, nullable=True)

    file_path:Mapped[str]=mapped_column(String, nullable=False)
    provider:Mapped[str]=mapped_column(String, nullable=False)
    status:Mapped[str]=mapped_column(String, default="generated")

    created_at : Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda:datetime.now(timezone.utc)
    )
    updated_at : Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda:datetime.now(timezone.utc),
        onupdate=lambda:datetime.now(timezone.utc)

    )

# SYSTEM EVALUATION

class SystemEvaluation(Base):

    __tablename__ = "system_evaluations"

    id:Mapped[int] = mapped_column(Integer, primary_key=True)

    campaign_run_id:Mapped[int]=mapped_column(ForeignKey("campaign_runs.id"),
                                              nullable=False)

    # Final Score
    overall_score:Mapped[float]=mapped_column(nullable=False)

    # Deterministic
    workflow_completion_score:Mapped[float]=mapped_column(
        nullable=False
    )

    asset_generation_score:Mapped[float]=mapped_column(nullable=False)

    brand_generation_success:Mapped[bool]=mapped_column(nullable=False)

    brand_evaluation_success:Mapped[bool]=mapped_column(nullable=False)

    campaign_generation_success:Mapped[bool]=mapped_column(nullable=False)

    campaign_evaluation_success:Mapped[bool]=mapped_column(nullable=False)

    image_generation_success:Mapped[bool]=mapped_column(nullable=False)

    video_generation_success: Mapped[bool] = mapped_column(
        nullable=False
    )

    human_approval_completed: Mapped[bool] = mapped_column(
        nullable=False
    )

    revision_count: Mapped[int] = mapped_column(
        nullable=False
    )

    # LLM evaluation
    
    brand_quality_score: Mapped[float] = mapped_column(nullable=False)
    campaign_quality_score: Mapped[float] = mapped_column(nullable=False)
    brand_campaign_consistency_score: Mapped[float] = mapped_column(nullable=False)

    brand_evaluation_score: Mapped[float] = mapped_column(nullable=False)
    campaign_evaluation_score: Mapped[float] = mapped_column(nullable=False)
    revision_effectiveness_score: Mapped[float] = mapped_column(nullable=False)
    human_feedback_alignment_score: Mapped[float] = mapped_column(nullable=False)

    strengths: Mapped[list] = mapped_column(JSON, nullable=True)
    weaknesses: Mapped[list] = mapped_column(JSON, nullable=True)
    recommendations: Mapped[list] = mapped_column(JSON, nullable=True)


# LLM USAGE

class LLMUsage(Base):
    __tablename__ = "llm_usage"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    campaign_run_id:Mapped[int]=mapped_column(ForeignKey("campaign_runs.id"),
                                              nullable=False)

    component:Mapped[str]=mapped_column(String, nullable=False)

    model:Mapped[str]=mapped_column(String, nullable=False)

    input_tokens:Mapped[int]=mapped_column(Integer, nullable=False)

    output_tokens:Mapped[int]=mapped_column(Integer, nullable=False)

    total_tokens:Mapped[int]=mapped_column(Integer, nullable=False)

    cost:Mapped[Decimal]=mapped_column(Numeric(12,8), nullable=False)


#  MEDIA USAGE

class MediaUsage(Base):
    __tablename__ = "media_usage"

    id:Mapped[int]=mapped_column(Integer, primary_key=True, index=True)

    campaign_run_id:Mapped[int]=mapped_column(ForeignKey("campaign_runs.id"),
                                              nullable=False)

    media_type:Mapped[str]=mapped_column(
        String,
        nullable=False
    )

    model:Mapped[str]=mapped_column(
        String, nullable=False
    )

    duration_seconds:Mapped[Optional[int]]=mapped_column(
        Integer, nullable=True
    )

    cost:Mapped[Decimal]=mapped_column(
        Numeric(12,8),nullable=False
    )