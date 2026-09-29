
import os

from dotenv import load_dotenv
from hindsight_client import Hindsight

# Load settings from the local .env file
load_dotenv()

api_key = os.getenv("HINDSIGHT_API_KEY")
base_url = os.getenv(
    "HINDSIGHT_BASE_URL",
    "https://api.hindsight.vectorize.io",
)

if not api_key:
    raise SystemExit(
        "HINDSIGHT_API_KEY is missing. Check your .env file."
    )

# Use the existing RecallOps memory bank.
# This ID is based on the bank URL in your screenshot.
BANK_ID = "recallps"

client = Hindsight(
    base_url=base_url,
    api_key=api_key,
)

# A fictional incident for our first test
incident = (
    "RecallOps demo incident: The checkout service returned "
    "HTTP 503 errors after a deployment. The root cause was "
    "a misconfigured upstream timeout. The engineer rolled "
    "back the deployment, which restored the service."
)

try:
    # Step 1: Store the incident in Hindsight
    client.retain(
        bank_id=BANK_ID,
        content=incident,
    )
    print("SUCCESS: Incident sent to Hindsight.")

    # Step 2: Search for the stored incident
    result = client.recall(
        bank_id=BANK_ID,
        query=(
            "What caused the checkout HTTP 503 incident, "
            "and how was it resolved?"
        ),
    )

    print("\nRecall results:")

    if result.results:
        for memory in result.results:
            print("-", memory.text)
    else:
        print("No matching memories returned yet.")

except Exception as error:
    print(f"Hindsight test failed: {error}")

finally:
    client.close()