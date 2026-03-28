import pytest
from tests.e2e.helpers.totp import generate_totp_code
import time

def test_totp_code_length():
    secret = "JBSWY3DPEHPK3PXP"
    code = generate_totp_code(secret)
    assert len(code) == 6
    assert code.isdigit()

def test_totp_code_consistency():
    secret = "JBSWY3DPEHPK3PXP"
    # Same counter should give same code
    code1 = generate_totp_code(secret)
    code2 = generate_totp_code(secret)
    assert code1 == code2
