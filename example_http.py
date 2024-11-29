import requests
import json


# Function to fetch and parse the JSON data from the given URL
def fetch_version_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()  # Parse the JSON data and return it
    except requests.exceptions.RequestException as e:
        print(f"Error fetching version data: {e}")
        return None


# Function to convert a version string (e.g., "1.2.3") to a tuple (1, 2, 3) for easy comparison
def version_to_tuple(version):
    return tuple(map(int, version.split(".")))


# Function to compare versions
def compare_versions(current_version, latest_version):
    current_version_tuple = version_to_tuple(current_version)
    latest_version_tuple = version_to_tuple(latest_version)

    if current_version_tuple < latest_version_tuple:
        return "Update available"
    elif current_version_tuple == latest_version_tuple:
        return "You are on the latest version"
    else:
        return "Your version is ahead of the latest version (unlikely)"


# Function to get the latest version from a list of versions
def get_latest_version(versions):
    # Initialize the latest version variable
    latest_version = versions[0]["version"]

    # Iterate over all versions to find the highest one
    for version_info in versions:
        current_version = version_info["version"]
        if version_to_tuple(current_version) > version_to_tuple(latest_version):
            latest_version = current_version

    return latest_version


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

