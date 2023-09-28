from pprint import pprint as pp

from graphviz import Digraph
from IPython.display import display

from sereia.candidate_network import CandidateNetwork
from sereia.query_match import QueryMatch
from sereia.keyword_match import KeywordMatch
from sereia.utils.printmd import printmd
from sereia.utils.shift_tab import shift_tab
from sereia.utils.ordinal import ordinal


class SereiaResult(dict):

    def __init__(self, database_name, index_handler, database_handler, data):
        dict.__init__(self, data)
        self.data = data
        self.database_name = database_name
        self.database_handler = database_handler
        self.index_handler = index_handler

    def plss(self, **kwargs):
        show_str = kwargs.get('show_str', kwargs.get('text', True))
        show_graph = kwargs.get('show_graph', kwargs.get('graph', True))
        show_sql = kwargs.get('show_sql', kwargs.get('sql', True))
        show_df = kwargs.get('show_df', kwargs.get(
            'df', kwargs.get('jnts', True)))
        top_k = kwargs.get('top_k', 0)
        head = kwargs.get('head', 5)

        for i, json_cn in enumerate(self.data['candidate_networks']):
            cjn = CandidateNetwork.from_json_serializable(json_cn)
            printmd('---')
            printmd(f'**{ordinal(i+1)} PLS**:')

            # if show_str:
            #     printmd('---')
            #     print(f'Text:\n{shift_tab(cjn)}')
            if show_graph:
                g = Digraph(
                    graph_attr={'nodesep': '0.2', 'ranksep': '0.25'},
                    node_attr={'fontsize': "9.0", },
                    edge_attr={'arrowsize': '0.9', },
                )
                for label, id in cjn.vertices():
                    g.node(id, label=str(label))
                if len(cjn) > 1:
                    for (label_a, id_a), (label_b, id_b) in cjn.generate_pipeline():
                        g.edge(id_a, id_b)
                printmd('---')
                print('Graph:')
                display(g)
            if show_df or show_sql:
                base_collection, mongo_query = cjn.get_mongo_query_from_cn(
                    self.database_name,
                    self.index_handler.schema_graph,
                ).build()
                
                if show_sql:
                    printmd('---')
                    print('Base collection:')
                    print(base_collection, end='\n\n')
                    print('Mongo Query:')
                    pp(mongo_query)

            print()

            if i+1 >= top_k and top_k > 0:
                break

    def qms(self, **kwargs):
        top_k = kwargs.get('top_k', 0)

        for i, json_qm in enumerate(self.data['query_matches']):
            qm = QueryMatch.from_json_serializable(json_qm)

            printmd('---')
            printmd(f'**{ordinal(i+1)} QM**:')
            printmd('---')
            print(qm, end='\n')

            if i+1 >= top_k and top_k > 0:
                break

    def kms(self, **kwargs):
        show_skms = kwargs.get('schema', True)
        show_vkms = kwargs.get('value', True)
        top_k = kwargs.get('top_k', 0)

        self.skms(top_k=top_k)
        self.vkms(top_k=top_k)

    def skms(self, **kwargs):
        top_k = kwargs.get('top_k', 0)
        printmd('---')
        printmd(f'**SKMs**:')
        printmd('---')

        if len(self.data['schema_keyword_matches']) == 0:
            print('There is no SKM for this keyword query.')
            return
        for i, json_km in enumerate(self.data['schema_keyword_matches']):
            km = KeywordMatch.from_json_serializable(json_km)
            #print(f'{i+1} KM:')
            print(km)
            if i+1 >= top_k and top_k > 0:
                break

    def vkms(self, **kwargs):
        top_k = kwargs.get('top_k', 0)
        printmd('---')
        printmd(f'**VKMs**:')
        printmd('---')
        if len(self.data['value_keyword_matches']) == 0:
            print('There is no VKM for this keyword query.')
            return
        for i, json_km in enumerate(self.data['value_keyword_matches']):
            km = KeywordMatch.from_json_serializable(json_km)
            print(km)
            if i+1 >= top_k and top_k > 0:
                break

    def __repr__(self):
        return 'SereiaResult'
