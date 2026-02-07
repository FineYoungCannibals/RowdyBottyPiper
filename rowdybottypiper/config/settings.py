from pydantic_settings import BaseSettings
from pydantic import Field, ValidationError, model_validator
from typing import Optional

class RBPSettings(BaseSettings):
    rbp_slack_bot_token: Optional[str] = None
    rbp_slack_bot_channel: Optional[str] = None

    rbp_s3_secret_key: Optional[str] = None
    rbp_s3_access_key: Optional[str] = None
    rbp_s3_bucket_name: Optional[str] = None
    rbp_s3_endpoint: Optional[str] = None
    rbp_s3_region: str = 'us-east-1'

    rbp_scp_host: Optional[str] = None
    rbp_scp_user: Optional[str] = None
    rbp_scp_private_key: Optional[str] = None
    rbp_scp_public_key: Optional[str] = None
    rbp_scp_port: int = 22

    @model_validator(mode='after')
    def check_slack_dependent_settings(self):
        if any( var for var in [self.rbp_slack_bot_token, self.rbp_slack_bot_channel]) and not all( var for var in [self.rbp_slack_bot_token, self.rbp_slack_bot_channel]):
            raise ValidationError('RBP_SLACK_BOT_CHANNEL is a required environment variable when RBP_SLACK_BOT_TOKEN is given.')
        return self
    
    @model_validator(mode='after')
    def check_scp_dependent_settings(self):
        if any(var for var in [self.rbp_scp_host, self.rbp_scp_port, self.rbp_scp_private_key, self.rbp_scp_public_key, self.rbp_scp_user]) and not all( var for var in [self.rbp_scp_host, self.rbp_scp_port, self.rbp_scp_private_key, self.rbp_scp_public_key, self.rbp_scp_user]):
            raise ValidationError('RBP_SCP_* (USER, PUBLIC_KEY, PRIVATE_KEY, PORT, HOST), if one is provided, all must be provided')
        return self
    
    @model_validator(mode='after')
    def check_s3_dependent_settings(self):
        if any( var for var in [self.rbp_s3_access_key, self.rbp_s3_bucket_name, self.rbp_s3_endpoint, self.rbp_s3_region, self.rbp_s3_secret_key]) and not all( var for var in [self.rbp_s3_access_key, self.rbp_s3_bucket_name, self.rbp_s3_endpoint, self.rbp_s3_region, self.rbp_s3_secret_key]):
            raise ValidationError('RBP_S3_* (SECRET_KEY, ACCESS_KEY, BUCKET_NAME, REGION, ENDPOINT) are all required if one is passed.')
        return self

settings = RBPSettings() #ignore:[call-arg]