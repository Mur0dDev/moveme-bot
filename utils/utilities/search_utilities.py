from difflib import get_close_matches
from sheet.google_sheets_integration import group_cache, update_cache

def search_company_name(query, group_cache):
    """
    Search for company names in the group cache that closely match the query.
    """
    company_names = [data["Company Name"] for data in group_cache.values() if "Company Name" in data]
    matches = get_close_matches(query, company_names, n=5, cutoff=0.5)
    return matches

def search_driver_name(query, group_cache):
    """
    Search for driver names in the group cache that closely match the query.
    """
    driver_names = [data["Driver Name"] for data in group_cache.values() if "Driver Name" in data]
    matches = get_close_matches(query, driver_names, n=5, cutoff=0.5)
    return matches


def search_truck_details(truck_number: str) -> list:
    """
    Searches for truck details in the group_cache based on the given truck number.
    Retrieves similar matches with company name, driver name, and group name.

    Args:
        truck_number (str): The truck number to search for.

    Returns:
        list: A list of dictionaries with truck details (company name, driver name, group name, truck number).
    """
    print(f"Searching for truck details matching: {truck_number}")

    # Gather all truck numbers from the group_cache
    truck_entries = [
        {
            "Truck Number": value["Truck Number"],
            "Company Name": value["Company Name"],
            "Driver Name": value["Driver Name"],
            "Group Name": value["Group Name"]
        }
        for value in group_cache.values()
    ]

    # Get all truck numbers as strings for matching
    truck_numbers = [str(entry["Truck Number"]) for entry in truck_entries]

    # Find close matches for the truck number
    similar_trucks = get_close_matches(truck_number, truck_numbers, n=5, cutoff=0.5)

    # Filter truck details for the matched truck numbers
    results = [
        entry for entry in truck_entries if str(entry["Truck Number"]) in similar_trucks
    ]

    if results:
        print(f"Found matching trucks: {results}")
    else:
        print("No matching trucks found.")

    return results
