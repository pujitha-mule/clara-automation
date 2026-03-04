import os

def summarize_outputs():

    base_path = os.path.join("outputs", "accounts")

    if not os.path.exists(base_path):
        print("No outputs found.")
        return

    print("\nPipeline Summary\n")
    print("--------------------------")

    total_accounts = 0
    v1_count = 0
    v2_count = 0

    for account in os.listdir(base_path):

        account_path = os.path.join(base_path, account)

        if not os.path.isdir(account_path):
            continue

        total_accounts += 1

        if os.path.exists(os.path.join(account_path, "v1")):
            v1_count += 1

        if os.path.exists(os.path.join(account_path, "v2")):
            v2_count += 1

        print(f"Account: {account}")

    print("\n--------------------------")
    print(f"Accounts processed: {total_accounts}")
    print(f"v1 agents created: {v1_count}")
    print(f"v2 agents created: {v2_count}")