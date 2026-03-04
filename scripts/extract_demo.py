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
        "account_id": None,
        "company_name": None,

        "business_hours": {
            "days": [],
            "start": None,
            "end": None,
            "timezone": None
        },

        "office_address": None,

        "services_supported": [],

        "emergency_definition": [],

        # Structured placeholders (required by assignment)
        "emergency_routing_rules": {
            "transfer_immediately": None,
            "contact_role": None,
            "fallback_action": None
        },

        "non_emergency_routing_rules": {
            "collect_details": True,
            "schedule_followup": None
        },

        "call_transfer_rules": {
            "timeout_seconds": None,
            "retry_attempts": None,
            "failure_message": None
        },

        "integration_constraints": [],

        "after_hours_flow_summary": None,

        "office_hours_flow_summary": None,

        "questions_or_unknowns": [],

        "notes": "",

        "metadata": {
            "source": "demo_call",
            "version": "v1",
            "created_at": str(datetime.now())
        }
    }

    text = transcript.lower()

    # ---------------------------
    # Extract company name
    # ---------------------------
    patterns = [
        r'company\s*:\s*(.+)',
        r'from\s+([A-Za-z &]+)',
        r'company\s+is\s+([A-Za-z &]+)',
        r'we(?:\'re| are)\s+([A-Za-z &]+)'
    ]

    company_name = None

    for p in patterns:
        match = re.search(p, transcript, re.IGNORECASE)
        if match:
            company_name = match.group(1).strip()
            break

    if company_name:
        memo["company_name"] = company_name
        memo["account_id"] = generate_account_id(company_name)
    else:
        memo["questions_or_unknowns"].append("Company name not specified")

    # ---------------------------
    # Business days
    # ---------------------------
    if "monday to friday" in text or "monday through friday" in text:
        memo["business_hours"]["days"] = [
            "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"
        ]

    # ---------------------------
    # Business hours
    # ---------------------------
    time_match = re.search(r'(\d+\s?[ap]m)\s*to\s*(\d+\s?[ap]m)', text)
    if time_match:
        memo["business_hours"]["start"] = time_match.group(1).upper()
        memo["business_hours"]["end"] = time_match.group(2).upper()

    # ---------------------------
    # Timezone detection
    # ---------------------------
    if "eastern" in text or "est" in text:
        memo["business_hours"]["timezone"] = "Eastern Time"
    elif "pacific" in text or "pst" in text:
        memo["business_hours"]["timezone"] = "Pacific Time"
    elif "central" in text or "cst" in text:
        memo["business_hours"]["timezone"] = "Central Time"
    elif "mountain" in text or "mst" in text:
        memo["business_hours"]["timezone"] = "Mountain Time"

    # ---------------------------
    # Service detection
    # ---------------------------
    if "sprinkler" in text:
        memo["services_supported"].append("sprinkler systems")

    if "fire alarm" in text:
        memo["services_supported"].append("fire alarm systems")

    if "electrical" in text:
        memo["services_supported"].append("electrical services")

    if "hvac" in text:
        memo["services_supported"].append("hvac services")

    if "inspection" in text:
        memo["services_supported"].append("inspection services")

    # ---------------------------
    # Emergency triggers
    # ---------------------------
    if "sprinkler leak" in text:
        memo["emergency_definition"].append("sprinkler leak")

    if "fire alarm" in text:
        memo["emergency_definition"].append("fire alarm active")

    if "power outage" in text:
        memo["emergency_definition"].append("power outage")

    if "exposed wiring" in text:
        memo["emergency_definition"].append("exposed wiring")

    # ---------------------------
    # Unknown field handling
    # ---------------------------
    if not memo["business_hours"]["start"]:
        memo["questions_or_unknowns"].append("Business hours not specified")

    if not memo["business_hours"]["timezone"]:
        memo["questions_or_unknowns"].append("Timezone not specified")

    if not memo["services_supported"]:
        memo["questions_or_unknowns"].append("Services supported not clearly mentioned")

    if not memo["emergency_definition"]:
        memo["questions_or_unknowns"].append("Emergency triggers not mentioned")

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

        account_id = memo["account_id"]

        if not account_id:
            print(f"⚠ Skipping {filename} — no company detected.")
            continue

        account_path = os.path.join(accounts_folder, account_id)
        v1_path = os.path.join(account_path, "v1")

        memo_file = os.path.join(v1_path, "account_memo.json")

        # Idempotency check
        if os.path.exists(memo_file):
            print(f"⏩ Skipping {account_id} — v1 already exists.")
            continue

        os.makedirs(v1_path, exist_ok=True)

        # Save account memo
        with open(memo_file, "w", encoding="utf-8") as f:
            json.dump(memo, f, indent=2)

        # Generate agent spec
        agent_spec = generate_agent_spec(memo)

        with open(os.path.join(v1_path, "agent_spec.json"), "w", encoding="utf-8") as f:
            json.dump(agent_spec, f, indent=2)

        print(f"✅ Created v1 for {account_id}")


if __name__ == "__main__":
    main()