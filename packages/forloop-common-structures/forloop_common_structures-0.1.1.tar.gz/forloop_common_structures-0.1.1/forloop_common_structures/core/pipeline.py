import copy
from dataclasses import dataclass, field
from typing import Optional

import networkx as nx
from matplotlib import pyplot as plt

import src.flog as flog
from src.core.node import Node


@dataclass
class Pipeline:
    name: str
    start_node_uid: str = 0
    is_active: bool = False
    active_nodes_uids: list = field(default_factory=list)
    remaining_nodes_uids: list = field(default_factory=list)
    last_job_uid: Optional[str] = None

    project_uid: str = "0"
    uid: Optional[str] = None

    def update(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if key in vars(self).keys():
                setattr(self, key, value)
            else:
                raise AttributeError(f"Attribute '{key}' cannot be updated, as it does not exist")

    def run(self):
        self.is_active = True

    def stop(self):  #todo: pause
        self.is_active = False


class GraphPipeline(nx.DiGraph):
    
    instance_counter = 0
    
    def __init__(self, nodes_dict = None, edges_dict = None, variables_dict = None, pipeline_uid:str="", project_uid:str = "", *args, **kwargs):
        """
        Forloop pipeline.
        
        :param nodes: dictionary of all nodes in the pipeline
        :param edges: dictionary of all edges in the pipeline
        :param variables: dictionary of all variables in the pipeline
        :param project_uid: unique key describing the pipeline
        :param args: Positional arguments for networkx.DiGraph
        :param kwargs: Keyword arguments for networkx.DiGraph
        """
        super(GraphPipeline, self).__init__(*args, **kwargs)
        
        self.nodes_dict = nodes_dict
        self.edges_dict = edges_dict
        self.variables_dict = variables_dict #not used at the moment
        
        self.temp_graph=None
        self.start_node=None
        self.node_node_id_dict={} #key: nodes.Node(), value: id_
        self.active_node=None
        self.remaining_nodes=None
        self.pipeline_uid = pipeline_uid
        self.project_uid = project_uid
        
        self.__class__.instance_counter += 1
        self.uid: int = self.instance_counter
        

    def get_start_node(self):
        # noinspection PyTypeChecker
        for node, degree in self.in_degree:
            if degree == 0 and node.typ == 'Start':
                return node

    def populate_from_dict(self, json_dict):
        if json_dict is None:
            return self
        self.nodes_dict = json_dict['nodes']
        self.edges_dict = json_dict['edges']
        node_detail_forms = json_dict.get('node_detail_forms')
        
        for id_, node in self.nodes_dict.items():
            typ = node['type']
            args = node['params']

            if node_detail_forms is not None:
                node_detail_form=node_detail_forms.get(id_)
            else:
                node_detail_form=None

            new_node = Node(pos=[0,0], typ=typ, params=args, fields=node_detail_form, project_uid=self.project_uid, pipeline_uid=self.pipeline_uid) #TODO: refactor pos argument
            self.add_node(new_node, id=str(id_))
            self.node_node_id_dict[new_node]=id_ #key: nodes.Node(), value: id_
        
        for edge in self.edges_dict.values():
            from_node_id = str(edge['from_node'])
            to_node_id = str(edge['to_node'])
            from_node = self.find_node_by_attr('id', from_node_id)
            to_node = self.find_node_by_attr('id', to_node_id)
            channel = edge.get('channel')
            
            try:
                if from_node is not None and to_node is not None:
                    self.add_edge(from_node, to_node, channel=channel)
            except Exception as e:
                flog.error(f"Error while adding edge: {e}")
        return self

    def display(self):
        pos = nx.planar_layout(self)
        # nx.draw_networkx_nodes(self, pos=pos, node_size=200)
        # nx.draw_networkx_edges(self, pos=pos, edgelist=self.edges(), edge_color='black')
        # nx.draw_networkx_labels(self, pos=pos)
        nx.draw(self, with_labels=True, pos=pos, node_color='white', node_size=1000)
        plt.show()

    def find_node_by_attr(self, attr: str, search_val):
        info = nx.get_node_attributes(self, attr)
        for node, value in info.items():
            if value == search_val:
                return node

    def walk(self):
        pass

    def find_sucessors(self,node,ret_value):
        """Finds the following nodes based on channel that has been returned from the input node"""
        self.temp_graph = self.copy()#copy.deepcopy(self)#.copy()
        successors = self.temp_graph.successors(node)
        for edge in [(node, successor) for successor in successors]:
            edge_data = self.get_edge_data(*edge) or {}
            if ret_value == edge_data.get('channel'):
                if not self.temp_graph.has_edge(*edge): #adding back in dynamic loops
                    self.temp_graph.add_edge(*edge)
            else:
                if self.temp_graph.has_edge(*edge):
                    self.temp_graph.remove_edge(*edge)
          
        return(self.temp_graph)
        

    def run_node(self,node):
        #logger.warning(f'Running {node}')
        #print(node,type(node))
        ret_value = node.execute()
        
        return(ret_value)

    def init_temp_graph_iterator_old(self,start_node=None):
        """DEPRECATED"""
        self.temp_graph = self.copy()
        if start_node is None:
            self.start_node = self.temp_graph.get_start_node()
        else:
            self.start_node = start_node
        self.remaining_nodes=nx.dfs_preorder_nodes(self.temp_graph, source=self.start_node)
        self.remaining_not_active_nodes=nx.dfs_preorder_nodes(self.temp_graph, source=self.start_node)
        next(self.remaining_not_active_nodes) #get ahead of the active_node
        
        
    def init_temp_graph(self,start_node=None):
        self.temp_graph = copy.deepcopy(self)#.copy()
        
        self.init_remaining_nodes(start_node)
            
    def init_remaining_nodes(self,start_node):
        if start_node is None:
            self.start_node = self.temp_graph.get_start_node()
        else:
            self.start_node = start_node
        self.remaining_nodes=list(nx.dfs_preorder_nodes(self.temp_graph, source=self.start_node))
        self.remaining_not_active_nodes=list(nx.dfs_preorder_nodes(self.temp_graph, source=self.start_node))
        if len(self.remaining_not_active_nodes)>0: #empty pipeline debug condition
            self.remaining_not_active_nodes.pop(0)
        
        #nx.dfs_preorder_nodes(self.temp_graph, source=self.start_node)
        #next(self.remaining_not_active_nodes) #get ahead of the active_node
    


    def run(self):
        self.init_temp_graph()
        for node in nx.dfs_preorder_nodes(self.temp_graph, source=self.start_node):
            ret_value=self.run_node(node) 
            if ret_value is not None:
                self.find_sucessors(node,ret_value)
            
