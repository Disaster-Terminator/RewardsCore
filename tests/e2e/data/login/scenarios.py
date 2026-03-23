"""Login test scenarios - complex data as Python modules."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class LoginScenario:
    """Login test scenario definition."""
    name: str
    email: str
    password: str
    totp_secret: Optional[str] = None
    expected_result: str = "success"  # success, failure, 2fa_required, locked
    skip_reason: Optional[str] = None


# Login scenarios for testing
LOGIN_SCENARIOS = [
    LoginScenario(
        name="valid_credentials",
        email="test@example.com",
        password="test_password",
        expected_result="success",
    ),
    LoginScenario(
        name="invalid_password",
        email="test@example.com",
        password="wrong_password",
        expected_result="failure",
    ),
    LoginScenario(
        name="2fa_required",
        email="test@example.com",
        password="test_password",
        totp_secret="JBSWY3DPEHPK3PXP",
        expected_result="2fa_required",
    ),
]


def get_scenario_by_name(name: str) -> Optional[LoginScenario]:
    """Get login scenario by name."""
    for scenario in LOGIN_SCENARIOS:
        if scenario.name == name:
            return scenario
    return None
