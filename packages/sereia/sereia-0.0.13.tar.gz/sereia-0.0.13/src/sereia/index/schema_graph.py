from pathlib import Path
import pickle

from sereia.utils import Graph


class SchemaGraph(Graph):
    def __init__(self, graph_dict=None,edges_info = None):
        super().__init__(graph_dict,edges_info)

    def add_fk_constraint(self,constraint,cardinality,table,foreign_table,attribute_mappings):
        self.add_vertex(table)
        self.add_vertex(foreign_table)

        edge_info = self._edges_info.setdefault( 
            (table,foreign_table),
            {}
        ) 
        edge_info[constraint] = (cardinality,attribute_mappings)
        self.add_edge(table, foreign_table, edge_info)

    def add_root(self, table):
        self.add_vertex(table)

    def __repr__(self):
        if len(self)==0:
            return 'EmptyGraph'
        print_string = ['\t'*level+direction+vertex for direction,level,vertex in self.leveled_dfs_iter()]
        return '\n'.join(print_string)

    def persist_to_file(self, filepath, filename):
        Path(filepath).mkdir(parents=True, exist_ok=True)
        data = (self._graph_dict,self._edges_info)
        with open(filepath + filename, mode='wb') as f:
            pickle.dump(
                data,
                f,
                protocol=3,
            )

    def load_from_file(self,filename):
        with open(filename,mode='rb') as f:
            data = pickle.load(f)
        self._graph_dict,self._edges_info = data