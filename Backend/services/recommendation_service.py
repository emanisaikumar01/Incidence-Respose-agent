
import re
import sys
from typing import Any

from agent import IncidentResponseAgent

# Windows consoles often use a legacy codepage (cp1252) that cannot encode
# characters LLMs love to emit (em-dashes, curly quotes, non-breaking
# hyphens). Replace them instead of crashing the analysis mid-demo.
try:
    if sys.stdout is not None and sys.stdout.encoding not in ("utf-8", "utf8"):
        sys.stdout.reconfigure(errors="replace")
except Exception:
    pass


# Reuse one agent instance.
incident_agent = IncidentResponseAgent()



def _parse_sections(text: str) -> dict[str, str]:
    """Extract AI response sections, accepting common heading variations."""
    sections = {}
    current_section = None
    lines = []

    headings = {
        "SUMMARY": "summary",
        "LIKELY_ROOT_CAUSE": "possible_cause",
        "POSSIBLE_CAUSE": "possible_cause",
        "ROOT_CAUSE": "possible_cause",
        "EVIDENCE": "evidence",
        "SIMILAR_INCIDENTS": "similar_incidents",
        "RECOMMENDED_ACTIONS": "recommended_action",
        "RECOMMENDED_ACTION": "recommended_action",
        "RECOMMENDED_CHECKS": "recommended_action",
        "PREVENTION": "prevention",
        "CONFIDENCE": "confidence",
    }

    # Match headings such as:
    # SUMMARY:
    # **Summary**
    # **Possible Cause**
    # **Recommended Action:**
    for line in text.splitlines():
        cleaned = line.strip()
        cleaned = re.sub(r"^\s*#+\s*", "", cleaned)
        cleaned = cleaned.replace("**", "").replace("__", "").strip()
        cleaned = cleaned.rstrip(":").strip()

        normalized = re.sub(r"[^A-Za-z0-9]+", "_", cleaned)
        normalized = normalized.strip("_").upper()

        if normalized in headings:
            if current_section:
                sections[current_section] = "\n".join(lines).strip()

            current_section = headings[normalized]
            lines = []
        elif current_section:
            lines.append(line)

    if current_section:
        sections[current_section] = "\n".join(lines).strip()

    return sections



def _clean_text(text: str) -> str:
    """Remove common Markdown formatting from AI-generated text."""
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"(?<!\*)\*(.*?)\*(?!\*)", r"\1", text)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"^\s*[-*_]{3,}\s*$", "", text, flags=re.MULTILINE)
    return text.strip()


def _split_list_items(text: str) -> list[str]:
    """Split bullet points or numbered items into separate entries."""
    text = _clean_text(text)

    # Split numbered items, including when they appear on one line.
    items = re.split(r"(?<!\S)(?=\d+[.)]\s)", text)

    cleaned_items = []
    for item in items:
        item = re.sub(r"^\s*(?:[-*•]|\d+[.)])\s*", "", item)
        item = _clean_text(item)

        if item:
            cleaned_items.append(item)

    return cleaned_items


def generate_recommendation(
    incident: dict[str, Any],
    recalled_cases: list[dict[str, str]],
) -> dict[str, Any]:
    """Generate a recommendation and split it into displayable sections."""
    result = incident_agent.analyze(incident, recalled_cases)

    recommendation = result.get("recommendation")

    if not recommendation:
        raise RuntimeError(
            result.get("error", "AI agent did not return a recommendation.")
        )

    sections = _parse_sections(recommendation)

    evidence = sections.get("evidence", "")
    evidence_items = _split_list_items(evidence)

    recommended_actions = _clean_text(
        sections.get("recommended_action", "")
    )
    recommended_steps = _split_list_items(recommended_actions)

    return {
        "status": result.get("status", "success"),
        "summary": _clean_text(
            sections.get("summary") or recommendation
        ),
        "possible_cause": _clean_text(
            sections.get("possible_cause", "")
        ),
        "root_cause": _clean_text(
            sections.get("possible_cause", "")
        ),
        "evidence": evidence_items,
        "similar_incidents": _clean_text(
            sections.get("similar_incidents", "")
        ),
        "recommended_action": recommended_actions,
        "recommended_steps": recommended_steps,
        "prevention": _clean_text(
            sections.get("prevention", "")
        ),
        "confidence": _clean_text(
            sections.get("confidence", "")
        ),
        "memory_status": result.get("memory_status", "success"),
        "memory_used": bool(recalled_cases),
    }
