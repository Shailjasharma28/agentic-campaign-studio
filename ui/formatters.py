def score_bar(score, width=10):
    if score is None:
        return "░" * width

    score = max(0, min(10, float(score)))

    filled = round((score/10)* width)
    empty = width - filled

    return "█" * filled + "░" * empty


def format_list(items):
     if not items:
        return "—"

        return ", ".join(str(item) for item in items)


def format_brand(brand):
    if not brand:
        return "No brand profile available."

    brand_colors = brand.get("brand_colors") or []
    style_keywords = brand.get("style_keywords") or []

    # Make sure these are lists
    if isinstance(brand_colors, str):
        brand_colors = [brand_colors]

    if isinstance(style_keywords, str):
        style_keywords = [style_keywords]

    color_display = " ".join(
    f"`{color}`"for color in brand_colors
    ) if brand_colors else "Not specified"

    keyword_display = " · ".join(
        keyword.title() for keyword in style_keywords
    ) if style_keywords else "Not specified"

    return f"""
## 🏷️ Brand Profile

### {brand.get("brand_name") or "Unnamed Brand"}
**Niche**  
{brand.get("niche") or "Not Specified"}

**👥 Target Audience**  
{brand.get("target_audience") or "Not Specified"}

**💬 Tone of Voice**  
{brand.get("tone_of_voice") or "Not Specified"}

**🎨 Brand Colors**  
{color_display}

**✨ Style Keywords**  
{keyword_display}
"""

# FORMATTING EVALUATION

def format_evaluation(evaluation):
    if not evaluation:
        return "No evaluation available."

    overall = float(evaluation.get("overall_score", 0))
    scores = evaluation.get("scores", {})

    score_lines = []

    for name, score in scores.items():
        score = float(score)
        display_name = name.replace("_", " ").title()

        bar = score_bar(score)

        score_lines.append(
            f"**{display_name}**  \n"
            f"`{bar}` **{score:.1f} / 10**"
        )

    score_breakdown = "\n\n".join(score_lines)

    strengths = "\n".join(
        f"- {item}"
        for item in evaluation.get("strengths", [])
    ) or "- None provided"

    weaknesses = "\n".join(
        f"- {item}"
        for item in evaluation.get("weaknesses", [])
    ) or "- None provided"

    recommendations = "\n".join(
        f"- {item}"
        for item in evaluation.get("recommendations", [])
    ) or "- None provided"

    return f"""
## 🧠 AI Evaluation

### ⭐ Overall Score

# {overall:.1f} / 10

---

### Score Breakdown

{score_breakdown}

---

### ✅ Strengths

{strengths}

---


### ⚠️ Areas for Improvement

{weaknesses}

---


### 💡 Recommendations

{recommendations}
"""


def format_campaign(campaign,brand):
    if not campaign:
        return "No campaign available."

    hashtags = campaign.get("hashtags") or []

    hashtag_display = " ".join(
        f"`{tag}`" for tag in hashtags
    ) if hashtags else "None"

    hashtags= ", ".join(hashtags) if hashtags else "Not Specified"

    return f"""
## 📢 Campaign

### {campaign.get("idea_title") or "Campaign Concept"}

**🏷️ Brand:** {brand.get("brand_name") or "-NO BRAND NAME"}

**Platform:** {campaign.get("platform") or "Not Specified"}

### 💡 Campaign Idea


**Angle**  
{campaign.get("idea_angle") or "Not Specified"}

**🎯 Objective**  
{campaign.get("idea_objective") or "Not Specified"}

---

### 🪝 Hook

> {campaign.get("hook") or "No Hook Generated"}

---


### ✍️ Caption

{campaign.get("caption") or "No Caption Generated"}

---


### 🎯 Call to Action

{campaign.get("cta") or "No CTA Generated"}

---


### #️⃣ Hashtags

{hashtags}

---

### 📌 Posting Instructions

{campaign.get("posting_instructions") or "No Posting Instructions Provided."}
"""

def format_creative_blueprint(campaign):
    if not campaign:
        return "No creative information available."

    # ============================
    # IMAGE
    # ============================

    image_colors = campaign.get("image_colors" ) or []

    image_color_display = ", ".join(
        f"'{color}'" for color in image_colors
    ) if image_colors else "Not Specified"

    # ============================
    # VIDEO
    # ============================

    scenes = campaign.get("video_scenes") or []

    scene_lines = []

    for i, scene in enumerate(scenes, start=1):
        visual = scene.get("visual") or "-"
        camera = scene.get("camera") or "-"
        on_screen_text = scene.get("text") or "-"
        duration = scene.get("duration")
        duration_display = (f"{duration}s" if duration is not None else "-")

        scene_lines.append(
            f"""
**Scene {i} — {duration_display}**

🎬 **Visual:** {visual}
📷 **Camera:** {camera}
- **On-screen text:** {on_screen_text}
"""
        )
    video_scenes = "\n".join(scene_lines) or "No scenes available."
    # Voiceover

    voiceover = campaign.get("video_voiceover") or []
    voiceover_display = "\n".join(
        f"{i}. {item}"
        for i, item in enumerate(voiceover, start=1)) if voiceover else "No Voiceover."
    
    # Transitions
    transitions = campaign.get("video_transitions") or []
    transitions_display = "-> ".join(transitions) if transitions else "Not Specified"

    return f"""
## 🖼️ Image Creative Blueprint

**Visual Style:**- {campaign.get("image_style") or "Not Specified"}

**🎨 Colors:** - {image_color_display}

**💡 Lighting:** - {campaign.get("image_lighting") or "Not Specified"}

**📐 Composition:** - {campaign.get("image_composition") or "Not Specified"}

**😊 Mood:** - {campaign.get("image_mood") or "Not Specified"}

**📏  Aspect Ratio:** - {campaign.get("image_aspect_ratio") or "Not Specified"}

### Image Prompt

> {campaign.get("image_prompt") or "—"}

---

## 🎬 Video Blueprint

**Hook** - {campaign.get("video_hook") or "Not Specified"}

**🎨 Visual Style** - {campaign.get("video_visual_style") or "Not Specified"}

**😊 Mood** - {campaign.get("video_mood") or "Not Specified"}

**📏 Aspect Ratio** - {campaign.get("video_aspect_ratio") or "Not Specified"}

**⏱️ Duration** - {campaign.get("video_duration_seconds") or "Not Specified"} seconds
 
---

### 🎞️ Scenes

{video_scenes}

---


### 🎙️ Voiceover

{voiceover_display}


---


### Transitions

{transitions_display}
"""

# Formatting Campaign Cost

def format_campaign_cost(cost_data):

    if not cost_data:
        return "###💰 Campaign Cost\n\nNo cost data available."

    llm_cost = cost_data["llm_cost"]
    media_cost = cost_data["media_cost"]
    total_cost=cost_data["total_cost"]

    llm_percentage = cost_data["llm_percentage"]
    media_percentage = cost_data["media_percentage"]

    return f"""
    ## 💰 Campaign Cost

### Total Campaign Cost
# ${total_cost:.6f}

| Cost Category | Cost | Share |
|---|---:|---:|
| 🧠 LLM | ${llm_cost:.6f} | {llm_percentage:.2f}% |
| 🎨 Media | ${media_cost:.6f} | {media_percentage:.2f}% |
| **Total** | **${total_cost:.6f}** | **100%** |

### 📊 Cost Breakdown

🧠 LLM — **{llm_percentage:.2f}%**

🎨 Media — **{media_percentage:.2f}%**
"""