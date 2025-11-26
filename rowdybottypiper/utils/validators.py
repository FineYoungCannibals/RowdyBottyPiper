from urllib.parse import urlparse

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

def validate_url(url: str) -> str:
    """Validate if the provided string is a valid URL"""
    parsed = urlparse(url)
    if not all([parsed.scheme, parsed.netloc]):
        raise ValidationError(f"Invalid URL: {url}")
    return url