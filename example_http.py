import requests
import json





# Main function
def check_for_update(current_version, version_url):
    data = fetch_version_data(version_url)

    if data:
        versions = data.get("versions", [])
        if not versions:
            print("No versions found in the data.")
            return

        latest_version = get_latest_version(versions)
        update_status = compare_versions(current_version, latest_version)

        print(f"Current version: {current_version}")
        print(f"Latest version: {latest_version}")
        print(update_status)


# Example usage
if __name__ == "__main__":
    # Replace with the actual URL of the JSON file
    version_url = "https://www.sympathiatech.com/archive/SympathiaConnect_versions.json"

    # Set the current version of your app (you can hard-code or dynamically get it)
    current_version = "1.0.0"

    # Check for updates
    check_for_update(current_version, version_url)

