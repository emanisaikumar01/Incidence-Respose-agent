# RecallOps — Integration Test Plan

## Purpose

Verify that the RecallOps frontend, backend, agent, Hindsight memory, and LLM work together correctly.

## Test 1: New incident with relevant past memory

- **Input:** The sample checkout HTTP 503 incident.
- **Action:** Submit the incident through the application.
- **Expected result:** Relevant past cases are returned when available, and the agent provides troubleshooting recommendations based on the current incident and retrieved context.
- **Pass criteria:** The recommendation is displayed without claiming that unavailable memories were retrieved.

## Test 2: No relevant memories

- **Input:** An incident with no relevant stored cases.
- **Action:** Submit the incident.
- **Expected result:** The system continues using the current incident alone.
- **Pass criteria:** No past cases are invented or presented as retrieved memories.

## Test 3: Hindsight unavailable

- **Input:** A valid incident while memory retrieval is unavailable.
- **Action:** Submit the incident.
- **Expected result:** The retrieval failure is reported clearly.
- **Pass criteria:** The system does not claim memory retrieval succeeded or fabricate recalled cases.

## Test 4: LLM unavailable

- **Input:** A valid incident while the LLM request fails.
- **Action:** Submit the incident.
- **Expected result:** A clear error or agreed fallback is displayed.
- **Pass criteria:** The application does not silently fail or claim a recommendation was generated when it was not.

## Test 5: Record fix outcome

- **Input:** An incident ID, a description of the attempted fix, and the engineer's reported result.
- **Action:** Submit the outcome.
- **Expected result:** The outcome is recorded using the agreed interface.
- **Pass criteria:** `worked=true` means resolved; `worked=false` means unresolved. The system does not assume an outcome that the engineer did not report.

## Test 6: Human approval

- **Input:** A troubleshooting recommendation.
- **Action:** Review the recommendation.
- **Expected result:** The engineer decides whether to try the suggested fix.
- **Pass criteria:** The application does not automatically execute production changes.

## Test 7: End-to-end workflow

- **Action:** Submit an incident, retrieve memory, generate a recommendation, review and try a fix, and record the outcome.
- **Expected result:** The complete workflow succeeds.
- **Pass criteria:** Each step behaves as specified, and failures are clearly reported.

## Test status

Mark each test as **Pass**, **Fail**, or **Blocked** only after running it. Do not mark untested behavior as passed.

## Notes

- Run these tests once the relevant components are integrated.
- Record the observed result and any bug for each failed test.
- Use fictional or approved test data; do not expose API keys, passwords, or sensitive production logs.
