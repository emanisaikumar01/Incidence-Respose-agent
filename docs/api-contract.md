# RecallOps API Contract

Status: Draft — memory interfaces confirmed; backend API contract pending final agreement.

## 1. Purpose

Define how the backend, Hindsight memory retrieval, and AI
recommendation component communicate.

## 2. New incident workflow

1. The engineer submits a new incident through the frontend.
2. The backend receives the incident details.
3. The backend calls `recall_similar(incident_text)`.
4. Hindsight returns relevant past cases, if available.
5. The AI recommendation component uses the current incident
   and recalled cases to generate troubleshooting suggestions.
6. The backend returns the recommendation to the frontend.
7. The engineer reviews the recommendation and tries the fix.
8. The outcome is submitted and recorded through
   `record_outcome(incident_id, fix, worked)`.

Operational changes must remain under human review and approval.

## 3. Memory retrieval interface
The team will use nexora-incidents as the agreed Hindsight bank ID.

### Function

`recall_similar(incident_text)` 

### Input

- `incident_text`: string describing the current incident.

### Output

A list of past cases. Each case contains:

- `memory_id`: identifier for the recalled memory.
- `text`: text describing the past case.

Illustrative output:

    [
      {
        "memory_id": "example-memory-id",
        "text": "Checkout returned HTTP 503 after deployment..."
      }
    ]

The example ID and text are placeholders, not actual Hindsight data.

### Empty results

If no relevant memories are found, continue using the current
incident alone. Do not invent past cases.

### Retrieval errors

If Hindsight fails, report the retrieval failure clearly.
Do not claim that memories were successfully retrieved.

## 4. AI recommendation interface

The AI recommendation component receives:

- The current incident.
- The list of recalled past cases, which may be empty.

**Recommendation generation — Member 3**
The backend calls `recall_similar(incident_text)` to retrieve relevant past incidents. It passes the current incident and recalled cases to the LLM to generate the troubleshooting recommendation. The memory module handles Hindsight retrieval and outcome recording; it does not generate the LLM recommendation.
The recommendation uses the available information, which may include an empty list of recalled cases.

It generates a troubleshooting recommendation using the
available information.

The exact function name, input schema, and output schema
must be confirmed with the AI component owner.

If the LLM fails, show an error or defined fallback. Do not
fabricate a recommendation or claim that it succeeded.

## 5. Outcome recording interface

### Function

`record_outcome(incident_id, fix, worked)`

### Inputs

- `incident_id`: identifier of the incident being resolved.
- `fix`: description of the fix attempted by the engineer.
- `worked`: boolean indicating the outcome.

### Outcome meaning

- `True`: the fix resolved the incident.
- `False`: the incident remains unresolved.

Only record an outcome based on information provided by the
engineer or otherwise verified. Do not invent outcomes.

## 6. Integration responsibilities

- Member 2: Hindsight memory retrieval and agent integration.
- AI component owner: recommendation generation using the
  current incident and recalled memories.
- Member 3: backend endpoints, validation, and integration
  with the agreed functions.
- Member 4: frontend forms and presentation.
- Member 5: sample incidents, testing, and demo.
- System Architect / Integration Lead: maintain this contract,
  coordinate interface agreement, and verify end-to-end behavior.

## 7. Error handling requirements

- No memories: continue with the current incident alone.
- Hindsight unavailable: report the retrieval failure honestly.
- LLM unavailable: show a clear error or defined fallback.
- Outcome not provided: do not assume that a fix worked.
- Never execute production fixes automatically.

## 8. Remaining items to confirm

- [ ] Exact backend endpoint paths and HTTP methods.
- [ ] Full incident request and response JSON schemas.
- [ ] Exact AI recommendation function and output schema.
- [ ] How memory retrieval failures are represented to the backend.
- [ ] How the outcome is submitted from the frontend.
- [ ] Who assigns `incident_id` and `memory_id`.
