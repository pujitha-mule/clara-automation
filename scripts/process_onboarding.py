import os
import json
import re
from datetime import datetime, timezone
from copy import deepcopy

from generate_agent_spec import generate_agent_spec


# ---------------------------
# Extract onboarding updates
# ---------------------------
def extract_updates(transcript):

    text = transcript.lower()
    updates = {}

    # Business hours detection
    time_match = re.search(r'(\d+\s?[ap]m)\s*(?:to|-)\s*(\d+\s?[ap]m)', text)
    if time_match:
        updates["business_hours.start"] = time_match.group(1).upper()
        updates["business_hours.end"] = time_match.group(2).upper()

    if "monday to friday" in text or "monday through friday" in text:
        updates["business_hours.days"] = [
            "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"
        ]

    if "monday to saturday" in text:
        updates["business_hours.days"] = [
            "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"
        ]

    # Timezone detection
    if re.search(r"\best\b", text):
        updates["business_hours.timezone"] = "Eastern Time"
    elif re.search(r"\bcst\b", text):
        updates["business_hours.timezone"] = "Central Time"
    elif re.search(r"\bmst\b", text):
        updates["business_hours.timezone"] = "Mountain Time"
    elif re.search(r"\bpst\b", text):
        updates["business_hours.timezone"] = "Pacific Time"

    # Emergency triggers
    emergency_keywords = [
        "sprinkler leak",
        "fire alarm",
        "power outage",
        "exposed wiring",
        "water leak",
        "sprinkler head damage",
        "heating failure",
        "cooling failure",
        "electrical hazard",
        "fire alarm malfunction"
    ]

    detected = [k for k in emergency_keywords if k in text]

    if detected:
        updates["emergency_definition_add"] = detected

    # Transfer timeout detection
    timeout_match = re.search(r'(\d+)\s*seconds', text)
    if timeout_match:
        updates["call_transfer_rules.timeout_seconds"] = int(timeout_match.group(1))

    return updates


# ---------------------------
# Apply updates to memo
# ---------------------------
def apply_patch(previous_memo, updates):

    new_memo = deepcopy(previous_memo)
    changelog = []

    # Ensure required fields exist
    new_memo.setdefault("business_hours", {})
    new_memo.setdefault("call_transfer_rules", {})
    new_memo.setdefault("emergency_definition", [])

    for key, value in updates.items():

        if key.startswith("business_hours."):

            field = key.split(".")[1]
            old = new_memo["business_hours"].get(field)

            if old != value:
                new_memo["business_hours"][field] = value

                changelog.append({
                    "field": key,
                    "old": old,
                    "new": value
                })

        elif key == "emergency_definition_add":

            for trigger in value:
                if trigger not in new_memo["emergency_definition"]:
                    new_memo["emergency_definition"].append(trigger)

                    changelog.append({
                        "field": "emergency_definition",
                        "old": None,
                        "new": trigger
                    })

        elif key == "call_transfer_rules.timeout_seconds":

            old = new_memo["call_transfer_rules"].get("timeout_seconds")

            if old != value:
                new_memo["call_transfer_rules"]["timeout_seconds"] = value

                changelog.append({
                    "field": key,
                    "old": old,
                    "new": value
                })

    return new_memo, changelog


# ---------------------------
# Find latest version folder
# ---------------------------
def get_latest_version(account_path):

    versions = [
        v for v in os.listdir(account_path)
        if v.startswith("v") and os.path.isdir(os.path.join(account_path, v))
    ]

    if not versions:
        return None

    versions.sort(key=lambda x: int(x[1:]))
    return versions[-1]


# ---------------------------
# MAIN PROCESSOR
# ---------------------------
def main():

    onboarding_folder = os.path.join("dataset", "onboarding")
    accounts_folder = os.path.join("outputs", "accounts")

    if not os.path.exists(onboarding_folder):
        print("❌ Onboarding dataset folder not found.")
        return

    for filename in os.listdir(onboarding_folder):

        if not filename.endswith(".txt"):
            continue

        account_id = os.path.splitext(filename)[0].replace("onboarding_", "")

        print(f"\n🔹 Processing onboarding for: {account_id}")

        account_path = os.path.join(accounts_folder, account_id)

        if not os.path.exists(account_path):
            print(f"⚠ Unknown account: {account_id}")
            continue

        latest_version = get_latest_version(account_path)

        if not latest_version:
            print(f"⚠ No previous version found for {account_id}")
            continue

        memo_path = os.path.join(account_path, latest_version, "account_memo.json")

        with open(memo_path, "r", encoding="utf-8") as f:
            previous_memo = json.load(f)

        onboarding_path = os.path.join(onboarding_folder, filename)

        with open(onboarding_path, "r", encoding="utf-8") as f:
            onboarding_text = f.read()

        updates = extract_updates(onboarding_text)

        new_memo, changelog = apply_patch(previous_memo, updates)

        if not changelog:
            print("⚠ No changes detected.")
            continue

        # Create new version
        new_version_number = int(latest_version[1:]) + 1
        new_version = f"v{new_version_number}"

        new_memo.setdefault("metadata", {})
        new_memo["metadata"]["version"] = new_version
        new_memo["metadata"]["last_updated_at"] = datetime.now(timezone.utc).isoformat()

        new_version_path = os.path.join(account_path, new_version)
        os.makedirs(new_version_path, exist_ok=True)

        # Save updated memo
        with open(os.path.join(new_version_path, "account_memo.json"), "w", encoding="utf-8") as f:
            json.dump(new_memo, f, indent=2)

        # Generate updated agent spec
        agent_spec = generate_agent_spec(new_memo)

        with open(os.path.join(new_version_path, "agent_spec.json"), "w", encoding="utf-8") as f:
            json.dump(agent_spec, f, indent=2)

        # Save changelog history
        changelog_path = os.path.join(account_path, "changes.json")

        history = []

        if os.path.exists(changelog_path):
            with open(changelog_path, "r", encoding="utf-8") as f:
                history = json.load(f)

        history.append({
            "version": new_version,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "changes": changelog
        })

        with open(changelog_path, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)

        print(f"✅ Created {new_version} for {account_id}")


if __name__ == "__main__":
    main()