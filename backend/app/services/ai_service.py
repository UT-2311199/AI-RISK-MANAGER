# =============================================================================
# services/ai_service.py — Google Gemini AI Integration
# =============================================================================
# This is the BRAIN of the entire application.
# It does 3 things:
#   1. Builds a detailed prompt describing what we want Gemini to analyze
#   2. Sends the project info to Gemini and asks for structured risk data
#   3. Parses Gemini's JSON response into Python objects we can save to the DB
#
# KEY CONCEPT: Prompt Engineering
# ────────────────────────────────
# We don't just ask Gemini "what are the risks?"
# We write a very precise, structured prompt that tells Gemini:
#   - Exactly what risk categories to look for
#   - What fields to include for each risk
#   - What format to return the response in (JSON)
#   - What scoring methodology to use
#
# This converts a general-purpose LLM into a specialized Risk Analyst.
# =============================================================================

from google import genai
from google.genai import types
# google.genai is the updated, officially supported Gemini Python SDK.
# 'types' provides configuration classes like GenerateContentConfig.

import json
# json module lets us:
#   - json.loads(string) → parse a JSON string into a Python dict/list
#   - json.dumps(obj) → convert a Python dict/list into a JSON string

import os
# For reading GEMINI_API_KEY from environment variables.

import re
# Regular expressions — we use this to extract JSON from Gemini's response
# even if Gemini wraps it in markdown code blocks like ```json ... ```

from dotenv import load_dotenv
# Load .env file.

from typing import List, Dict, Any
# Type hints for function signatures.
# List[Dict] = a list of dictionaries (our risks list).
# Any = any type (flexible).

load_dotenv()
# Read .env file into environment variables.

# ─────────────────────────────────────────────────────────────────────────────
# Configure Gemini API
# ─────────────────────────────────────────────────────────────────────────────

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# Read the API key from .env file.
# If GEMINI_API_KEY is not set, this returns None.

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found in environment variables. "
        "Please add it to your .env file."
    )
# Fail early with a clear error message if the key is missing.
# This prevents confusing 'API auth failed' errors later during a request.

client = genai.Client(api_key=GEMINI_API_KEY)
# Creates a Gemini API client using the new google.genai SDK.
# The client is reused for every API call (connection pooling).


# ─────────────────────────────────────────────────────────────────────────────
# Probability and Impact Score Mapping
# ─────────────────────────────────────────────────────────────────────────────

PROBABILITY_SCORES = {
    "Low": 2,
    "Medium": 5,
    "High": 8,
}
# Maps text labels to numeric values for the risk score formula.
# Low=2, Medium=5, High=8 — these are chosen to produce a 1-10 final score.

IMPACT_SCORES = {
    "Low": 1,
    "Medium": 2,
    "High": 3,
}
# Maps impact labels to multiplier values.
# Low=1, Medium=2, High=3 — used in the formula below.

# Risk Score Formula: (Probability × Impact) / max_possible × 10
# Max possible: probability=High(8) × impact=High(3) = 24
# Example: Medium probability × High impact = 5 × 3 = 15 → 15/24 × 10 = 6.25

def calculate_risk_score(probability: str, impact: str) -> float:
    """
    Calculates a 1-10 risk score from probability and impact labels.

    This ensures consistent scoring — we don't let the AI decide the score
    (which would be inconsistent). Instead, AI provides probability + impact
    labels, and WE calculate the final numeric score deterministically.

    Args:
        probability: "Low", "Medium", or "High"
        impact:      "Low", "Medium", or "High"

    Returns:
        Risk score as a float between 1.0 and 10.0
    """
    prob_score = PROBABILITY_SCORES.get(probability, 5)
    # .get(key, default) → if probability is not in the dict, use 5 (Medium).
    # This handles cases where AI returns an unexpected value.

    impact_score = IMPACT_SCORES.get(impact, 2)
    # Same safety fallback for impact.

    raw_score = prob_score * impact_score
    # Raw score range: 2×1=2 (min) to 8×3=24 (max).

    normalized = (raw_score / 24) * 10
    # Normalize to 0-10 range by dividing by max possible (24) then × 10.

    return round(normalized, 1)
    # Round to 1 decimal place. e.g., 6.25 → 6.3


def determine_severity(risk_score: float) -> str:
    """
    Converts a numeric risk score to a severity label.

    Score Ranges:
        0.0 - 3.3  → "Low"
        3.4 - 6.6  → "Medium"
        6.7 - 8.4  → "High"
        8.5 - 10.0 → "Critical"
    """
    if risk_score >= 8.5:
        return "Critical"
    elif risk_score >= 6.7:
        return "High"
    elif risk_score >= 3.4:
        return "Medium"
    else:
        return "Low"


# =============================================================================
# CORE FUNCTION: Build the AI Prompt
# =============================================================================

def build_risk_analysis_prompt(
    project_name: str,
    description: str,
    objective: str,
    technologies: List[str],
    context: str
) -> str:
    """
    Builds the detailed prompt we send to Gemini.

    This is the most important function for output quality.
    The prompt does the following:
    1. Assigns Gemini a specific ROLE ("you are a senior risk analyst")
    2. Provides full PROJECT CONTEXT
    3. Specifies EXACT RISK CATEGORIES to consider
    4. Defines the EXACT JSON STRUCTURE for the response
    5. Gives EXAMPLES so Gemini understands what we want
    6. Sets CONSTRAINTS (don't invent risks, only real ones)
    """

    tech_list = ", ".join(technologies) if technologies else "Not specified"
    # Convert list ["React", "FastAPI"] to string "React, FastAPI"
    # If no technologies, use a fallback string.

    prompt = f"""You are a senior risk analyst and cybersecurity expert specializing in software projects and business systems.

Analyze the following project information and identify ALL potential risks across multiple categories.

## PROJECT INFORMATION
- **Project Name**: {project_name}
- **Description**: {description or "Not provided"}
- **Business Objective**: {objective or "Not provided"}
- **Technologies Used**: {tech_list}
- **Additional Context**: {context or "No additional context provided"}

## YOUR TASK
Identify between 4 and 8 specific, realistic risks for this project. For each risk, analyze:
1. What could go wrong?
2. How likely is it to happen?
3. How bad would the impact be?
4. What should the team do about it?

## RISK CATEGORIES TO CONSIDER
- **Security**: unauthorized access, data breaches, injection attacks, authentication flaws
- **Privacy**: GDPR/CCPA compliance, PII exposure, data minimization
- **Technical**: scalability, technical debt, integration failures, performance issues
- **Financial**: budget overrun, revenue loss, unexpected costs
- **Operational**: process failures, dependency on key people, infrastructure downtime
- **Compliance**: regulatory violations, licensing issues, industry standards
- **Project**: scope creep, timeline risks, resource constraints, requirement changes
- **AI/Ethical**: bias, hallucination, explainability, AI misuse

## PROBABILITY SCALE
Use ONLY these exact values: "Low", "Medium", "High"
- Low: unlikely to occur (< 30% chance)
- Medium: may occur (30-70% chance)
- High: likely to occur (> 70% chance)

## IMPACT SCALE
Use ONLY these exact values: "Low", "Medium", "High"
- Low: minor inconvenience, easily recoverable
- Medium: significant disruption, recovery takes time/resources
- High: severe consequences, business-critical damage or legal issues

## REQUIRED JSON RESPONSE FORMAT
Return ONLY a valid JSON array with NO markdown, NO explanation text, NO code blocks.
Your entire response must be ONLY the JSON array starting with [ and ending with ].

[
  {{
    "title": "Short, specific risk name (5-10 words)",
    "category": "One of: Security, Privacy, Technical, Financial, Operational, Compliance, Project, AI/Ethical",
    "probability": "Low OR Medium OR High",
    "impact": "Low OR Medium OR High",
    "explanation": "2-3 sentences explaining what the risk is, why it applies to this project, and what triggers it.",
    "mitigation": [
      "Specific action item 1",
      "Specific action item 2",
      "Specific action item 3",
      "Specific action item 4"
    ]
  }}
]

## IMPORTANT RULES
- Return ONLY the JSON array. No introduction, no conclusion, no markdown.
- All mitigation items must be SPECIFIC and ACTIONABLE (not generic advice).
- The explanation must reference this specific project's context.
- Do NOT invent risks that have no basis in the provided information.
- Ensure mitigation strategies are practical for the project's apparent team size and maturity.
"""
    return prompt
    # We return the complete prompt string. It will be sent to Gemini as-is.
    # The f-string (f"...") lets us embed Python variables using {variable_name}.


# =============================================================================
# CORE FUNCTION: Parse Gemini's Response
# =============================================================================

def parse_ai_response(response_text: str) -> List[Dict[str, Any]]:
    """
    Extracts and parses the JSON array from Gemini's response text.

    Why do we need this?
    Gemini might return:
      - Pure JSON: [{"title": "..."}]  ← ideal
      - JSON wrapped in code block: ```json\n[...]\n```  ← common
      - JSON with extra text before/after  ← sometimes happens

    This function handles all these cases robustly.

    Args:
        response_text: Raw text string from Gemini API.

    Returns:
        List of risk dictionaries parsed from JSON.

    Raises:
        ValueError: If no valid JSON array can be extracted.
    """

    # Strategy 1: Try to parse the entire response as JSON directly.
    try:
        data = json.loads(response_text.strip())
        # .strip() removes leading/trailing whitespace and newlines.
        # json.loads() parses JSON string → Python object.
        if isinstance(data, list):
            # isinstance(data, list) → checks if the result is a list.
            return data
            # 
    except json.JSONDecodeError:
        pass
        # If this fails, move on to Strategy 2. Don't crash.

    # Strategy 2: Extract JSON from markdown code blocks.
    # Gemini sometimes wraps JSON in: ```json\n...\n``` or ```\n...\n```
    code_block_pattern = r'```(?:json)?\s*([\s\S]*?)```'
    # Regex explanation:
    # ```        → literal backticks (opening code block)
    # (?:json)?  → optional word "json" (non-capturing group)
    # \s*        → any whitespace (spaces, newlines)
    # ([\s\S]*?) → capture group: any character including newlines (non-greedy)
    # ```        → literal backticks (closing code block)

    matches = re.findall(code_block_pattern, response_text)
    # re.findall() returns all matches as a list of captured groups.

    for match in matches:
        try:
            data = json.loads(match.strip())
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            continue
            # If this match isn't valid JSON, try the next one.

    # Strategy 3: Find anything that looks like a JSON array [...]
    array_pattern = r'\[[\s\S]*\]'
    # \[  → literal opening bracket
    # [\s\S]* → anything (including newlines)
    # \]  → literal closing bracket

    match = re.search(array_pattern, response_text)
    # re.search() finds the FIRST occurrence of the pattern in the text.

    if match:
        try:
            data = json.loads(match.group())
            # match.group() → returns the matched string.
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            pass

    # If all strategies fail, raise an error.
    raise ValueError(f"Could not extract valid JSON array from AI response. Raw response: {response_text[:500]}")
    # Include first 500 chars of the response in the error for debugging.


# =============================================================================
# CORE FUNCTION: Validate and Normalize AI Risk Data
# =============================================================================

VALID_CATEGORIES = {"Security", "Privacy", "Technical", "Financial", "Operational", "Compliance", "Project", "AI/Ethical"}
VALID_PROBABILITY_IMPACT = {"Low", "Medium", "High"}
# These sets define acceptable values. We use them to validate AI output.

def validate_and_normalize_risk(raw_risk: Dict[str, Any], index: int) -> Dict[str, Any]:
    """
    Validates a single risk dict from AI output and fills in safe defaults.

    The AI might occasionally return slightly different field names or values.
    This function ensures every risk has all required fields with valid values.

    Args:
        raw_risk: Single risk dictionary from AI JSON response.
        index: Position in the risks list (used for default title).

    Returns:
        Normalized risk dictionary with all required fields.
    """

    title = str(raw_risk.get("title", f"Risk #{index + 1}")).strip()
    # .get("title", fallback) → get "title" from dict, or use fallback if missing.
    # str(...).strip() → ensure it's a string and remove whitespace.

    category = raw_risk.get("category", "Technical")
    if category not in VALID_CATEGORIES:
        # If AI returned an unknown category, default to "Technical".
        category = "Technical"

    probability = raw_risk.get("probability", "Medium")
    if probability not in VALID_PROBABILITY_IMPACT:
        probability = "Medium"
    # Same normalization for probability.

    impact = raw_risk.get("impact", "Medium")
    if impact not in VALID_PROBABILITY_IMPACT:
        impact = "Medium"

    explanation = str(raw_risk.get("explanation", "Risk identified during AI analysis.")).strip()

    # Handle mitigation — it should be a list of strings.
    mitigation = raw_risk.get("mitigation", [])
    if not isinstance(mitigation, list):
        # If AI returned a string instead of a list, wrap it in a list.
        mitigation = [str(mitigation)]
    mitigation = [str(item).strip() for item in mitigation if item]
    # List comprehension: convert each item to string, strip whitespace,
    # filter out empty items.

    risk_score = calculate_risk_score(probability, impact)
    # Calculate the numeric score from our deterministic formula.
    # We ignore any "risk_score" the AI may have returned.
    # This ensures consistency across all risks.

    severity = determine_severity(risk_score)
    # Derive severity label from the calculated score.

    return {
        "title": title,
        "category": category,
        "probability": probability,
        "impact": impact,
        "risk_score": risk_score,
        "severity": severity,
        "explanation": explanation,
        "mitigation": mitigation,
    }


# =============================================================================
# MAIN FUNCTION: Analyze Project Risks with Gemini
# =============================================================================

async def analyze_project_risks(
    project_name: str,
    description: str = "",
    objective: str = "",
    technologies: List[str] = None,
    context: str = ""
) -> List[Dict[str, Any]]:
    """
    Main entry point for AI risk analysis.

    This function orchestrates the entire AI pipeline:
    1. Build the prompt from project data
    2. Send prompt to Gemini API
    3. Parse the JSON response
    4. Validate and normalize each risk
    5. Return clean list of risk dicts ready for database storage

    Args:
        project_name: Name of the project being analyzed.
        description:  What the project does.
        objective:    Business goal of the project.
        technologies: List of technologies used.
        context:      Additional context for more targeted analysis.

    Returns:
        List of validated risk dictionaries.

    Raises:
        Exception: If the API call fails or response cannot be parsed.

    Note: This is an 'async' function because FastAPI routes are async.
    However, the Gemini SDK call itself is synchronous — in a production app
    you'd want to use run_in_executor for true async. For our purposes, this works.
    """

    technologies = technologies or []
    # If technologies is None, use an empty list to avoid errors.

    # Step 1: Build the prompt
    prompt = build_risk_analysis_prompt(
        project_name=project_name,
        description=description,
        objective=objective,
        technologies=technologies,
        context=context
    )

    # Step 2: Send prompt to Gemini using the new google.genai SDK (with resilient fallback)
    models_to_try = ["gemini-2.5-flash", "gemini-flash-latest", "gemini-2.5-flash-lite", "gemini-flash-lite-latest"]
    last_error = None
    response_text = None

    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    top_p=0.8,
                    max_output_tokens=4096,
                ),
            )
            if response and response.text:
                response_text = response.text
                break
        except Exception as e:
            last_error = e
            continue

    if not response_text:
        raise Exception(f"Gemini API call failed: {str(last_error)}")

    # Step 3: Parse the JSON from Gemini's response
    try:
        raw_risks = parse_ai_response(response_text)
    except ValueError as e:
        raise Exception(f"Failed to parse AI response: {str(e)}")

    # Step 4: Validate and normalize each risk
    validated_risks = []
    for index, raw_risk in enumerate(raw_risks):
        # enumerate() gives us both the index (0, 1, 2...) and the item.
        if isinstance(raw_risk, dict):
            # Only process items that are dictionaries (skip malformed items).
            validated_risk = validate_and_normalize_risk(raw_risk, index)
            validated_risks.append(validated_risk)

    if not validated_risks:
        # If we got zero valid risks, something went wrong.
        raise Exception("AI analysis returned no valid risks. Please try again.")

    return validated_risks
    # Returns a list like:
    # [
    #   {
    #     "title": "Sensitive Data Exposure",
    #     "category": "Security",
    #     "probability": "High",
    #     "impact": "High",
    #     "risk_score": 10.0,
    #     "severity": "Critical",
    #     "explanation": "...",
    #     "mitigation": ["...", "..."]
    #   },
    #   ...
    # ]
