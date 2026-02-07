from typing import List, Union, Literal, Optional, Annotated
from pydantic import BaseModel, Field, field_validator
import nodriver
from nodriver import cdp
from rowdybottypiper.utils.realistic import slow_typing
from pathlib import Path



class Click(BaseModel):
    action_type: Literal['click'] = 'click'
    element: str
    wait_alert: bool = False

    async def execute(self, browser):
        tab = await browser.main_tab
        elem = await tab.select(self.element)
        await elem.click()
        if self.wait_alert:
            await tab.wait(10)
            


class Browse(BaseModel):
    action_type: Literal['browse'] = 'browse'
    url: str
    selector: Optional[str] = "div.content"

    @field_validator('url')
    @classmethod
    def validate_url(cls, v):
        from urllib.parse import urlparse
        parsed = urlparse(v)
        assert all([parsed.scheme, parsed.netloc])
        return v

    async def execute(self, browser):
        tab = await browser.get(self.url)
        print(self.selector)
        await tab.wait_for(selector=self.selector, timeout=1000)

class Form(BaseModel):
    action_type: Literal['submit'] = 'submit'
    fields: List[tuple]
    element: str

    async def execute(self, browser):
        tab = await browser.tabs[0]
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
        tab = await browser.tabs[0]
        elem = await tab.select(self.element)
        await elem.send_file(self.file_path)

class Download(BaseModel):
    action_type: Literal['download'] = 'download'
    url:str
    filename:Optional[Path]= Path.cwd() / 'downloads'

    @field_validator('url')
    @classmethod
    def validate_url(cls, v):
        from urllib.parse import urlparse
        parsed = urlparse(v)
        assert all([parsed.scheme, parsed.netloc])
        return v
    
    async def execute(self, browser):
        tab = await browser.tabs[0]
        await tab.set_download_path(self.filename)
        await tab.download_file(self.url, self.filename)

class Alert(BaseModel):
    action_type: Literal['alert']='alert'
    action: Literal['accept','dismiss'] = 'accept'
    text: Optional[str] = None

    async def execute(self, browser):
        tab = browser.main_tab
        await tab.sleep(1)

        if self.action == 'accept':
            if self.text:
                await tab.send(cdp.page.handle_java_script_dialog(
                    accept=True,
                    prompt_text=self.text
                ))
            else:
                await tab.send(cdp.page.handle_java_script_dialog(accept=True))
        else:
            await tab.send(cdp.page.handle_java_script_dialog(accept=False))

    

# Discriminated union
Action = Annotated[
    Union[Alert, Click, Browse, Form, Upload, Download],
    Field(discriminator='action_type')
]



class Bot:
    def __init__(self, actions: List[Action], browser_exe_path: str = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"):
        self.actions = actions
        self.browser_exe_path  = Path(browser_exe_path)
    
    async def run(self):
        browser = await nodriver.start(browser_executable_path=self.browser_exe_path)
        try:
            for action in self.actions:
                await action.execute(browser)
        finally:
            browser.stop()
        