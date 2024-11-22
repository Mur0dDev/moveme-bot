from sheet.google_sheets_integration import fetch_all_data, refresh_cache

# Fetch cached data
data = fetch_all_data()
allowed_users = data["allowed_users"]
pwd_credentials = data["pwd_credentials"]

# Print data for debugging
print("Allowed Users:", allowed_users)
print("PWD Credentials:", pwd_credentials)

# Refresh cache when necessary
refresh_cache()
