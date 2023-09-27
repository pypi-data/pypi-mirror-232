import json
import os
from abc import ABC
import textwrap
from pytzen.shared import logs, parser
from pytzen.tools.status import StatusChecker


class Prototype(ABC):
    """
    A foundational prototype class that provides a template structure 
    for other classes based on external configurations.
    """
    
    class SharedData:
        """A placeholder for shared data among Prototype instances."""
        ...
        
    config: dict = None
    data: SharedData = None

    def __init__(self, log_level:str='INFO', **kwargs):
        """
        Initializes the Prototype with given configurations, logger, 
        and data attributes.
        """
        self._prototype_path:str = os.environ.get('PROTOTYPE_PATH', '.')
        self._class_pattern:dict[str,str] = self._get_class_pattern()
        self.__doc__:str = self._generate_class_doc()
        self._get_data()
        self._create_inputs(kwargs)
        self._get_logger(log_level)
        self._get_config()
    
    def _get_class_pattern(self):
        """
        Fetches the class pattern from a corresponding JSON 
        configuration.
        """
        class_name:str = self.__class__.__name__
        json_path:str = os.path.join(self._prototype_path, 
                                     f'classes/{class_name}.json')
        with open(json_path) as file:
            class_pattern:dict[str,str|dict[str,str]] = json.load(file)
        return class_pattern

    def _generate_class_doc(self, width=68, indent=' '*4):
        """
        Generates a documentation string based on the class's pattern.
        """
        doc_str:str = self._class_pattern['description'] + '\n'
        
        def add_object(obj, doc_str:str):
            doc_str += f'\n{obj.capitalize()}:\n'
            for k, v in self._class_pattern[obj].items():
                line = f'- {k}: {v}'
                doc_str += textwrap.fill(text=line, width=width, 
                                         subsequent_indent=indent) + '\n'
            return doc_str
        
        for obj in ['inputs', 'attributes', 'methods', 'data']:
            if obj in self._class_pattern:
                doc_str = add_object(obj, doc_str)
        return doc_str

    def _create_inputs(self, kwargs:dict[str]):
        """
        Processes and assigns provided inputs as instance attributes.
        """
        if 'inputs' in self._class_pattern:
            for input_name in self._class_pattern['inputs']:
                if input_name not in kwargs:
                    raise ValueError(f'{input_name} must be provided!')
                setattr(self, input_name, kwargs[input_name])
    
    def _get_logger(self, log_level):
        """Initializes a logger for this instance."""
        logger_name = str(self.__class__)
        self.logs = logs.Logger(name=logger_name, level=log_level)

    def _get_config(self):
        """
        Loads a global configuration and stores it in the class-level 
        variable.
        """
        if not Prototype.config:
            config_path:str = os.path.join(self._prototype_path, 'config.json')
            if os.path.exists(config_path):
                vars = parser.VariablesParser(json_path=config_path, 
                                              logs=self.logs)
                Prototype.config:dict[str,dict[str]] = vars.config
    
    def _get_data(self):
        """Retrieves shared data and stores it in a class-level 
        variable."""
        if not Prototype.data:
            Prototype.data = Prototype.SharedData()
    
    def status(self):
        """Checks and returns the status logs of the current 
        instance."""
        checker = StatusChecker(target=self, logs=self.logs)
        checker.check_status()
