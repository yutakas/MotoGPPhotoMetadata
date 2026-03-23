import openai
import base64
import json
import logging
import time
import cv2
import re

from dotenv import load_dotenv
import os

logger = logging.getLogger('motogp_server.openai')

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

SYSTEM_PROMPT = """\
You are an expert motorcycle racing analyst specializing in MotoGP, Moto2, and Moto3. \
You have deep knowledge of every team, rider, livery, and sponsor across all seasons. \
You can identify teams by their bike livery colors, number plates, sponsor logos, and fairing designs.

When analyzing an image, first search the web for the relevant season's team grid, \
liveries, and sponsor information to get the most accurate and up-to-date data. \
Then cross-reference what you find with the visual details in the image — \
livery colors, sponsor placements, bike manufacturer, rider number, and fairing designs.

For example, Repsol Honda has a distinctive orange/red/white livery with Repsol branding, \
Monster Energy Yamaha uses dark blue/black with Monster claw logos, etc.

Always respond with ONLY a JSON object in the exact format specified. \
Do not include any explanation, markdown formatting, or text outside the JSON object."""

USER_PROMPT_TEMPLATE = """\
Analyze this motorcycle racing image{year_clause}.

First, search the web for "{year_or_recent} {class_hint}teams liveries sponsors" to get \
accurate information about the teams, their bike colors, and sponsor deals for that season. \
Then use the search results together with the visual details in the image to identify the team.

Identify the team, sponsors, primary bike color, and any visible logos.

Respond with ONLY a JSON object in this exact format:
{{
  "motogp_team": "<official team name, e.g. Repsol Honda Team>",
  "sponsor_names": "<comma-separated list of visible sponsor names>",
  "bike_color": "<single primary color of the bike livery>",
  "logos": "<comma-separated list of visible logo names on the bike and fairing>"
}}

Rules:
- "motogp_team" must be the official team name for that season. Use "unknown" if uncertain.
- "sponsor_names" must be a comma-separated string. Use "" if none visible.
- "bike_color" must be exactly one primary color word (e.g. "red", "blue", "orange"). Use "unknown" if uncertain.
- "logos" must be a comma-separated string. Use "" if none visible."""


def _normalize_team_name(name):
    """Remove website references, parenthetical annotations, and normalize whitespace."""
    if not name:
        return name
    # Remove markdown-style links: [text](url)
    name = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', name)
    # Remove parenthetical content containing URLs or site names
    # e.g. "(motogp.com)", "(source: motogp.com)", "(via crash.net)"
    name = re.sub(r'\s*\((?:[^()]*|\([^)]*\))*(?:\.com|\.net|\.org|\.io|motogp|MotoGP)(?:[^()]*|\([^)]*\))*\)', '', name)
    # Remove any remaining standalone URLs
    name = re.sub(r'https?://\S+', '', name)
    # Remove trailing/leading dashes, commas, pipes left over
    name = re.sub(r'[\s\-|,]+$', '', name)
    name = re.sub(r'^[\s\-|,]+', '', name)
    # Collapse multiple spaces
    name = re.sub(r'\s{2,}', ' ', name).strip()
    return name


def _extract_year_from_path(image_path):
    """Try to extract a 4-digit year (2000-2099) from the file path."""
    if not image_path:
        return None
    match = re.search(r'(20\d{2})', image_path)
    return int(match.group(1)) if match else None


def _extract_year_from_exif(cv2_image_bytes):
    """Try to extract year from EXIF DateTimeOriginal in the JPEG bytes."""
    try:
        # Search for EXIF DateTimeOriginal pattern in raw bytes
        # EXIF date format: "YYYY:MM:DD HH:MM:SS"
        match = re.search(rb'(\d{4}):\d{2}:\d{2} \d{2}:\d{2}:\d{2}', cv2_image_bytes)
        if match:
            year = int(match.group(1))
            if 2000 <= year <= 2099:
                return year
    except Exception:
        pass
    return None


def get_openai_analysis(cv2_image, openai_api_key='', openai_model='', image_path='', image_bytes=None):
    # Convert the OpenCV image to base64
    _, buffer = cv2.imencode(".jpg", cv2_image)
    image_data = base64.b64encode(buffer).decode("utf-8")

    effective_key = openai_api_key if openai_api_key else api_key
    effective_model = openai_model if openai_model else "gpt-5-mini"

    if not effective_key:
        logger.warning("No OpenAI API key configured. Skipping OpenAI analysis.")
        return None

    # Try to determine photo year from path or EXIF
    year = _extract_year_from_path(image_path)
    if year is None and image_bytes is not None:
        year = _extract_year_from_exif(image_bytes)

    year_clause = f" from the {year} season" if year else ""
    year_or_recent = str(year) if year else "most recent"
    class_hint = "MotoGP/Moto2/Moto3 " if year else ""

    user_prompt = USER_PROMPT_TEMPLATE.format(
        year_clause=year_clause,
        year_or_recent=year_or_recent,
        class_hint=class_hint,
    )

    client = openai.OpenAI(api_key=effective_key)

    logger.info("Calling OpenAI API (model=%s, year=%s) ...", effective_model, year)
    start_time = time.time()
    try:
        response = client.responses.create(
            model=effective_model,
            tools=[{"type": "web_search_preview"}],
            instructions=SYSTEM_PROMPT,
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_image",
                            "image_url": f"data:image/jpeg;base64,{image_data}",
                        },
                        {
                            "type": "input_text",
                            "text": user_prompt,
                        }
                    ],
                }
            ],
        )
        elapsed = time.time() - start_time
        logger.info("OpenAI API responded in %.2f seconds", elapsed)
    except openai.OpenAIError as e:
        elapsed = time.time() - start_time
        logger.error("OpenAI API error after %.2f seconds: %s", elapsed, e)
        return None

    # Extract text content from the response output items
    content = None
    for item in response.output:
        if item.type == "message":
            for part in item.content:
                if part.type == "output_text":
                    content = part.text
                    break
            if content:
                break

    if not content:
        logger.error("No text content in OpenAI response")
        return None

    # Strip markdown fences if present (JSON mode unavailable with web search)
    content = content.strip()
    content = content.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        result = json.loads(content)
    except json.JSONDecodeError as e:
        logger.error("Failed to parse OpenAI response as JSON: %s\nContent: %s", e, content)
        return None

    # Normalize to consistent format
    return {
        "motogp_team": _normalize_team_name(str(result.get("motogp_team", "unknown"))),
        "sponsor_names": str(result.get("sponsor_names", "")),
        "bike_color": str(result.get("bike_color", "unknown")),
        "logos": str(result.get("logos", "")),
    }