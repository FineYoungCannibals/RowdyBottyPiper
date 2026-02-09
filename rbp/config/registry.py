from typing import Optional
from rbp.config.settings import settings
import sys
import importlib
import importlib.util
import pkgutil
from tqdm import tqdm
import inspect
from pathlib import Path

class ModuleRegistry:
    BASE_PATH = "rbp.modules.scripts"
    USER_BASE_DIR = Path.home() / ".rbp" / "scripts"
    USER_BASE_DIR.mkdir(parents=True,exist_ok=True)
    _modules = {}

    @classmethod
    def initialize(cls):
        cls._load_builtin_modules()
        cls._load_user_modules()
    
    @classmethod
    def _register(cls, module):
        name = getattr(module, "__rbp_name__", module.__name__.split(".")[-1])
        cls._modules[name] = module

    @classmethod
    def _load_builtin_modules(cls):
        pkg = importlib.import_module(cls.BASE_PATH)
        for _, name, _ in pkgutil.iter_modules(pkg.__path__):
            mod = importlib.import_module(f"{cls.BASE_PATH}.{name}")
            if hasattr(mod, settings.run_method):
                cls._register(mod)
    
    @classmethod
    def _load_user_modules(cls):
        if str(cls.USER_BASE_DIR) not in sys.path:
            sys.path.insert(0, str(cls.USER_BASE_DIR))
        
        for _, name, _ in pkgutil.iter_modules([str(cls.USER_BASE_DIR)]):
            mod = importlib.import_module(name)
            if hasattr(mod, settings.run_method):
                cls._register(mod)
    
    @classmethod
    def _module_source(cls, module) -> str:
        module_path = Path(module.__file__).resolve()
        return "user" if cls.USER_BASE_DIR in module_path.parents else "builtin"

    @classmethod
    def list_modules(cls):
        """scan and return all modules"""
        modules = []

        for name, module in cls._modules.items():
            source = cls._module_source(module)
            modules.append(
                {
                    "name":name,
                    "source":source,
                }
            )
        return modules
    
    @staticmethod
    def module_exists(module_name):
        """check if module exists"""
        # Built ins
        spec = importlib.util.find_spec(f"{ModuleRegistry.BASE_PATH}.{module_name}")
        print(f"Base check {spec}")
        if spec:
            return spec
        # USER specified path
        print(" what is hte problem :" + str(ModuleRegistry.USER_BASE_DIR) + ", " + module_name)
        spec = importlib.import_module(f"{module_name}")
        return spec is not None
    
    @classmethod
    def run_module(cls, module_name, config=None, file_handler=None):
        """ load and run a module """
        try:
            module = cls._modules[module_name]
        except KeyError:
            raise ValueError(
                f"Module '{module_name}' does not exist.\n"
                f"Available: {','.join(cls._modules)}"
            )
        if not hasattr(module, settings.run_method):
            raise ValueError(
                f"Module '{module_name}' missing {settings.run_method} method for RBP to execute."
            )
        total_steps = 0
        for _, obj in inspect.getmembers(module, inspect.isfunction):
            if inspect.getmodule(obj) == module:
                source = inspect.getsource(obj)
                total_steps+=source.count("#@rbp_progbar_counter")
        
        # run the module and get updates
        with tqdm(total=total_steps, desc=f"Running {module_name}") as pbar:
            return module.run(
                config or {}, 
                progress_callback=pbar.update,
                file_download_callback=file_handler
            )