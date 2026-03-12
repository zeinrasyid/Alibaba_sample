import re


def is_read_only(query: str) -> bool:
    """Validate query is read-only by stripping comments and checking for dangerous keywords."""
    cleaned = re.sub(r"--.*$", "", query, flags=re.MULTILINE)
    cleaned = re.sub(r"/\*.*?\*/", "", cleaned, flags=re.DOTALL)
    cleaned = cleaned.strip().upper()

    if not cleaned.startswith(("SELECT", "SHOW", "DESCRIBE", "EXPLAIN", "WITH")):
        return False

    dangerous = [
        "INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER",
        "TRUNCATE", "GRANT", "REVOKE", "EXEC", "EXECUTE"
    ]
    for keyword in dangerous:
        if re.search(rf"\b{keyword}\b", cleaned):
            return False
    return True
