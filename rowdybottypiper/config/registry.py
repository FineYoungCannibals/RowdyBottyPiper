from typing import Optional
from rowdybottypiper.config.settings import settings
import rowdybottypiper.modules
import importlib
import importlib.util
import pkgutil

class ModuleRegistry:
    @staticmethod
    def list_modules():
        """scan and return all modules"""
        modules = []
        for importer, modname, ispkg in pkgutil.iter_modules(rowdybottypiper.modules.__path__):
            if not ispkg:
                modules.append(modname)
        return modules
    
    @staticmethod
    def module_exists(module_name):
        """check if module exists"""
        spec = importlib.util.find_spec(f"rowdybottypiper.modules.{module_name}")
        return spec is not None
    
    @staticmethod
    def run_module(module_name, config=None):
        """ load and run a module """
        if not ModuleRegistry.module_exists(module_name):
            available = ModuleRegistry.list_modules()
            raise ValueError(
                f"Module '{module_name} does not exist"
                f"Available modules: {', '.join(available)}"
            )
        module = importlib.import_module(f"rowdybottypiper.modules.{module_name}")
        if not hasattr(module,settings.run_method ):
            raise ValueError(f"Module '{module_name} missing {settings.run_method}() function")
        
