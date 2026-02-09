from pydantic_settings import BaseSettings
from pydantic import BaseModel

class RBPSettings(BaseSettings):
    run_method: str = 'run'

settings = RBPSettings()