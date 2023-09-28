from copy import deepcopy
import json
import logging
import re
from glob import glob
from pprint import pprint as pp


LOGGING_MAP = {
    'DEBUG' : logging.DEBUG,
    'INFO': logging.INFO,
    'ERROR': logging.ERROR,
    'WARNING': logging.WARNING,
    'CRITICAL': logging.CRITICAL
}

class ConfigHandler:
    __instance = None

    dataset = None
    queryset = None
    dataset_config = None
    queryset_config = None
    config_folder_directory = None
    connection = {}
    create_index = True
    results_directory = None
    plots_directory = None
    logging_mode = None
    default_settings = None

    def __init__(self, config_directory, reset=False, **kwargs):
        from pprint import pprint as pp

        if reset:
            if 'dataset' in kwargs:
                self.dataset = kwargs.get('dataset')

            self.queryset_config = self.get_queryset_filepath(
                self.dataset,
            )

            self.dataset_config = deepcopy(self.default_settings['dataset_config'])
            self.update_config_paths(
                self.dataset,
                self.dataset_config,
            )

            self.connection['database'] = self.dataset
        else:
            self.config_folder_directory = config_directory
            general_config_file = f'{config_directory}config.json'

            config = self.load_config(general_config_file)
            self.default_settings = deepcopy(config)

            self.dataset = config['dataset']
            if 'dataset' in kwargs:
                self.dataset = kwargs.get('dataset')
            self.queryset = config['queryset']
            self.connection = config['connection']

            self.dataset_config = config['dataset_config']
            self.querysets_directory = config['querysets_directory']
            self.queryset_config = self.get_queryset_filepath(
                self.dataset,
            )
            self.update_config_paths(
                self.dataset,
                self.dataset_config,
            )

            self.create_index = config['create_index']
            self.plots_directory = config['plots_directory']
            self.results_directory = config['results_directory']
            self.logging_mode = self.set_logging_level(
                config['logging_mode'],
            )

    def load_config(self, filepath):
        with open(filepath, 'r') as f:
            config = json.load(f)
        return config
    
    def get_queryset_filepath(self, dataset):
        dataset_filename = dataset + '.json'
        if self.querysets_directory.endswith('/'):
            return ''.join([self.querysets_directory, dataset_filename])

        return '/'.join([self.querysets_directory,dataset_filename])

    def change_dataset(self, dataset):
        self.__init__(self.config_folder_directory, reset=True, dataset=dataset)
    
    def change_queryset(self, queryset):
        self.queryset = queryset
    
    def update_config_paths(self, value, config_paths):
        for configuration, path in config_paths.items():
            if configuration.endswith('filepath') or configuration.endswith('directory'):
                config_paths[configuration] = path.format(value)

    def set_logging_level(self, level):
        self.logging_mode = LOGGING_MAP[level]

    # def get_dataset_configs(self):
    #     subfolder = './datasets_config/'
    #     results = []
    #     for filepath in glob(f'{self.config_folder_directory}{subfolder}*.json'):
    #         with open(filepath,'r') as f:
    #             results.append( (json.load(f)['database'], filepath) )
    #     return results

    # def get_queryset_configs(self,dataset_config_filepath=None):
    #     subfolder = './querysets_config/'
    #     results = []
    #     for filepath in glob(f'{self.config_folder_directory}{subfolder}*.json'):
    #         with open(filepath,'r') as f:
    #             data = json.load(f)
    #             if dataset_config_filepath in (None,data['dataset_config_filepath']):
    #                 results.append( (data['queryset_name'], filepath) )
    #     return results
