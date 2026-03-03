import os
import json
from datetime import datetime


# -----------------------------
# Safe Value Helper
# -----------------------------
def safe(value):
    if value is None or value == []:
        return "Not specified"
    return value


# -----------------------------
# Build System Prompt
# -----------------------------
def build_system_prompt(memo):

    company = safe(memo["metadata"]["company_name"])
    timezone = safe(memo["business_profile"]["timezone"])
    business_days = safe(memo["business_hours"]["days_open"])
    start = safe(memo["business_hours"]["start_time"])
    end = safe(memo["business_hours"]["end_time"])
    emergencies = memo["emergency_handling"]["emergency_definition"]

    emergency_text = ", ".join(emergencies) if emergencies else "Not specified"

    prompt = f"""
You are Clara, the AI voice assistant for {company}.

Timezone: {timezone}
Business Hours: {business_days} from {start} to {end}

========================
BUSINESS HOURS FLOW
========================
1. Greet the caller professionally.
2. Ask how you can help.
3. Collect caller name and callback number.
4. Determine if the situation is an emergency ({emergency_text}).
5. If emergency:
   - Transfer immediately.
6. If non-emergency:
   - Collect details and route appropriately.
7. If transfer fails:
   - Apologize and inform dispatch will follow up.
8. Ask if they need anything else.
9. Close the call politely.

========================
AFTER HOURS FLOW
========================
1. Greet caller and inform office is closed.
2. Ask if this is an emergency.
3. If emergency:
   - Collect name, callback number, and address immediately.
   - Attempt transfer to on-call technician.
   - If transfer fails, apologize and assure quick follow-up.
4. If non-emergency:
   - Collect details.
   - Inform caller team will follow up during business hours.
5. Ask if they need anything else.
6. Close the call.
"""

    return prompt.strip()


# -----------------------------
# Generate Agent Spec
# -----------------------------
def generate_agent_spec(memo):

    account_id = memo["metadata"]["account_id"]
    version = memo["metadata"]["version"]

    # Read transfer timeout from memo if exists
    timeout = 60
    if "call_transfer_protocol" in memo:
        timeout = memo["call_transfer_protocol"].get("timeout_seconds", 60)

    agent_spec = {
        "metadata": {
            "account_id": account_id,
            "agent_name": f"{memo['metadata']['company_name']} - Clara {version}",
            "version": version,
            "source": memo["metadata"].get("source", "unknown"),
            "generated_at": str(datetime.now())
        },
        "configuration": {
            "voice_style": "professional, calm, concise",
            "timezone": safe(memo["business_profile"]["timezone"]),
            "business_hours": memo["business_hours"]
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
        }
    }

    return agent_spec


# -----------------------------
# Batch Generate (v1 only)
# -----------------------------
def main():

    base_accounts_path = os.path.join("outputs", "accounts")

    if not os.path.exists(base_accounts_path):
        print("❌ No accounts found.")
        return

    for account_id in os.listdir(base_accounts_path):

        v1_memo_path = os.path.join(
            base_accounts_path,
            account_id,
            "v1",
            "memo.json"
        )

        if not os.path.exists(v1_memo_path):
            continue

        with open(v1_memo_path, "r", encoding="utf-8") as f:
            memo = json.load(f)

        agent_spec = generate_agent_spec(memo)

        output_path = os.path.join(
            base_accounts_path,
            account_id,
            "v1",
            "agent_spec.json"
        )

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(agent_spec, f, indent=2)

        print(f"✅ Agent spec generated for {account_id} ({memo['metadata']['version']})")


if __name__ == "__main__":
    main()