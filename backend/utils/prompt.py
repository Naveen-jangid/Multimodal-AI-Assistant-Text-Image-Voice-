"""Prompt engineering helpers for different input modalities."""


def build_food_nutrition_prompt(extra: str = "") -> str:
    base = (
        "Analyze this food image and provide:\n"
        "1. Food identification (what dish/items are present)\n"
        "2. Estimated nutritional information (calories, protein, carbs, fats)\n"
        "3. Key vitamins and minerals\n"
        "4. Health assessment (is this a healthy meal?)\n"
        "5. Serving size estimate\n"
    )
    if extra:
        base += f"\nAdditional question: {extra}"
    return base


def build_voice_followup_prompt(transcription: str) -> str:
    return (
        f"The user asked via voice: \"{transcription}\"\n"
        "Please answer clearly and concisely."
    )


def enrich_prompt(user_input: str, modality: str) -> str:
    """
    Optionally enhance prompts based on detected intent.
    Falls back to the raw input if no special handling is needed.
    """
    lower = user_input.lower()

    if modality == "image":
        food_keywords = {"food", "eat", "meal", "nutrition", "calorie", "diet", "dish", "recipe"}
        if any(kw in lower for kw in food_keywords) or not user_input.strip():
            return build_food_nutrition_prompt(user_input)

    if modality == "voice":
        return build_voice_followup_prompt(user_input)

    return user_input
