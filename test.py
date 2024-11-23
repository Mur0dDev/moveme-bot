import pyotp

def generate_totp_code(secret_key: str) -> str:
    """
    Generates a 6-digit TOTP code using the provided secret key.
    The code refreshes every 30 seconds.

    :param secret_key: Base32-encoded secret key
    :return: 6-digit TOTP code
    """
    # Create a TOTP object with the provided key
    totp = pyotp.TOTP(secret_key)
    # Generate the current OTP
    return totp.now()

if __name__ == "__main__":
    # Test the function with a sample key
    test_secret_key = "rqcu52knzcq5ewc7huh5vw7o5ukq4ppw"  # Replace with a valid base32-encoded key
    try:
        otp_code = generate_totp_code(test_secret_key)
        print(f"Generated OTP Code: {otp_code}")
    except Exception as e:
        print(f"Error generating OTP: {e}")
