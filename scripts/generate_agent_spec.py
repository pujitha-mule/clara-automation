import os
import json
from datetime import datetime


# -----------------------------
# Safe Value Helper
# -----------------------------
def safe(value):
    if value is None or value == [] or value == "":
        return "Not specified"
    return value


# -----------------------------
# Build System Prompt
# -----------------------------
def build_system_prompt(memo):

    company = safe(memo.get("company_name"))

    business_hours = memo.get("business_hours", {})
    timezone = safe(business_hours.get("timezone"))
    business_days = safe(business_hours.get("days"))
    start = safe(business_hours.get("start"))
    end = safe(business_hours.get("end"))

    emergencies = memo.get("emergency_definition", [])
    emergency_text = ", ".join(emergencies) if emergencies else "Not specified"

    services = memo.get("services_supported", [])
    services_text = ", ".join(services) if services else "Not specified"

    prompt = f"""
You are Clara, the AI voice assistant for {company}.

Timezone: {timezone}
Business Hours: {business_days} from {start} to {end}
Supported Services: {services_text}

========================
BUSINESS HOURS FLOW
========================
1. Greet the caller professionally.
2. Ask how you can help.
3. Collect caller name and callback number.
4. Determine if the situation is an emergency ({emergency_text}).
5. If emergency:
   - Transfer immediately to dispatch or technician.
6. If non-emergency:
   - Collect service details and route appropriately.
7. If transfer fails:
   - Apologize and inform the caller that dispatch will follow up shortly.
8. Ask if they need anything else.
9. Close the call politely.

========================
AFTER HOURS FLOW
========================
1. Greet caller and inform office is currently closed.
2. Ask if the situation is an emergency.
3. If emergency:
   - Immediately collect name, callback number, and service address.
   - Attempt transfer to on-call technician.
   - If transfer fails, apologize and assure rapid follow-up.
4. If non-emergency:
   - Collect service request details.
   - Inform the caller the team will follow up during business hours.
5. Ask if they need anything else.
6. Close the call politely.
"""

    return prompt.strip()


# -----------------------------
# Generate Agent Spec
# -----------------------------
def generate_agent_spec(memo):

    account_id = memo.get("account_id")
    company = memo.get("company_name", "Unknown Company")

    version = memo.get("metadata", {}).get("version", "v1")

    business_hours = memo.get("business_hours", {})
    services = memo.get("services_supported", [])
    emergencies = memo.get("emergency_definition", [])

    transfer_rules = memo.get("call_transfer_rules", {})
    timeout = transfer_rules.get("timeout_seconds", 60)

    agent_spec = {
        "agent_name": f"{company} - Clara",
        "version": version,

        "voice_style": "professional, calm, concise",

        "variables": {
            "timezone": safe(business_hours.get("timezone")),
            "business_hours": business_hours,
            "services_supported": services if services else ["Not specified"],
            "emergency_triggers": emergencies if emergencies else ["Not specified"]
        },

        "system_prompt": build_system_prompt(memo),

        "call_transfer_protocol": {
            "enabled": True,
            "timeout_seconds": timeout,
            "retry_attempts": 1
        },

        "fallback_protocol": {
            "transfer_failure_message":
                "We are experiencing difficulty transferring your call. "
                "Our dispatch team will contact you shortly."
        },

        "metadata": {
            "account_id": account_id,
            "generated_at": datetime.utcnow().isoformat()
        }
    }

    return agent_spec


# -----------------------------
# Batch Generate Agent Specs
# -----------------------------
def main():

    base_accounts_path = os.path.join("outputs", "accounts")

    if not os.path.exists(base_accounts_path):
        print("❌ No accounts directory found.")
        return

    for account_id in os.listdir(base_accounts_path):

        account_path = os.path.join(base_accounts_path, account_id)
        v1_memo_path = os.path.join(account_path, "v1", "account_memo.json")

        if not os.path.exists(v1_memo_path):
            print(f"⚠ No memo found for {account_id}, skipping.")
            continue

        with open(v1_memo_path, "r", encoding="utf-8") as f:
            memo = json.load(f)

        output_path = os.path.join(account_path, "v1", "agent_spec.json")

        # Idempotency check
        if os.path.exists(output_path):
            print(f"⏩ Agent spec already exists for {account_id}, skipping.")
            continue

        print(f"🔹 Generating agent spec for {account_id}...")

        agent_spec = generate_agent_spec(memo)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(agent_spec, f, indent=2)

        print(f"✅ Agent spec generated for {account_id}")


if __name__ == "__main__":
    main()