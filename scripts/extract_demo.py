import os
import json
import re
from datetime import datetime

from generate_agent_spec import generate_agent_spec


# ---------------------------
# Generate account_id from company
# ---------------------------
def generate_account_id(company_name):
    slug = re.sub(r'[^a-z0-9]+', '_', company_name.lower())
    slug = re.sub(r'_+', '_', slug).strip('_')
    return slug


# ---------------------------
# Extract data from demo transcript
# ---------------------------
def extract_data(transcript):

    memo = {
        "metadata": {
            "account_id": None,
            "company_name": None,
            "source": "demo_call",
            "version": "v1",
            "created_at": str(datetime.now())
        },
        "business_profile": {
            "office_address": None,
            "timezone": None,
            "services_supported": []
        },
        "business_hours": {
            "days_open": [],
            "start_time": None,
            "end_time": None
        },
        "emergency_handling": {
            "emergency_definition": []
        },
        "integration_constraints": [],
        "questions_or_unknowns": []
    }

    text = transcript.lower()

    # Extract company name
    match = re.search(r'from\s+([A-Za-z ]+)', transcript, re.IGNORECASE)
    if match:
        company_name = match.group(1).strip()
        memo["metadata"]["company_name"] = company_name
        memo["metadata"]["account_id"] = generate_account_id(company_name)
    else:
        memo["questions_or_unknowns"].append("Company name not specified")

    # Business days
    if "monday to friday" in text or "monday through friday" in text:
        memo["business_hours"]["days_open"] = [
            "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"
        ]

    # Business hours
    time_match = re.search(r'(\d+\s?[ap]m)\s*to\s*(\d+\s?[ap]m)', text)
    if time_match:
        memo["business_hours"]["start_time"] = time_match.group(1).upper()
        memo["business_hours"]["end_time"] = time_match.group(2).upper()

    # Timezone
    if "eastern" in text:
        memo["business_profile"]["timezone"] = "Eastern Time"
    elif "pacific" in text:
        memo["business_profile"]["timezone"] = "Pacific Time"

    # Emergency triggers
    if "sprinkler leak" in text:
        memo["emergency_handling"]["emergency_definition"].append("sprinkler leak")

    if "fire alarm" in text:
        memo["emergency_handling"]["emergency_definition"].append("fire alarm active")

    return memo


# ---------------------------
# MAIN - Batch Process
# ---------------------------
def main():

    demo_folder = os.path.join("dataset", "demo")
    accounts_folder = os.path.join("outputs", "accounts")

    if not os.path.exists(demo_folder):
        print("❌ Demo folder not found.")
        return

    for filename in os.listdir(demo_folder):

        if not filename.endswith(".txt"):
            continue

        demo_path = os.path.join(demo_folder, filename)

        with open(demo_path, "r", encoding="utf-8") as f:
            transcript = f.read()

        memo = extract_data(transcript)

        account_id = memo["metadata"]["account_id"]

        if not account_id:
            print(f"⚠ Skipping {filename} — no company detected.")
            continue

        account_path = os.path.join(accounts_folder, account_id)
        v1_path = os.path.join(account_path, "v1")

        # Idempotency: skip if already exists
        if os.path.exists(os.path.join(v1_path, "memo.json")):
            print(f"⏩ Skipping {account_id} — already processed.")
            continue

        os.makedirs(v1_path, exist_ok=True)

        # Save memo
        with open(os.path.join(v1_path, "memo.json"), "w", encoding="utf-8") as f:
            json.dump(memo, f, indent=2)

        # Generate agent spec
        agent_spec = generate_agent_spec(memo)

        with open(os.path.join(v1_path, "agent_spec.json"), "w", encoding="utf-8") as f:
            json.dump(agent_spec, f, indent=2)

        print(f"✅ Created v1 for {account_id}")


if __name__ == "__main__":
    main()