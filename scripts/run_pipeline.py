import subprocess
import os
import json

print("🚀 Starting Clara automation pipeline...\n")


# -------------------------
# Step 1: Extract Demo Data
# -------------------------
print("🔹 Step 1: Extracting demo call information")
subprocess.run(["python", "scripts/extract_demo.py"], check=True)


# -------------------------
# Step 2: Generate Agent Specs
# -------------------------
print("\n🔹 Step 2: Generating agent specifications")
subprocess.run(["python", "scripts/generate_agent_spec.py"], check=True)


# -------------------------
# Step 3: Process Onboarding Updates
# -------------------------
print("\n🔹 Step 3: Processing onboarding updates")
subprocess.run(["python", "scripts/process_onboarding.py"], check=True)


# -------------------------
# Generate Summary Report
# -------------------------
accounts_folder = os.path.join("outputs", "accounts")

summary = {
    "total_accounts": 0,
    "accounts": []
}

if os.path.exists(accounts_folder):

    accounts = [
        a for a in os.listdir(accounts_folder)
        if os.path.isdir(os.path.join(accounts_folder, a))
    ]

    summary["total_accounts"] = len(accounts)
    summary["accounts"] = accounts


summary_path = os.path.join("outputs", "summary_report.json")

with open(summary_path, "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2)

print("\n📊 Summary report generated:")
print(summary_path)


print("\n✅ Pipeline completed successfully.")