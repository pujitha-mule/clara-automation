import subprocess
import os
import json

print("🚀 Starting Clara automation pipeline...\n")


# -------------------------
# Helper to run steps safely
# -------------------------
def run_step(name, command):
    print(f"\n🔹 {name}")
    try:
        subprocess.run(command, check=True)
        print("✅ Step completed successfully.")
    except subprocess.CalledProcessError:
        print(f"❌ Error occurred during: {name}")
        exit(1)


# -------------------------
# Step 1: Extract Demo Data
# -------------------------
run_step(
    "Step 1: Extracting demo call information",
    ["python", "scripts/extract_demo.py"]
)


# -------------------------
# Step 2: Process Onboarding Updates
# -------------------------
run_step(
    "Step 2: Processing onboarding updates",
    ["python", "scripts/process_onboarding.py"]
)


# -------------------------
# Generate Summary Report
# -------------------------
print("\n📊 Generating pipeline summary...")

accounts_folder = os.path.join("outputs", "accounts")

summary = {
    "total_accounts": 0,
    "v1_generated": 0,
    "v2_generated": 0,
    "accounts": []
}

if os.path.exists(accounts_folder):

    accounts = [
        a for a in os.listdir(accounts_folder)
        if os.path.isdir(os.path.join(accounts_folder, a))
    ]

    summary["total_accounts"] = len(accounts)

    for account in accounts:

        account_path = os.path.join(accounts_folder, account)

        v1_exists = os.path.exists(os.path.join(account_path, "v1"))
        v2_exists = os.path.exists(os.path.join(account_path, "v2"))

        if v1_exists:
            summary["v1_generated"] += 1

        if v2_exists:
            summary["v2_generated"] += 1

        summary["accounts"].append({
            "account_id": account,
            "v1_created": v1_exists,
            "v2_created": v2_exists
        })


summary_path = os.path.join("outputs", "summary_report.json")

os.makedirs("outputs", exist_ok=True)

with open(summary_path, "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2)


print("📄 Summary report saved to:")
print(summary_path)

print("\n📊 Pipeline Summary")
print("----------------------------")
print(f"Accounts processed: {summary['total_accounts']}")
print(f"v1 agents created: {summary['v1_generated']}")
print(f"v2 agents created: {summary['v2_generated']}")
print("----------------------------")

print("\n✅ Clara automation pipeline completed successfully.")