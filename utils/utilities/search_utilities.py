from difflib import get_close_matches

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

def search_truck_number(query, group_cache):
    """
    Search for truck numbers in the group cache that closely match the query.
    """
    truck_numbers = [data["Truck Number"] for data in group_cache.values() if "Truck Number" in data]
    matches = get_close_matches(query, truck_numbers, n=5, cutoff=0.5)
    return matches
