import pyaml
from pathlib import Path
import inspect

BASE_SECRETS_DIR = Path(__file__).parent.parent.resolve() / "secrets"

def read_secret():
    caller_path = Path(inspect.stack()[1].filename)
    caller_name = caller_path.stem

    target_path = (BASE_SECRETS_DIR / f"caller_name.yaml").resolve()

    if not target_path.is_relative_to(BASE_SECRETS_DIR):
        raise PermissionError
    
    if not target_path.exists():
        raise FileNotFoundError(f"No secret file found for '{caller_name}'")
    
    with open(target_path, 'r') as f:
        return pyaml.yaml.safe_load(f)