from typing import Dict
from dflow.plugins.dispatcher import DispatcherExecutor
import os

def init_executor(
        executor_dict,
    ):
    if executor_dict is None:
        return None
    else:
        return DispatcherExecutor(**executor_dict)

def normalize_resources(config_dict: Dict):
    template_dict = {}
    template_dict["template_config"] = config_dict.get("template_config", {})
    template_dict["executor"] = config_dict.get("executor", None)
    if template_dict["executor"] is None:
        assert ("image" in template_dict["template_config"].keys()) and \
            template_dict["template_config"]["image"] is not None
    else:
        return template_dict
