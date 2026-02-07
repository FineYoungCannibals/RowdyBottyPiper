from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os
from typing import Optional
from rowdybottypiper.logging.structured_logger import StructuredLogger

class SlackClient():
    def __init__(
        self,
        logger: Optional[StructuredLogger],
        token: str,
        channel: str
    ):
        self.token = token
        self.channel = channel
        self.client = WebClient(token=self.token)
        self.logger = logger

    def send_message(self, title: str, message: str, file_path: Optional[str] = None):
        self.logger.info(f"Sending message with title '{title}'")
        response = None
        try:
            if file_path and os.path.exists(file_path) and os.access(file_path, os.R_OK):
                self.logger.info('Slackbot recieved send_message with file_path. Uploading file...')
                response = self.client.files_upload_v2(
                    channel=self.channel,
                    title=title,
                    file=file_path,
                    initial_comment=message
                )
            else: 
                self.logger.info('Slackbot recieved send_message with no file path. Sending message...')
                response = self.client.chat_postMessage(
                    channel=self.channel,
                    text=message
                )
            self.logger.info('Slackbot upload attempted.')
            if response is None:
                self.logger.error('An error occurred with SlackClient. Recieved no response from Slack.')
            else:
                self.logger.info('Slack message send attempted! Response:')

        except SlackApiError as se:
            self.logger.error(f"Slack specific error occurred:\n{str(se)}\n\n")
            return False
        except Exception as e:
            self.logger.error(f"An error occurred:\n{str(e)}\n\n")
            return False
        return True