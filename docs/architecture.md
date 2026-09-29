# RecallOps — System Architecture

## 1. Project Overview

RecallOps is an AI-assisted incident response agent. It uses Hindsight as a memory layer to recall relevant past incidents, their root causes, attempted fixes, and outcomes. An LLM uses the current incident and recalled cases to suggest troubleshooting steps.

## 2. Problem We Solve

Engineers often investigate recurring incidents from scratch. RecallOps aims to make previous incident knowledge useful when similar incidents happen again.

## 3. Architecture

         +----------------------+
         |    Engineer / User   |
         +----------------------+
                    |
                    v
         +----------------------+
         |    Frontend UI       |
         |    Member 4          |
         +----------------------+
                    |
              HTTP API calls
                    |
                    v
         +----------------------+
         |    Backend API       |
         |    Member 3          |
         +----------------------+
                    |
             Calls agent
                    |
                    v
         +----------------------+
         | Python Agent Core    |
         | Member 2              |
         +----------------------+
                /          \
               v            v

+----------------+ +------------------+
| Hindsight Cloud| | LLM Provider |
| Incident Memory| | Groq / alternative|
+----------------+ +------------------+
^
|
Retain incident and
engineer-reported outcome
|
+---- Agent Core

The engineer reviews recommendations, tries a suitable fix,
and reports whether it worked. The application records the
incident and outcome through the agreed agent interface.

The backend, agent, Hindsight, and LLM responsibilities are
separate. Exact API endpoints and function schemas remain
subject to team agreement.

All operational changes require human review and approval.

The agent core coordinates the workflow. Hindsight and the LLM are separate services used by the agent.

## 4. Component Responsibilities

### User Interface

- Accept incident details and logs.
- Display the incident summary and recommended troubleshooting steps.
- Show relevant past incidents when available.
- Allow the engineer to record whether a suggested fix worked.

### Python Agent Core

- Validate incoming incident details.
- Request relevant past cases from the memory layer.
- Build a prompt using the current incident and recalled cases.
- Call the configured LLM and return a structured suggestion.
- Record the engineer's reported outcome through the memory layer.

### Hindsight Memory Layer

- Retain incident details, root causes, attempted fixes, and outcomes.
- Recall relevant past incidents for a new incident.
- Make previous incident knowledge available to the agent.

### LLM Provider

- Analyze the current incident together with relevant recalled cases.
- Suggest possible causes and troubleshooting steps.
- Clearly distinguish evidence from uncertainty.

## 5. Incident Workflow

1. The engineer submits incident details or logs.
2. The agent validates the input.
3. The agent asks Hindsight for relevant past incidents.
4. The agent sends the current incident and recalled cases to the LLM.
5. The agent returns a summary, possible cause, and recommended steps.
6. The engineer reviews and tries a suitable fix.
7. The engineer records whether the fix worked.
8. The agent retains the incident and outcome through Hindsight.
9. A future similar incident can recall this experience.

## 6. Error Handling

- If no relevant past cases are found, analyze the current incident without claiming that memory found a match.
- If Hindsight is unavailable, report that memory could not be accessed; do not invent recalled cases.
- If the LLM request fails, show a clear error and allow a retry.
- Validate user input and handle missing or malformed fields.

## 7. Safety

RecallOps provides recommendations only. It must not automatically execute production changes. Engineers are responsible for reviewing and approving operational actions. Logs and prompts must not expose API keys, passwords, or other secrets.

## 8. MVP Scope

- Submit incident details or logs.
- Recall relevant past cases using Hindsight.
- Generate troubleshooting recommendations using an LLM.
- Record the outcome of a fix.
- Demonstrate that a later similar incident can benefit from retained experience.

## 9. Technology Choices

- Language: Python
- Memory: Hindsight (required by the hackathon brief)
- LLM: Groq or another provider permitted by the event
- User interface: to be confirmed by the team

The exact Hindsight SDK/API calls and the final UI framework will be documented once verified and agreed by the team.
