"""
Action Registry for RowdyBottyPiper
Central registry mapping action type strings to Pydantic action classes
"""

from typing import Union, Annotated, Type, Dict
from pydantic import Field

from rowdybottypiper.actions.action import Action
from rowdybottypiper.actions.navigation.navigate import NavigateAction
from rowdybottypiper.actions.clickable.click import ClickAction
from rowdybottypiper.actions.clickable.download import DownloadAction
from rowdybottypiper.actions.forms.submit_form import SubmitFormAction
from rowdybottypiper.actions.forms.login import LoginAction
from rowdybottypiper.actions.browser.alert import AlertAction


# Discriminated union for automatic Pydantic parsing
# The discriminator='type' tells Pydantic to look at the 'type' field
# to determine which action class to instantiate
ActionUnion = Annotated[
    Union[
        NavigateAction,
        ClickAction,
        DownloadAction,
        SubmitFormAction,
        LoginAction,
        AlertAction,
    ],
    Field(discriminator='type')
]


# Registry mapping string type names to action classes
# Useful for YAML/config file loading where you have string identifiers
ACTION_REGISTRY: Dict[str, Type[Action]] = {
    'navigate': NavigateAction,
    'click': ClickAction,
    'download': DownloadAction,
    'submit_form': SubmitFormAction,
    'login': LoginAction,
    'alert': AlertAction,
}


# Reverse mapping: action class to string type
# Useful for serialization
ACTION_TYPE_NAMES: Dict[Type[Action], str] = {
    v: k for k, v in ACTION_REGISTRY.items()
}


def get_action_class(action_type: str) -> Type[Action]:
    """
    Get action class from string type name
    
    Args:
        action_type: String type name (e.g., 'login', 'click')
        
    Returns:
        Action class
        
    Raises:
        ValueError: If action type is not registered
    """
    if action_type not in ACTION_REGISTRY:
        raise ValueError(
            f"Unknown action type: '{action_type}'. "
            f"Available types: {', '.join(ACTION_REGISTRY.keys())}"
        )
    return ACTION_REGISTRY[action_type]


def get_action_type_name(action_class: Type[Action]) -> str:
    """
    Get string type name from action class
    
    Args:
        action_class: Action class (e.g., LoginAction)
        
    Returns:
        String type name (e.g., 'login')
        
    Raises:
        ValueError: If action class is not registered
    """
    if action_class not in ACTION_TYPE_NAMES:
        raise ValueError(f"Action class not registered: {action_class.__name__}")
    return ACTION_TYPE_NAMES[action_class]