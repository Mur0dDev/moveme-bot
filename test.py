from utils.utilities.search_utilities import search_company_name, search_driver_name, search_truck_number

# Sample data for group_cache and user_cache
group_cache = {
    "group1": {"Company Name": "Elmir INC"},
    "group2": {"Company Name": "GM Cargo LLC"},
    "group3": {"Company Name": "Elite Logistics"},
    "group4": {"Company Name": "Green Movers"},
}

user_cache = {
    "user1": {"Full Name": "John Doe", "Truck Number": "1234"},
    "user2": {"Full Name": "Jane Smith", "Truck Number": "5678"},
    "user3": {"Full Name": "Alice Johnson", "Truck Number": "4321"},
    "user4": {"Full Name": "Bob Brown", "Truck Number": "8765"},
}

# Test Cases
def test_search_company_name():
    print("Testing Company Name Search:")
    query = "Elm"
    results = search_company_name(query, group_cache)
    print(f"Search Query: {query}")
    print(f"Results: {results}")

def test_search_driver_name():
    print("\nTesting Driver Name Search:")
    query = "John"
    results = search_driver_name(query, user_cache)
    print(f"Search Query: {query}")
    print(f"Results: {results}")

def test_search_truck_number():
    print("\nTesting Truck Number Search:")
    query = "1234"
    results = search_truck_number(query, user_cache)
    print(f"Search Query: {query}")
    print(f"Results: {results}")

# Execute Tests
if __name__ == "__main__":
    test_search_company_name()
    test_search_driver_name()
    test_search_truck_number()
