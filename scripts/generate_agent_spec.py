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
    days = safe(business_hours.get("days"))
    start = safe(business_hours.get("start"))
    end = safe(business_hours.get("end"))

    emergencies = memo.get("emergency_definition", [])
    emergency_text = ", ".join(emergencies) if emergencies else "Not specified"

    services = memo.get("services_supported", [])
    services_text = ", ".join(services) if services else "Not specified"

    transfer_rules = memo.get("call_transfer_rules", {})
    timeout = transfer_rules.get("timeout_seconds", 60)

    prompt = f"""
You are Clara, the AI voice assistant for {company}.

You handle inbound service calls and must route requests accurately and efficiently.

Timezone: {timezone}
Business Hours: {days} from {start} to {end}
Supported Services: {services_text}

Emergency Triggers: {emergency_text}

========================
BUSINESS HOURS FLOW
========================
1. Greet the caller professionally.
2. Ask the purpose of the call.
3. Collect caller name and callback number.
4. Determine if the request is an emergency.
5. If emergency:
   - Transfer immediately to dispatch or technician.
6. If non-emergency:
   - Collect service details and route appropriately.
7. If transfer fails after {timeout} seconds:
   - Apologize and inform the caller dispatch will follow up shortly.
8. Confirm next steps.
9. Ask if the caller needs anything else.
10. Close the call politely.

========================
AFTER HOURS FLOW
========================
1. Greet the caller and inform them the office is closed.
2. Ask the purpose of the call.
3. Confirm if the situation is an emergency.
4. If emergency:
   - Immediately collect name, callback number, and service address.
   - Attempt transfer to on-call technician.
   - If transfer fails, apologize and assure rapid follow-up.
5. If non-emergency:
   - Collect service request details.
   - Inform the caller the team will follow up during business hours.
6. Ask if the caller needs anything else.
7. Close the call politely.

========================
GENERAL RULES
========================
• Only collect information necessary for routing or dispatch.
• Do not mention internal systems or tools.
• Be calm, concise, and professional.
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

        "agent_name": f"{company} Clara Agent",

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
            "generated_at": datetime.utcnow().isoformat(),
            "source": "automation_pipeline"
        }
    }

    return agent_spec


# -----------------------------
# Generate for Specific Version
# -----------------------------
def generate_for_version(account_path, version):

    memo_path = os.path.join(account_path, version, "account_memo.json")
    output_path = os.path.join(account_path, version, "agent_spec.json")

    if not os.path.exists(memo_path):
        return

    if os.path.exists(output_path):
        print(f"⏩ {version} agent spec already exists, skipping.")
        return

    with open(memo_path, "r", encoding="utf-8") as f:
        memo = json.load(f)

    agent_spec = generate_agent_spec(memo)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(agent_spec, f, indent=2)

    print(f"✅ {version} agent spec generated.")


# -----------------------------
# Batch Runner
# -----------------------------
def main():

    base_accounts_path = os.path.join("outputs", "accounts")

    if not os.path.exists(base_accounts_path):
        print("❌ No accounts directory found.")
        return

    for account_id in os.listdir(base_accounts_path):

        account_path = os.path.join(base_accounts_path, account_id)

        print(f"\n🔹 Processing account: {account_id}")

        generate_for_version(account_path, "v1")
        generate_for_version(account_path, "v2")


if __name__ == "__main__":
    main()