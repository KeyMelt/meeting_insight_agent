# Mock employee directory for email resolution
EMPLOYEE_DIRECTORY = {
    "Alice": "alice.smith@example.com",
    "Bob": "bob.jones@example.com",
    "Charlie": "charlie.brown@example.com",
    "Manager": "manager@example.com",
    "Marketing Team": "marketing@example.com",
    "Engineering Team": "engineering@example.com",
    "Support": "support@example.com",
}

def get_email_for_name(name: str) -> str:
    """
    Resolves a name to an email address.
    Returns the email if found, otherwise returns the original input.
    """
    # Case-insensitive lookup
    for key, email in EMPLOYEE_DIRECTORY.items():
        if key.lower() in name.lower():
            return email
    return None
