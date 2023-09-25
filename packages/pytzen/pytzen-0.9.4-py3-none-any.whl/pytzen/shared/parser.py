import os
import json
import sys

class VariablesParser:
    """
    Parses and retrieves configuration variables from a JSON file, 
    environment variables, and command-line arguments, with type 
    conversion and error handling.
    """

    def __init__(self, json_path, logs):
        """
        Initializes the VariablesParser with the specified JSON file and 
        logger.
        """
        self.logs = logs
        self._config_dict:dict[str] = self._get_json(json_path)
        self._arg_dict:dict[str] = self._get_args()
        self._env_dict:dict[str] = self._get_env()
        self._str_converters = {
            'int': int,
            'str': str,
            'float': float,
            'bool': lambda v: v.lower() in ['true', '1', 'yes', 'y']
        }
        self._native_converters = {
            'bool': {1: True, 0: False}
        }
        self.config = self._generate_config()

    def _get_json(self, json_path):
        """
        Retrieves the JSON content from the specified path.
        """
        with open(json_path, 'r') as file:
            json_dict:dict[str] = json.load(file)
            return json_dict

    def _get_args(self):
        """
        Parses command-line arguments into a dictionary for 
        configuration.
        """
        arg_dict:dict[str] = {}
        for arg in sys.argv[1:]:
            if arg.startswith('--'):
                key, value = arg[2:].split('=')
                arg_dict[key] = value
        return arg_dict

    def _get_env(self):
        """
        Retrieves relevant environment variables based on the config 
        keys.
        """
        env_dict:dict[str] = {}
        for key in self._config_dict.keys():
            if os.environ.get(key.upper()):
                env_dict[key] = os.environ.get(key.upper())
        return env_dict

    def _generate_config(self):
        """
        Generates the final configuration, considering JSON, arguments, 
        and environment variables.
        """
        output_config:dict[str] = {}
        for var_name, details in self._config_dict.items():
            var_type = details['type']
            default_value = details['value']
            args = self._arg_dict.get(var_name, default_value)
            value = self._env_dict.get(var_name, args)
            try:
                converted_value = self._convert_value(value, var_type)
                output_config[var_name] = converted_value
            except Exception as e:
                error = (f'Error converting value for {var_name}. ' 
                         f'Details: {str(e)}')
                self.logs.error(error)    
        return output_config

    def _convert_value(self, value, var_type):
        """
        Converts the given value to the specified type if possible.
        """
        if isinstance(value, str):
            try:
                return self._str_converters[var_type](value)
            except KeyError:
                self.logs.error(f'Unsupported type: {var_type}.')
        else:
            if (var_type in self._native_converters 
                and value in self._native_converters[var_type]):
                return self._native_converters[var_type][value]
            elif type(value).__name__ == var_type:
                return value
            else:
                error = (f'Value type does not match expected type: {var_type}'
                         ' or cannot be converted.')
                self.logs.error(error)
                raise ValueError(error)
