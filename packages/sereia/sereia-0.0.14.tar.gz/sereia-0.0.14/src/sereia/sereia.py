import json
from pathlib import Path
from os import listdir
from os.path import isfile, join
from timeit import default_timer as timer
from pprint import pprint as pp

import pymongo

from sereia.candidate_network import CandidateNetworkHandler
from sereia.database import MongoHandler
from sereia.evaluation import EvaluationHandler
from sereia.index import IndexHandler
from sereia.keyword_match import KeywordMatchHandler
from sereia.query_match import QueryMatchHandler
from sereia.utils import (
    ConfigHandler,
    KeywordQuery,
    Similarity,
    Tokenizer,
    modify_retrieved_documents,
)
from sereia.utils.result import SereiaResult


class Sereia():
    
    def __init__(
        self,
        dataset_name,
        database_credentials,
        config_directory='./config/',
        **kwargs,
    ):
        self.config = ConfigHandler(
            config_directory,
        )
        self.config_directory = config_directory

        self.topk_qms = kwargs.get('topk_qms', 100)
        self.max_qm_size = kwargs.get('max_qm_size', 3)
        self.max_cjn_size = kwargs.get('max_cjn_size', 4)
        self.topk_cjns = kwargs.get('topk_cjns', 10)
        self.topk_cjns_per_qm = kwargs.get('topk_cjns_per_qm', 2)
        self.topk_cjns_per_qm_list = kwargs.get('top_cjns_per_qm_list', [1])
        self.approaches = ['standard']
        self.assume_golden_qms = False
        self.input_desired_cn = False
        self.assume_golden_standards_in_topk = kwargs.get('assume_golden_standards_in_topk', False)
        self.golden_standards_within_k = kwargs.get('golden_standards_within_k', 5)
        self.datasets_configurations = {}
        self.querysets_configurations = {}
        self.current_dataset = dataset_name
        self.database_handler = self._set_database_handler(
            self.current_dataset,
            database_credentials,
        )
        self.index_handler = self._set_index_handler(
            self.current_dataset,
        )
        self.tokenizer = Tokenizer(tokenize_method = 'simple')
        self.similarity = Similarity(self.index_handler.schema_index)
        self.keyword_match_handler = KeywordMatchHandler(self.similarity)
        self.query_match_handler = QueryMatchHandler()
        self.evaluation_handler = EvaluationHandler(self.current_dataset, self.config)
        self.candidate_network_handler = CandidateNetworkHandler(self.database_handler)
        self.evaluation_handler.load_golden_standards()
        self.mongo_client = pymongo.MongoClient(
            database_credentials,
        )

    def _set_database_handler(self, dataset, database_credentials):
        return MongoHandler(
            dataset,
            database_credentials,
            self.config,
        )
    
    def _set_index_handler(self, dataset):
        return IndexHandler(
            dataset,
            self.database_handler,
            self.config,
        )

    def list_datasets(self):
        datasets = self.database_handler.get_databases()
        print(sorted(list(datasets)))
    
    def list_querysets(self):
        querysets_folder = self.config.querysets_directory
        querysets_configurations = [
            (f.replace('.json', ''), join(querysets_folder, f))
            for f in listdir(querysets_folder)
            if isfile(join(querysets_folder, f))
        ]

        for configuration in querysets_configurations:
            self.querysets_configurations[configuration[0]] = configuration[1] 

        print(sorted(list(self.querysets_configurations.keys())))

    def use_database(self, dataset_name):
        self.current_dataset = dataset_name
        self.config.change_dataset(dataset_name)
        self.current_queryset = dataset_name
        self.database_handler.set_dataset_name(self.current_dataset)
        self.database_handler
        self.index_handler = self._set_index_handler(dataset_name)
        self.load_indexes()

    def use_queryset(self, queryset_name):
        self.current_queryset = queryset_name
        self.config.change_queryset(queryset_name)
        queryset_filepath = self.config.get_queryset_filepath(
            self.current_queryset,
        )
        with open(queryset_filepath, mode='r') as f:
            self._queryset = json.load(f)

    def create_indexes(self):
        self.index_handler.create_indexes()

    def load_indexes(self):
        self.index_handler.load_indexes()
    
    def print_runtime_configs(self):
        print(f'Maximum QM size: {self.max_qm_size}')
        print(f'Top-K QMs considered: {self.topk_qms}')
        print(f'Maximum CJN size: {self.max_cjn_size}')
        print(f'Top-K CJNs considered: {self.topk_cjns}')
        print(f'Maximum CJNs per QM: {self.topk_cjns_per_qm}')

    def run_queryset(self, **kwargs):
        results_filename = kwargs.get('results_filename', None)
        export_results = kwargs.get('export_results', False)
        approach = kwargs.get('approach', 'standard')
        preprocessed_results = kwargs.get('preprocessed_results', {})

        results = []

        keywords_to_load = {
            keyword
            for item in self._queryset
            for keyword in set(self.tokenizer.keywords(item['keyword_query']))
        }

        self.index_handler.load_indexes(keywords = keywords_to_load)

        for query_number, item in enumerate(self._queryset):
            keyword_query = item['keyword_query']

            if keyword_query in preprocessed_results:
                result = preprocessed_results[keyword_query]
            else:
                result = self.keyword_search(
                    keyword_query,
                    query_number=query_number + 1,
                    topk_qms=self.topk_qms,
                    max_qm_size=self.max_qm_size,
                    topk_cjns=self.topk_cjns,
                    max_cjn_size=self.max_cjn_size,
                    topk_cjns_per_qm=self.topk_cjns_per_qm,
                )
            results.append(result)

        data = {
            "database":self.config.connection['database'],
            "queryset":self.config.queryset_config,
            "results":results,
        }

        if export_results:
            if results_filename is None:
                results_filename = 'output.json'

            with open(results_filename, mode='w') as f:
                print(f'Writing results in {results_filename}')
                json.dump(data,f, indent = 4)

        return data

    def keyword_search(self, keyword_query=None, **kwargs):
        max_qm_size = kwargs.get('max_qm_size', self.max_qm_size)
        topk_qms = kwargs.get('topk_qms', self.topk_qms)
        max_cjn_size = kwargs.get('max_cjn_size', self.max_cjn_size)
        topk_cjns = kwargs.get('topk_cjns', self.topk_cjns)
        topk_cjns_per_qm = kwargs.get('topk_cjns_per_qm', self.topk_cjns_per_qm)
        weight_scheme = kwargs.get('weight_scheme', 0)

        repeat = kwargs.get('repeat', 1)
        assume_golden_qms = kwargs.get('assume_golden_qms', False)
        
        input_desired_cn = kwargs.get('input_desired_cn', False)
        skip_cn_generations = kwargs.get('skip_cn_generations', False)
        show_kms_in_result = kwargs.get('show_kms_in_result', True)
        use_result_class = kwargs.get('use_result_class', True)

        weight_scheme = kwargs.get('weight_scheme', 3)

        if 'weight_scheme' in kwargs:
            del kwargs['weight_scheme']

        generated_query = None
        retrieved_documents = []
        query_number = 1
        if 'query_number' in kwargs:
            query_number = kwargs.get('query_number')
        
        print(f'Running keyword query: {keyword_query}')

        elapsed_time = {
            'km':[],
            'skm':[],
            'vkm':[],
            'qm':[],
            'cn':[],
            'total':[],
        }

        if keyword_query is None:
            print(f'Please input a keyword query or choose one of the queries below:')
            for i,item in enumerate(self._queryset):
                keyword_query = item['keyword_query']
                print(f'{i+1:02d} - {keyword_query}')
            return None

        if isinstance(keyword_query, int):
            keyword_query=self._queryset[keyword_query - 1]['keyword_query']

        keywords = self.tokenizer.extract_keywords(keyword_query)
        keyword_query = KeywordQuery(keywords, keyword_query)

        for _ in range(repeat):

            if not assume_golden_qms:
                skm_generation_start_time = timer()

                sk_matches = self.keyword_match_handler.schema_keyword_match_generator(
                    keyword_query,
                    self.index_handler.schema_index,
                )

                vkm_generation_start_time = timer()
                vk_matches = self.keyword_match_handler.value_keyword_match_generator(
                    keyword_query,
                    self.index_handler.value_index,
                )

                num_value_keyword_matches = len(vk_matches)
                num_schema_keyword_matches = len(sk_matches)

                kw_matches = sk_matches + vk_matches
                qm_start_time = timer()
                query_matches = self.query_match_handler.generate_query_matches(
                    keyword_query.get_keywords(),
                    kw_matches,
                    max_qm_size=len(keyword_query.get_keywords()),
                )
            else:
                skm_generation_start_time = timer()
                vkm_generation_start_time = timer()
                qm_start_time = timer()
                kw_matches = []
                query_matches = self.evaluation_handler.golden_standards[keyword_query]['query_matches']

            
            ranked_query_matches = self.query_match_handler.rank_query_matches(query_matches,
                self.index_handler.value_index,
                self.index_handler.schema_index,
                self.similarity,
                weight_scheme,
            )

            ranked_query_matches = ranked_query_matches[:topk_qms]

            cn_start_time = timer()

            if input_desired_cn:
                desired_cn = self.evaluation_handler.golden_standards[keyword_query]['candidate_networks'][0]
                kwargs['desired_cn'] = desired_cn
            else:
                kwargs['desired_cn'] = None

            query_generation_time = None
            query_execution_time = None

            if not skip_cn_generations:
                ranked_cns = self.candidate_network_handler.generate_cns(
                    self.index_handler.schema_index,
                    self.index_handler.schema_graph,
                    ranked_query_matches,
                    keyword_query.get_keywords(),
                    weight_scheme,
                    topk_cjns=topk_cjns,
                    max_cjn_size=max_cjn_size,
                    topk_cjns_per_qm=topk_cjns_per_qm,
                )

                if len(ranked_cns) > 0:
                    top_cn = ranked_cns[0]
                    if self.assume_golden_standards_in_topk:
                        golden_standard_position = self.evaluation_handler.evaluate_single_cjn(
                            keyword_query.get_value(),
                            ranked_cns[:self.golden_standards_within_k],
                        )

                        if golden_standard_position != -1:
                            print('Assuming golden CJN for {} ({})in position {}'.format(keyword_query.get_value(), keyword_query.get_parsed_value(), golden_standard_position))
                            top_cn = ranked_cns[golden_standard_position - 1]
                            print('top cn from gs: {}'.format(top_cn))

                    query_generation_start_time = timer()
                    base_collection, generated_query = top_cn.get_mongo_query_from_cn(
                        self.current_dataset,
                        self.index_handler.schema_graph,
                    ).build()
                    query_generation_end_time = timer()

                    query_execution_start_time = timer()
                    query_result = self.database_handler.execute(base_collection, generated_query)
                    query_execution_end_time = timer()

                    query_generation_time = query_generation_end_time - query_generation_start_time
                    query_execution_time = query_execution_end_time - query_execution_start_time

                    retrieved_documents.extend(list(query_result))
            else:   
                ranked_cns=[]

            cn_end_time = timer()

            elapsed_time['skm'].append(vkm_generation_start_time - skm_generation_start_time)
            elapsed_time['vkm'].append(qm_start_time - vkm_generation_start_time)
            elapsed_time['km'].append(qm_start_time - skm_generation_start_time)
            elapsed_time['qm'].append(cn_start_time - qm_start_time)
            elapsed_time['cn'].append(cn_end_time - cn_start_time)
            elapsed_time['total'].append(cn_end_time - skm_generation_start_time)

        aggregated_elapsed_time = {phase:min(times) for phase,times in elapsed_time.items()}
        modified_documents = modify_retrieved_documents(list(retrieved_documents))

        result = {
            'query_number': query_number,
            'keyword_query': keyword_query.get_value(),
            'keywords': list(keywords),
            'query_matches':      [query_match.to_json_serializable()
                                  for query_match in ranked_query_matches],
            'candidate_networks': [candidate_network.to_json_serializable()
                                  for candidate_network in ranked_cns],
            'elapsed_time':       aggregated_elapsed_time,
            'num_keyword_matches':len(kw_matches),
            'num_query_matches':  len(query_matches),
            'num_candidate_networks':  len(ranked_cns),
            'generated_query': generated_query,
            'retrieved_documents': modified_documents,
            'query_generation_time': query_generation_time,
            'query_execution_time': query_execution_time,
            'num_value_keyword_matches': num_value_keyword_matches,
            'num_schema_keyword_matches': num_schema_keyword_matches,
        }

        if show_kms_in_result:
            result['value_keyword_matches'] = [vkm.to_json_serializable() for vkm in vk_matches]
            result['schema_keyword_matches']= [skm.to_json_serializable() for skm in sk_matches]

        return SereiaResult(self.current_dataset, self.index_handler, self.database_handler, result)

    def execute_mongo_query(self, initial_collection, mongo_query):
        print('Executing query...')
        result = self.mongo_client[
            self.current_dataset
        ][
            initial_collection
        ].aggregate(mongo_query)

        print('Showing enumerated results')
        for n, document in enumerate(result):
            print(f'Document #{n + 1}')
            pp(document)
