import os
import json
import re
from datetime import datetime
from copy import deepcopy

from generate_agent_spec import generate_agent_spec


# ---------------------------
# Extract onboarding updates
# ---------------------------
def extract_updates(transcript):

    text = transcript.lower()
    updates = {}

    time_match = re.search(r'(\d+\s?[ap]m)\s*to\s*(\d+\s?[ap]m)', text)
    if time_match:
        updates["business_hours.start_time"] = time_match.group(1).upper()
        updates["business_hours.end_time"] = time_match.group(2).upper()

    if "monday to friday" in text or "monday through friday" in text:
        updates["business_hours.days_open"] = [
            "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"
        ]

    if "gas leak" in text:
        updates["emergency_handling.emergency_definition_add"] = "gas leak"

    timeout_match = re.search(r'(\d+)\s*seconds', text)
    if timeout_match:
        updates["call_transfer_protocol.timeout_seconds"] = int(timeout_match.group(1))

    return updates


# ---------------------------
# Apply patch
# ---------------------------
def apply_patch(previous_memo, updates):

    new_memo = deepcopy(previous_memo)
    changelog = []

    for key, value in updates.items():

        if key == "business_hours.start_time":
            old = new_memo["business_hours"]["start_time"]
            if old != value:
                new_memo["business_hours"]["start_time"] = value
                changelog.append(f"- Updated start_time: {old} → {value}")

        elif key == "business_hours.end_time":
            old = new_memo["business_hours"]["end_time"]
            if old != value:
                new_memo["business_hours"]["end_time"] = value
                changelog.append(f"- Updated end_time: {old} → {value}")

        elif key == "business_hours.days_open":
            old = new_memo["business_hours"]["days_open"]
            if old != value:
                new_memo["business_hours"]["days_open"] = value
                changelog.append(f"- Updated business days: {old} → {value}")

        elif key == "emergency_handling.emergency_definition_add":
            existing = new_memo["emergency_handling"]["emergency_definition"]
            if value not in existing:
                existing.append(value)
                changelog.append(f"- Added emergency trigger: {value}")

        elif key == "call_transfer_protocol.timeout_seconds":
            old = new_memo.get("call_transfer_protocol", {}).get("timeout_seconds")
            if old != value:
                new_memo.setdefault("call_transfer_protocol", {})
                new_memo["call_transfer_protocol"]["timeout_seconds"] = value
                changelog.append(f"- Updated transfer timeout: {old} → {value}")

    return new_memo, changelog


# ---------------------------
# Get latest version folder
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
# MAIN BATCH PROCESSOR
# ---------------------------
def main():

    onboarding_folder = os.path.join("dataset", "onboarding")
    accounts_folder = os.path.join("outputs", "accounts")

    if not os.path.exists(onboarding_folder):
        print("❌ Onboarding folder not found.")
        return

    files = os.listdir(onboarding_folder)

    for filename in files:

        if not filename.endswith(".txt"):
            continue

        name_without_ext = os.path.splitext(filename)[0]

        if name_without_ext.startswith("onboarding_"):
            account_id = name_without_ext.replace("onboarding_", "")
        else:
            account_id = name_without_ext

        print(f"\nProcessing onboarding for: {account_id}")

        account_path = os.path.join(accounts_folder, account_id)

        if not os.path.exists(account_path):
            print(f"⚠ Unknown account: {account_id}")
            continue

        latest_version = get_latest_version(account_path)

        if not latest_version:
            print(f"⚠ No previous version found for {account_id}")
            continue

        latest_memo_path = os.path.join(
            account_path,
            latest_version,
            "memo.json"
        )

        with open(latest_memo_path, "r", encoding="utf-8") as f:
            previous_memo = json.load(f)

        onboarding_path = os.path.join(onboarding_folder, filename)

        with open(onboarding_path, "r", encoding="utf-8") as f:
            onboarding_text = f.read()

        updates = extract_updates(onboarding_text)

        new_memo, changelog = apply_patch(previous_memo, updates)

        if not changelog:
            print("No changes detected.")
            continue

        # Create next version
        new_version_number = int(latest_version[1:]) + 1
        new_version = f"v{new_version_number}"

        new_memo["metadata"]["version"] = new_version
        new_memo["metadata"]["last_updated_at"] = str(datetime.now())

        new_version_path = os.path.join(account_path, new_version)
        os.makedirs(new_version_path, exist_ok=True)

        # Save new memo
        with open(os.path.join(new_version_path, "memo.json"), "w", encoding="utf-8") as f:
            json.dump(new_memo, f, indent=2)

        # Generate agent spec
        agent_spec = generate_agent_spec(new_memo)

        with open(os.path.join(new_version_path, "agent_spec.json"), "w", encoding="utf-8") as f:
            json.dump(agent_spec, f, indent=2)

        # Save changelog
        changelog_path = os.path.join(account_path, f"changes_{new_version}.md")
        with open(changelog_path, "w", encoding="utf-8") as f:
            f.write(f"{new_version} Updates:\n\n")
            for line in changelog:
                f.write(line + "\n")

        print(f"✅ Created {new_version} for {account_id}")


if __name__ == "__main__":
    main()