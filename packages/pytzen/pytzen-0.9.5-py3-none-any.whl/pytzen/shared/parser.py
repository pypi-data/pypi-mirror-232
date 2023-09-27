import os
import json
import sys

class VariablesParser:
    """
    Parses configuration from a JSON file, environment variables, 
    and command-line arguments.
    """
    
    def __init__(self, json_path, logs):
        """
        Initializes the parser with a JSON file and logs.
        """
        self.logs = logs
        self._config_dict = self._get_json(json_path)
        self._arg_dict = self._get_args()
        self._env_dict = self._get_env()
        self.config = self._generate_config()

    def _get_json(self, json_path):
        """
        Reads and returns the configuration from the specified JSON file.
        """
        with open(json_path, 'r') as file:
            return json.load(file)

    def _get_args(self):
        """
        Parses and returns configuration from command-line arguments.
        """
        arg_dict = {}
        for arg in sys.argv[1:]:
            if arg.startswith('--'):
                key, value = arg[2:].split('=')
                arg_dict[key] = value
        return arg_dict

    def _get_env(self):
        """
        Retrieves and returns configuration from environment variables.
        """
        env_dict = {}
        for key in self._config_dict.keys():
            if os.environ.get(key.upper()):
                env_dict[key] = os.environ.get(key.upper())
        return env_dict

    def _generate_config(self):
        """
        Consolidates and returns the final configuration from all sources.
        """
        output_config = {}
        for var_name, default_value in self._config_dict.items():
            env_val = self._env_dict.get(var_name, default_value)
            final_val = self._arg_dict.get(var_name, env_val)
            output_config[var_name] = final_val
        return output_config