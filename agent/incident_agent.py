import os

from dotenv import load_dotenv
from groq import Groq

from memory import recall_similar, record_outcome
from .prompts import INCIDENT_ANALYSIS_PROMPT

load_dotenv()


class GroqLLM:
    """Small adapter around the Groq Chat Completions API."""

    def __init__(
        self,
        model=None,
        temperature=0.2,
    ):
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError("GROQ_API_KEY is not set in .env")

        self.client = Groq(api_key=api_key)
        self.model = model or os.getenv(
            "GROQ_MODEL",
            "openai/gpt-oss-120b",
        )
        self.temperature = temperature

    def generate(self, prompt):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an AI-assisted production "
                        "incident response agent."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=self.temperature,
        )

        return response.choices[0].message.content


class IncidentResponseAgent:
    """
    AI-assisted incident response agent.

    Flow:
    Incident
      -> Hindsight recall
      -> Prompt construction
      -> Groq LLM
      -> Troubleshooting recommendation

    Engineer-confirmed outcomes are written back to Hindsight.

    The agent also supports backend-provided recalled_cases so that
    Hindsight retrieval is not duplicated during backend integration.
    """

    REQUIRED_FIELDS = [
        "incident_id",
        "service",
    ]

    def __init__(self, llm=None):
        self.llm = llm if llm is not None else GroqLLM()

    def validate_incident(self, incident):
        if not isinstance(incident, dict):
            raise ValueError("Incident must be a dictionary.")

        missing = [
            field
            for field in self.REQUIRED_FIELDS
            if not incident.get(field)
        ]

        if missing:
            raise ValueError(
                f"Missing required incident fields: {', '.join(missing)}"
            )

        if not incident.get("symptom") and not incident.get("description"):
            raise ValueError(
                "Either symptom or description is required."
            )

        return True

    def build_incident_text(self, incident):
        return f"""
Incident ID: {incident.get("incident_id")}
Service: {incident.get("service")}
Title: {incident.get("title", "")}
Severity: {incident.get("severity", "")}

Symptom:
{incident.get("symptom", incident.get("description", ""))}

Logs:
{incident.get("logs", "")}

Additional context:
{incident.get("historical_context", "")}
""".strip()

    def retrieve_similar_incidents(self, incident):
        incident_text = self.build_incident_text(incident)
        return recall_similar(incident_text)

    def build_prompt(self, incident, historical_incidents):
        incident_text = self.build_incident_text(incident)

        if historical_incidents:
            historical_text = "\n\n".join(
                f"Memory ID: {item.get('memory_id')}\n"
                f"{item.get('text', '')}"
                for item in historical_incidents
            )
        else:
            historical_text = (
                "No relevant historical incidents were found."
            )

        return INCIDENT_ANALYSIS_PROMPT.format(
            incident=incident_text,
            historical_incidents=historical_text,
        )

    def analyze(self, incident, recalled_cases=None):
        self.validate_incident(incident)

        if recalled_cases is None:
            historical_incidents = self.retrieve_similar_incidents(
                incident
            )
        else:
            historical_incidents = recalled_cases

        prompt = self.build_prompt(
            incident,
            historical_incidents,
        )

        try:
            recommendation = self._call_llm(prompt)
        except Exception as error:
            return {
                "incident": incident,
                "similar_incidents": historical_incidents,
                "memory_status": "success",
                "prompt": prompt,
                "recommendation": None,
                "status": "llm_error",
                "error": str(error),
            }

        return {
            "incident": incident,
            "similar_incidents": historical_incidents,
            "memory_status": "success",
            "prompt": prompt,
            "recommendation": recommendation,
            "status": "success",
        }

    def _call_llm(self, prompt):
        if hasattr(self.llm, "generate"):
            return self.llm.generate(prompt)

        if callable(self.llm):
            return self.llm(prompt)

        raise TypeError(
            "LLM must provide a generate(prompt) "
            "method or be callable."
        )

    def record_engineer_outcome(
        self,
        incident_id,
        fix,
        worked,
    ):
        if not incident_id:
            raise ValueError("incident_id is required.")

        if not fix:
            raise ValueError("fix is required.")

        if not isinstance(worked, bool):
            raise ValueError("worked must be True or False.")

        return record_outcome(
            incident_id=incident_id,
            fix=fix,
            worked=worked,
        )