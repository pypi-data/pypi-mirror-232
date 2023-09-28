from collections import OrderedDict
import json
from os import listdir
from os.path import isfile, join

from nltk.featstruct import interactive_demo

from sereia.utils import ConfigHandler
from sereia.query_match import QueryMatch
from sereia.candidate_network import CandidateNetwork
from sereia.utils.document_traverser import DocumentTraverser
from sereia.utils.utils import DictToSTupleFormatter, load_datasets_ids_from_json


class EvaluationHandler:

    def __init__(self, dataset_name, config=None):
        self.config = config
        self.dataset_name = dataset_name

    def load_golden_standards(self):
        golden_standards_path = self.config.queryset_config
        # print('Golden standards_path', golden_standards_path)
        with open(golden_standards_path, mode='r') as f:
            data = json.load(f)
        
        # from pprint import pprint as pp
        # pp(data)

        golden_standards = OrderedDict()
        for item in data:
            if 'query_matches' in item:
                item['query_matches'] = [QueryMatch.from_json_serializable(json_serializable_qm)
                                         for json_serializable_qm in item['query_matches']]

            if 'candidate_networks' in item:
                item['candidate_networks'] = [CandidateNetwork.from_json_serializable(json_serializable_cn)
                                         for json_serializable_cn in item['candidate_networks']]

            golden_standards[item['keyword_query']] = item

        self.golden_standards = golden_standards
        # from pprint import pprint as pp
        # pp(self.golden_standards.keys())
        # pp(self.golden_standards)

    def load_results_from_file(self, **kwargs):
        approach = kwargs.get('approach','standard')
        results_filename = kwargs.get(
            'results_filename',
            last_path(f'{self.config.results_directory}{self.config.queryset_name}-{approach}-%03d.json')
        )

        with open(results_filename + '.json', mode='r') as f:
            data = json.load(f)
        return data

    def evaluate_results(self, results, **kwargs):
        '''
        results_filename is declared here for sake of readability. But the
        default value is only set later to get a timestamp more accurate.
        '''
        results_filename = kwargs.get('results_filename', None)
        approach = kwargs.get('approach', 'standard')
        skip_ranking_evaluation = kwargs.get('skip_ranking_evaluation', False)
        skip_document_retrieval_evaluation = kwargs.get('skip_document_retrieval_evaluation', False)
        write_evaluation_only  = kwargs.get('write_evaluation_only', False)

        if not skip_ranking_evaluation:
            self.evaluate_query_matches(results)
            self.evaluate_candidate_networks(results)

        if not skip_document_retrieval_evaluation:
            self.evaluate_retrieved_documents(results)

        self.evaluate_performance(results)
        self.evaluate_num_schema_keyword_matches(results)
        self.evaluate_num_value_keyword_matches(results)
        self.evaluate_num_keyword_matches(results)
        self.evaluate_num_query_matches(results)
        self.evaluate_num_candidate_networks(results)
        self.evaluate_keyword_matches(results)

        if write_evaluation_only:
            del results['results']

        print(f'Results filename: {results_filename}')
        with open(results_filename + '.json', mode='w') as f:
            json.dump(results, f, indent = 2)

        return results

    def evaluate_query_matches(self, results, **kwargs):
        max_k = kwargs.get('max_k',10)

        results.setdefault('evaluation',{})
        results['evaluation']['query_matches']={}

        relevant_positions = []
        for item in results['results']:

            if 'query_matches' in item.data and 'query_matches' in self.golden_standards[item.data['keyword_query']]:
                if len(self.golden_standards[item.data['keyword_query']]['query_matches']) <= 0:
                    continue

                # print(item.data['keyword_query'], item.data['query_matches'])

                relevant_position = self.evaluate_single_query_match(
                    item.data['keyword_query'],
                    item.data['query_matches'],
                )

                relevant_positions.append(relevant_position)

        precision_at_k = {f'p@{k}' : self.get_precision_at_k(k,relevant_positions)
                          for k in range(1,max_k+1)}

        results['evaluation']['query_matches']['mrr'] = self.get_mean_reciprocal_rank(relevant_positions)
        results['evaluation']['query_matches'].update(precision_at_k)
        results['evaluation']['query_matches']['relevant_positions'] = relevant_positions

        print('QM Evaluation {}'.format(results['evaluation']['query_matches']))

    def evaluate_single_query_match(
        self,
        keyword_query,
        query_matches,
    ):
        golden_qm = self.golden_standards[keyword_query]['query_matches'][0]
        if len(query_matches) > 0 and not isinstance(query_matches[0], QueryMatch):
            query_matches = [QueryMatch.from_json_serializable(qm) for qm in query_matches]
        relevant_position = self.get_relevant_position(query_matches, golden_qm)

        # print(golden_qm)
        # from pprint import pprint as pp
        # pp(query_matches)

        return relevant_position

    def evaluate_candidate_networks(self, results, **kwargs):
        max_k = kwargs.get('max_k',10)

        results.setdefault('evaluation',{})
        results['evaluation']['candidate_networks']={}

        relevant_positions = []
        for item in results['results']:
            if 'candidate_networks' in item.data  and 'candidate_networks' in self.golden_standards[item.data['keyword_query']]:
                if len(self.golden_standards[item.data['keyword_query']]['candidate_networks']) <= 0:
                    continue

                relevant_position = self.evaluate_single_cjn(
                    item.data['keyword_query'],
                    item.data['candidate_networks'],
                )

                relevant_positions.append(relevant_position)

        precision_at_k = {f'p@{k}' : self.get_precision_at_k(k,relevant_positions)
                          for k in range(1,max_k+1)}

        results['evaluation']['candidate_networks']['mrr'] = self.get_mean_reciprocal_rank(relevant_positions)
        results['evaluation']['candidate_networks'].update(precision_at_k)
        results['evaluation']['candidate_networks']['relevant_positions'] = relevant_positions

        print('CJN Evaluation {}'.format(results['evaluation']['candidate_networks']))

    def evaluate_single_cjn(
        self,
        keyword_query,
        candidate_networks,
    ):
        golden_cn = self.golden_standards[keyword_query]['candidate_networks'][0]
        if len(candidate_networks) > 0 and not isinstance(candidate_networks[0], CandidateNetwork):
            candidate_networks = [CandidateNetwork.from_json_serializable(cn) for cn in candidate_networks]
        relevant_position = self.get_relevant_position(candidate_networks, golden_cn)

        return relevant_position

    def evaluate_retrieved_documents(self, results, use_expected_cjn=False):

        results['evaluation']['retrieval_score'] = []
        GROUND_TRUTH_FOLDER = './ground_truth/{}/'.format(self.dataset_name)

        traverser = DocumentTraverser()
        formatter = DictToSTupleFormatter()

        mongo_id_as_id = False
        databases_collection_ids = load_datasets_ids_from_json()
        database_collections = databases_collection_ids[self.dataset_name]

        for collection in database_collections:
            if '_id' in database_collections[collection]:
                mongo_id_as_id = True

        for item in results['results']:
            retrieved_documents = item.data['retrieved_documents']
            # print(f'Lenght of retrieved documents in evaluation: {len(retrieved_documents)}')
            formatted_retrieved_documents = []
            retrieved_documents_tuples = set([])
            if len(retrieved_documents):
                for document in retrieved_documents:
                    if not mongo_id_as_id:
                        del document['mongo_id']
                    traverser.traverse(document)
                    traversed = traverser.get_traversed_attributes()
                    formatted_retrieved_documents.append(
                        traversed,
                    )
                    retrieved_documents_tuples.add(
                        formatter.format(traversed)
                    )
                    traverser.cleanup()
                
                # print(f'Formatted retrieved documents: {len(formatted_retrieved_documents)}')
                # print(f'Retrieved document tuples: {len(retrieved_documents_tuples)}')
                
                ground_truth_file = GROUND_TRUTH_FOLDER + 'gt_query_{}.json'.format(item.data['query_number'])
                with open(ground_truth_file) as f:
                    ground_truth = json.load(f)
                
                query_ground_truth = set([])
                for document in ground_truth['expected_documents']:
                    if not mongo_id_as_id:
                        del document['mongo_id']
                    query_ground_truth.add(
                        formatter.format(document)
                    )
                
                # print(f'Length of query ground truth: {len(query_ground_truth)}')

                intersection_len = len(retrieved_documents_tuples.intersection(query_ground_truth))
                union_len = len(retrieved_documents_tuples.union(query_ground_truth))
                retrieved_len = len(retrieved_documents_tuples)

                # print(f'Intersection: {intersection_len} | Retrieved: {retrieved_len}')

                if not retrieved_len:
                    precision = 0
                else:
                    precision = intersection_len / retrieved_len
                
                if len(query_ground_truth):
                    recall = intersection_len / len(query_ground_truth)
                else:
                    recall = 0

                results['evaluation']['retrieval_score'].append(
                    {
                        'keyword_query': item['keyword_query'],
                        'precision': precision,
                        'recall': recall,
                        'num_documents_retrieved': retrieved_len,
                        'num_documents_expected': len(query_ground_truth)
                    }
                )

            del item['retrieved_documents']


    def evaluate_performance(self, results, **kwargs):
        results.setdefault('evaluation',{})
        results['evaluation']['performance']={}

        for item in results['results']:

            if 'elapsed_time' in item.data:
                for phase in item.data['elapsed_time']:
                    results['evaluation']['performance'].setdefault(phase,[]).append(item.data['elapsed_time'][phase])

    def evaluate_num_schema_keyword_matches(self, results, **kwargs):
        results.setdefault('evaluation', {})
        results['evaluation']['num_schema_keyword_matches'] = []

        for item in results['results']:

            if 'num_schema_keyword_matches' in item.data:
                results['evaluation']['num_schema_keyword_matches'].append(
                    item.data['num_schema_keyword_matches'])

    def evaluate_num_value_keyword_matches(self, results, **kwargs):
        results.setdefault('evaluation', {})
        results['evaluation']['num_value_keyword_matches'] = []

        for item in results['results']:

            if 'num_value_keyword_matches' in item.data:
                results['evaluation']['num_value_keyword_matches'].append(
                    item.data['num_value_keyword_matches'])

    def evaluate_num_keyword_matches(self, results, **kwargs):
        results.setdefault('evaluation',{})
        results['evaluation']['num_keyword_matches']=[]

        for item in results['results']:

            if 'num_keyword_matches' in item.data:
                results['evaluation']['num_keyword_matches'].append(item.data['num_keyword_matches'])

    def evaluate_num_query_matches(self, results, **kwargs):
        results.setdefault('evaluation',{})
        results['evaluation']['num_query_matches']=[]

        for item in results['results']:

            if 'num_query_matches' in item.data:
                results['evaluation']['num_query_matches'].append(item.data['num_query_matches'])
    
    def evaluate_keyword_matches(self, results, **kwargs):
        results.setdefault('evaluation',{})
        results['evaluation']['keyword_matches']=[]

        for item in results['results']:

            if 'keyword_matches' in item.data:
                results['evaluation']['keyword_matches'].append(str(item.data['keyword_matches']))

    def evaluate_num_candidate_networks(self, results, **kwargs):
        results.setdefault('evaluation',{})
        results['evaluation']['num_candidate_networks']=[]
        for item in results['results']:
            if 'num_candidate_networks' in item.data:
                results['evaluation']['num_candidate_networks'].append(item.data['num_candidate_networks'])

    def get_relevant_position(self, items, ground_truth):
        for i,item in enumerate(items):
            # print('Comparing item {} to {}'.format(item, ground_truth))
            # print(item)
            # print(ground_truth)
            if item == ground_truth:
                # print('Comparing {} and {}'.format(item, ground_truth))
                # print('Found expected at position {}'.format(i+1))
                # print(item)
                return (i+1)
        # print('Not found for', ground_truth)
        return -1

    def get_mean_reciprocal_rank(self, relevant_positions):
        if len(relevant_positions)==0:
            return 0
        sum = 0
        for relevant_position in relevant_positions:
            if relevant_position != -1:
                reciprocal_rank = 1/relevant_position
            else:
                reciprocal_rank = 0
            sum += reciprocal_rank

        mrr = sum/len(relevant_positions)
        return mrr

    def get_precision_at_k(self, k, relevant_positions):
        if len(relevant_positions)==0:
            return 0
        sum = 0
        for relevant_position in relevant_positions:
            if relevant_position <= k and relevant_position!=-1:
                sum+=1
        presition_at_k = sum/len(relevant_positions)
        return presition_at_k
