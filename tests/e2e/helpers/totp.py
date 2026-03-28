import base64
import hmac
import hashlib
import time
import struct

def generate_totp_code(secret: str) -> str:
    """
    Generate a TOTP code from base32 secret (Microsoft Authenticator format).
    """
    # Decode base32 secret (remove spaces, pad with =)
    secret = secret.replace(" ", "").upper()
    missing_padding = len(secret) % 8
    if missing_padding:
        secret += '=' * (8 - missing_padding)
    key = base64.b32decode(secret, casefold=True)

    # Get current time step (30s intervals)
    counter = int(time.time()) // 30

    # Generate HMAC-SHA1
    msg = struct.pack(">Q", counter)
    hmac_hash = hmac.new(key, msg, hashlib.sha1).digest()

    # Dynamic truncation
    offset = hmac_hash[-1] & 0x0F
    truncated_hash = hmac_hash[offset:offset+4]
    code_int = struct.unpack(">I", truncated_hash)[0] & 0x7FFFFFFF
    code = str(code_int % 1000000).zfill(6)  # Corrected to 10^6 for 6 digits

    return code

async def fill_totp_code(page, secret: str):
    """Detect TOTP input field and fill with generated code."""
    code = generate_totp_code(secret)

    # Try common selectors for 2FA input
    selectors = [
        "input[name='otp']",
        "input[name='verificationCode']",
        "input[placeholder*='code']",
        "input[id*='twoFactor']"
    ]

    for selector in selectors:
        input_field = await page.query_selector(selector)
        if input_field:
            await input_field.fill(code)
            await input_field.blur()
            return True

    raise ValueError("No TOTP input field found")
