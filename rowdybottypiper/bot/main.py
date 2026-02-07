from typing import List, Union, Literal, Optional
from pydantic import BaseModel, Field, field_validator
import nodriver
from rowdybottypiper.utils.realistic import slow_typing


class Click(BaseModel):
    action_type: Literal['click'] = 'click'
    element: str

    async def execute(self, browser):
        tab = await browser.get_tab()
        elem = await tab.select(self.element)
        await elem.click()


class Browse(BaseModel):
    action_type: Literal['browse'] = 'browse'
    url: str

    @field_validator('url')
    @classmethod
    def validate_url(cls, v):
        from urllib.parse import urlparse
        parsed = urlparse(v)
        assert all([parsed.scheme, parsed.netloc])
        return v

    async def execute(self, browser):
        tab = await browser.get_tab()
        await tab.get(self.url)


class Form(BaseModel):
    action_type: Literal['submit'] = 'submit'
    fields: List[tuple]
    element: str

    async def execute(self, browser):
        tab = await browser.get_tab()
        for selector, value in self.fields:
            elem = await tab.select(selector)
            await slow_typing(elem, value)
        submit = await tab.select(self.element)
        await submit.click()


class Upload(BaseModel):
    action_type: Literal['upload'] = 'upload'
    element: str
    file_path: str

    async def execute(self, browser):
        tab = await browser.get_tab()
        elem = await tab.select(self.element)
        await elem.send_file(self.file_path)


# Discriminated union
Action = Union[Click, Browse, Form, Upload]


class Bot:
    def __init__(self, actions: List[Action]):
        self.actions = actions
    
    async def run(self):
        browser = await nodriver.start()
        try:
            for action in self.actions:
                await action.execute(browser)
        finally:
            browser.stop()