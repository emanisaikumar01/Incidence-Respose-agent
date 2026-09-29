# RecallOps Integration Checklist

Status: Draft — confirm interfaces with the team.

## 1. Component ownership

- Member 1: System Architect / Integration Lead
- Member 2: Hindsight memory and incident-response agent.
- Member 3: Backend API and application integration.
- Member 4: Frontend and user interactions.
- Member 5: Sample incidents, testing, and demo.
- System Architect / Integration Lead: Architecture, interface
  agreements, coordination, integration review, and end-to-end testing.

## 2. Proposed data flow

1. Engineer submits an incident through the frontend.
2. Backend passes the incident to the agent.
3. Agent retrieves relevant past incidents from Hindsight.
4. Agent uses the current incident and recalled context to
   generate troubleshooting suggestions.
5. Backend returns the suggestion to the frontend.
6. Engineer reviews and tries a suggested fix.
7. Engineer submits the outcome.
8. The application records the incident and outcome in Hindsight.

All operational changes remain under human review and approval.

## 3. Interfaces to confirm

### Member 2 — Agent interface

- [✓] Confirm memory retrieval function: `recall_similar(incident_text)`.
- [✓] Confirm recalled case format: list of objects containing `memory_id` and `text`.
- [✓] Confirm outcome recording function: `record_outcome(incident_id, fix, worked)`.
- [✓] Confirm behavior when no memories are found.
- [✓] Confirm behavior when Hindsight or the LLM fails.
- [ ] Confirm the AI recommendation function name and input/output schema.

### Member 3 — Backend interface

- [ ] Confirm API framework and endpoint paths.
- [ ] Confirm request and response JSON formats.
- [✓] Confirm how the backend calls Member 2's agent.
- [ ] Confirm validation and error responses.
- [ ] Confirm who assigns `incident_id`.
- [✓] Generate the complete LLM recommendation using the current incident and recalled cases from `recall_similar()`.

### Member 4 — Frontend interface

- [ ] Confirm incident form fields.
- [ ] Confirm how suggestions and past incidents are displayed.
- [✓] Confirm how engineers submit outcomes.
- [ ] Confirm loading and error states.
- [ ] Confirm how the outcome submission maps to the backend API.

## 4. Proposed acceptance criteria

- [ ] Submit a sample incident successfully.
- [✓] Retrieve relevant past incidents when available.
- [ ] Generate suggestions using the incident and recalled context.
- [ ] Clearly handle cases where no relevant memories are found.
- [ ] Record whether the suggested fix worked.
- [ ] Handle Hindsight or LLM failures without crashing silently.
- [ ] Verify that no API keys are committed to Git.
- [ ] Demonstrate the complete workflow from incident submission
      to outcome recording.

## 5. Integration rule

The interfaces in this document are proposals, not final agreements.
Update them after the responsible teammates confirm their implementation.
