from environs import Env

# Use the environs library to load environment variables
env = Env()
env.read_env()

# Load bot-specific configurations
BOT_TOKEN = env.str("BOT_TOKEN")  # Bot token
ADMINS = env.list("ADMINS")  # List of admin IDs
IP = env.str("ip")  # Hosting IP address

# Database configurations
DB_USER = env.str("DB_USER")
DB_PASS = env.str("DB_PASS")
DB_NAME = env.str("DB_NAME")
DB_HOST = env.str("DB_HOST")

# AWS configurations
AWS_ACCESS_KEY_ID = env.str("AWS_ACCESS_KEY_ID")  # AWS Access Key ID
AWS_SECRET_ACCESS_KEY = env.str("AWS_SECRET_ACCESS_KEY")  # AWS Secret Access Key
AWS_REGION = env.str("AWS_REGION")  # AWS Region
