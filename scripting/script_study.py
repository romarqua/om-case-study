import json
import sys
import os

def should_apply_plan(plan_data):
    for resource_change in plan_data.get("resource_changes", []):
        action = resource_change.get("change", {}).get("actions", [])

        # Disallow destroy actions
        if "delete" in action:
            print(f"Action 'delete' found for resource {resource_change['address']}. Apply must not proceed.")
            return False

        # Only allow create or update actions
        if set(action) - {"create", "update"}:
            print(f"Unsupported action(s) {action} for resource {resource_change['address']}. Apply must not proceed.")
            return False

        # If it's an update, only allow changes to tags.GitCommitHash
        if "update" in action:
            before = resource_change.get("change", {}).get("before", {})
            after = resource_change.get("change", {}).get("after", {})

            allowed_keys = {"tags"}
            actual_keys = set(after.keys())

            if not actual_keys.issubset(allowed_keys):
                print(f"Update affects non-tag attributes: {actual_keys}. Apply must not proceed.")
                return False

            tags_before = before.get("tags", {}) or {}
            tags_after = after.get("tags", {}) or {}
            tag_keys = set(tags_after.keys())

            if tag_keys != {"GitCommitHash"}:
                print(f"Tags other than GitCommitHash are being modified: {tag_keys}. Apply must not proceed.")
                return False

    return True

def main():
    # Default test plan for environments where sys.argv is not used
    default_plan = "test.tfplan.json"

    if len(sys.argv) == 2:
        plan_path = sys.argv[1]
    elif os.path.exists(default_plan):
        print(f"No file argument provided. Using default: {default_plan}")
        plan_path = default_plan
    else:
        print("Usage: python script.py <tfplan.json>")
        return

    try:
        with open(plan_path, 'r') as f:
            plan_data = json.load(f)

        if should_apply_plan(plan_data):
            print("Plan is valid. Proceed with apply.")
        else:
            print("Plan is invalid. Do not proceed.")

    except Exception as e:
        print(f"Error reading or processing file: {e}")

if __name__ == "__main__":
    main()
