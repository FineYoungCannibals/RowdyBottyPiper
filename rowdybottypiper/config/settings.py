from pydantic_settings import BaseSettings

class RBPSettings:
    run_method: str = 'run'

settings = RBPSettings()