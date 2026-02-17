import os
import configparser

class Configuration(object):
    def __init__(self):
        #Defaults
        # Storage
        self.storage_backend = "file"

        # Queue
        self.queue_backend = "kafka"
        self.queue_config = "kafka:29092"
        self.queue_input_channel = "requests_topic"
        self.queue_response_channel = "response_topic"

        # Dispatcher
        self.dispatcher_app_host = "127.0.0.1"
        self.dispatcher_app_port = "8080"
        self.dispatcher_app_debug = True
        self.dispatcher_temp_folder = "/tmp"
        self.dispatcher_allowed_extensions = {'png', 'jpg', 'jpeg'}

        # Categorize
        self.categorize_app_host = "127.0.0.1"
        self.categorize_app_port = "8090"
        self.categorize_app_debug = True
        self.categorize_model_path = "../model/vgg19-weather.h5"

        # Reporting
        self.reporting_app_host = "127.0.0.1"
        self.reporting_app_port = "8070"
        self.reporting_app_debug = True
        self.reporting_db_host = "localhost"
        self.reporting_db_port = 5438
        self.reporting_db_database_user_name = "postgres"
        self.reporting_db_database_user_password = "postgres"
        self.reporting_db_database_name = "cat_categorize"
        self.reporting_db_request_table = "requests"
        self.reporting_db_response_table = "responses"

    def load_config(self, config_file_path=None):
        if config_file_path is not None:
            self._update_from_file(config_file_path)
        self._update_from_env()

    def save_to_file(self, config_file_path, file_format="ini"):
        if file_format == "ini":
            config_obj = configparser.ConfigParser()
            for field in self.__dict__:
                section = field.split('_')[0]
                if section not in config_obj:
                    config_obj[section] = dict()
                config_item = field.split(f"{section}_")[1]
                config_obj[section][config_item] = str(self.__dict__[field])
            with open(config_file_path, "w") as config_file:
                config_obj.write(config_file)
        elif file_format == "env":
            with open(config_file_path, "w") as config_file:
                for field in self.__dict__:
                    config_file.write(
                        f"export {field.upper()}=\"{str(self.__dict__[field])}\"\n"
                    )
        else:
            raise Exception("Not a valid config format")

    def _update_from_env(self):
        for field in self.__dict__:
            self.__dict__[field] = os.getenv(str(field).upper(), default=self.__dict__[field])

    def _update_from_file(self, file_path):
        config_obj = configparser.ConfigParser()
        config_obj.read(file_path)

        for field in self.__dict__:
            section = field.split('_')[0]
            option = field.split(f"{section}_")[1]
            self.__dict__[field] = config_obj.get(section, option, fallback=self.__dict__[field])
