# Agentic Campaign Studio

An agentic AI system for generating, evaluating, revising, and producing social media campaigns with AI-generated creative assets.

## Overview

Agentic Campaign Studio is an agentic AI workflow designed to transform a client brief into a structured social media campaign.

The system uses specialized agents to understand brand and campaign context, generate campaign content, evaluate the output,
perform revisions when required and obtain human approval before generating final creative assets.

The approved campaign can then be used to generate AI-powered image and multi-shot video assets, while campaign runs, generated assets, revisions and media usage are persisted in a database.


## Demo

The system takes a client brief through an agentic campaign workflow and produces an approved campaign along with generated image and multi-shot video assets.

The workflow demonstrates:

- Multi-agent collaboration
- Structured campaign generation
- Brand and campaign evaluation
- Automated revision
- Human-in-the-loop approval
- AI image and multi-shot video generation
- Cost tracking and database persistence

Screenshots: See the screenshots/ folder for examples of the application workflow and generated output.





## Problem

Generating social media content with a single LLM prompt can produce inconsistent or generic results because campaign quality depends on multiple factors such as:

- Brand identity
- Target audience
- Campaign objective
- Platform
- Tone of voice 
- Cultural context
- Creative direction
- Visual consistency

A campaign also needs evaluation and refinement rather than simply accepting the first generated response.


## Solution

Agentic Campaign Studio approaches campaign creation as a structured workflow rather than a single LLM call.

The workflow separates context extraction, campaign generation, evaluation, revision, human approval and asset generation into
distinct stages.

This allows the system to iteratively improve campaign output while keeping a human in the approval loop before creative assets are generated.


## Key Features

- Brand context extraction
- Persistent brand profiles
- Structured campaign generation
- Brand evaluation
- Campaign evaluation
- Automated revision loop
- Human approval workflow
- AI image generation
- Multi-shot AI video generation
- Generated asset persistence
- Media usage and cost tracking
- System-level evaluation


## Architecture

The system is implemented as a stateful LangGraph workflow. Each stage performs a specific responsibility and passes structured state to the next stage.


```text
Client Brief
     |
     ▼
Brand Context Agent 
     │
     ▼
Brand Profile
     │
     ▼
Brand Evaluation
     │
     ▼
Campaign Agent
     │
     ▼
Campaign Evaluation
     │
     ▼
Revision Loop
     │
     ▼
Human Approval
     │
     ▼
Asset Generation
     ├──────────────┐
     ▼              ▼
Image Generation   Multi-Shot Video
     │              │
     └───────┬──────┘
             ▼
      System Evaluation
             │
             ▼
        Campaign Complete
```

## Agent Workflow

### Brand Context Agent

Extracts relevant brand and campaign information from the client's brief and establishes the context required for campaign generation.

### Campaign Agent

Generates a structured campaign containing campaign strategy, social media copy, image direction, and video direction.

### Evaluation Agent

Evaluates the brand context and generated campaign against defined criteria and identifies strengths, weaknesses, and areas requiring improvement.

### Revision Agent

Uses evaluation feedback to revise the relevant campaign components when the output does not meet the required quality threshold.

### Human Approval

The workflow pauses for human review after the evaluation and revision stages. The campaign can either be approved or sent back for revision.

### System Evaluation Agent

Performs a final evaluation of the completed workflow and generated output.


## Campaign Output

The Campaign Agent produces a structured `CampaignOutput` containing:

### Campaign Content

- Campaign idea/title
- Campaign angle
- Objective
- Hook
- Caption
- Call to action
- Hashtags

### Image Direction

- Image prompt
- Visual style
- Colors
- Lighting
- Composition
- Mood
- Aspect ratio

### Video Direction

- Video hook
- 3–5 video scenes
- Camera direction
- On-screen text
- Voiceover
- Transitions
- Visual style
- Mood
- Aspect ratio
- Video duration

## AI Asset Generation

After human approval, the approved campaign is passed to the asset generation stage.

### Image Generation

The campaign's structured image direction is used to generate the campaign image.

### Multi-Shot Video Generation

The campaign's video scenes are converted into individual video shots and submitted to the Runway Multi-Shot Video Recipe.

The workflow validates that:

- The campaign contains 3–5 video scenes.
- Each scene contains the required visual and camera information.
- Individual scene prompts remain within the provider's prompt limit.
- Scene durations sum exactly to the requested total video duration.

The generated image and video are stored as campaign assets and associated with the corresponding campaign run.

## Technology Stack

- **Python** — Application and workflow implementation
- **LangGraph** — Stateful agentic workflow orchestration
- **Pydantic** — Structured outputs and validation
- **SQLAlchemy** — Database ORM
- **SQLite** — Persistent application database
- **Gradio** — User interface
- **OpenAI API** — LLM 
- **Runway API** — Image and Multi-shot video generation

## Project Structure

```text
project/
├── agents/
├── database/
├── langgraph_workflow/
├── services/
├── cost_tracking/
├── evaluation/
├── llm/
├── ui/
├── utils/
├── schema_agents/
├── screenshots/
├── app.py
├── requirements.txt
├── .env.example
└── README.md
```

## Installation

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd <project-directory>
```
### 2. Create and activate the virtual environment

```bash
python -m venv myvenv
myvenv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the project root and add the required API credentials:

```env
OPENAI_API_KEY=your_openai_api_key
RUNWAYML_API_SECRET=your_runway_api_key
```

Make sure .env is included in .gitignore.


## Running the Application

Start the Gradio application with:

```bash
python app.py
```

## Example Workflow

A typical workflow looks like:

```text
Client Brief
     ↓
Missing context identified
     ↓
Additional client information
     ↓
Brand profile created
     ↓
Campaign generated
     ↓
Campaign evaluated
     ↓
Revision if required
     ↓
Human approval
     ↓
Image + video generation
     ↓
Assets stored
     ↓
Final system evaluation
```

## Cost Tracking

The system tracks media generation usage at the campaign level.

Tracked information includes:

- Campaign run
- Media type
- Provider/model
- Generation cost
- Video duration where applicable

Media usage is persisted in the database through the `media_usage` table.

## Database & Persistence

SQLAlchemy is used to persist campaign and generation data.

Key database entities include:

- `brand_profiles`
- `campaign_runs`
- `revision_history`
- `generated_assets`
- `system_evaluations`
- `llm_usage`
- `media_usage`

This allows campaign runs, revisions, generated assets, and usage information to remain associated with their originating campaign.

## Testing

The application has been tested through the complete campaign workflow, including:

- Brand context collection
- Brand profile creation
- Campaign generation
- Brand evaluation
- Campaign evaluation
- Revision workflow
- Human approval
- Image generation
- Multi-shot video generation
- Video scene and duration validation
- Media usage tracking
- Generated asset persistence

An end-to-end test successfully generated both an image and a multi-shot campaign video from an approved campaign.

## Limitations

- Campaign and creative quality depends partly on the underlying LLM and media generation providers.
- AI-generated content may require human review before publication.
- Media generation depends on external APIs and associated costs.
- Video generation is subject to provider-specific constraints such as supported durations and prompt limits.
- The current application is intended as a project/prototype implementation rather than a production-scale deployment.

## Future Improvements

- Additional media generation providers
- More platform-specific campaign optimization
- Expanded campaign analytics
- Production deployment and scaling

## Author

Built as an end-to-end exploration of agentic AI workflows, structured LLM outputs, evaluation and revision loops, human-in-the-loop systems, and AI-generated creative assets.

**Author:** Shailja Sharma


