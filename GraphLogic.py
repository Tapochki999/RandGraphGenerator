import networkx as nx
import matplotlib.pyplot as plt
import random
import time
import csv
import os

class Graph:
    def __init__(self):
        self.G = None
        self.metrics = {}
        self.last_time = 0
        self.is_weighted = False

    def create(self, type_val, n_val, p_val, neighbours_val, is_directed, is_weighted, w_from, w_to):
        start_time = time.time()
        self.is_weighted = is_weighted
        
        try:
            nodes = int(n_val)
            
            if type_val == 'Ердоша-Реньї':
                probability = float(p_val) / 100
                self.G = nx.erdos_renyi_graph(nodes, probability, directed=is_directed)
            
            elif type_val == 'Конфігураційна модель':
                neighbours = int(neighbours_val)                
                sequence = [neighbours] * nodes
                
                if sum(sequence) % 2 != 0:
                    sequence[0] += 1
                
                multi_graph = nx.configuration_model(sequence)
                if is_directed:
                    self.G = nx.DiGraph(multi_graph)
                else:
                    self.G = nx.Graph(multi_graph)
                
                loops = nx.selfloop_edges(self.G)
                self.G.remove_edges_from(loops)

            elif type_val == 'Барабаші-Альберта':
                m = int(neighbours_val)
                self.G = nx.barabasi_albert_graph(nodes, m)
                if is_directed:
                    self.G = nx.DiGraph(self.G)

            elif type_val == 'Тісного світу':
                k = int(neighbours_val)
                p = float(p_val) / 100
                self.G = nx.watts_strogatz_graph(nodes, k, p)
                if is_directed:
                    self.G = nx.DiGraph(self.G)

            if is_weighted:
                try:
                    wf = int(w_from)
                    wt = int(w_to)
                    for u, v in self.G.edges():
                        self.G[u][v]['weight'] = random.randint(wf, wt)
                except:
                    pass

            end_time = time.time()
            self.last_time = round(end_time - start_time, 4)
            return True

        except:
            return False

    def calculate_metrics(self):
        if self.G is None:
            return
        
        acc = nx.average_clustering(self.G)
        
        degrees_dict = dict(self.G.degree())
            
        sum_of_degrees = sum(degrees_dict.values())
        count_of_nodes = len(self.G)
        anc = sum_of_degrees / count_of_nodes if count_of_nodes > 0 else 0
        
        if self.G.is_directed():
            if nx.is_strongly_connected(self.G):
                apl = nx.average_shortest_path_length(self.G)
            else:
                components = list(nx.strongly_connected_components(self.G))
                if not components:
                    apl = 0
                else:
                    largest_component = max(components, key=len)
                    subgraph = self.G.subgraph(largest_component)
                    if len(subgraph) > 1:
                        apl = nx.average_shortest_path_length(subgraph)
                    else:
                        apl = 0
        else:
            if nx.is_connected(self.G):
                apl = nx.average_shortest_path_length(self.G)
            else:
                components = list(nx.connected_components(self.G))
                if not components:
                    apl = 0
                else:
                    largest_component = max(components, key=len)
                    subgraph = self.G.subgraph(largest_component)
                    if len(subgraph) > 1:
                        apl = nx.average_shortest_path_length(subgraph)
                    else:
                        apl = 0

        self.metrics = {}
        self.metrics['ACC'] = round(acc, 4)
        self.metrics['ANC'] = round(anc, 4)
        self.metrics['APL'] = round(apl, 4)

    def get_figure(self):
        if self.G is None:
            return None
            
        fig = plt.figure(figsize=(5, 4))
        pos = nx.spring_layout(self.G)
        
        nx.draw(self.G, pos, with_labels=True, node_color='lightblue', arrows=self.G.is_directed())
        
        if self.is_weighted:
            labels = nx.get_edge_attributes(self.G, 'weight')
            nx.draw_networkx_edge_labels(self.G, pos, edge_labels=labels)
            
        return fig

    def save_graph(self, filename):
        if self.G is not None:
            if not filename.lower().endswith('.txt'):
                filename += '.txt'
            
            data = ['weight'] if self.is_weighted else False
            try:
                nx.write_edgelist(self.G, filename, data=data, encoding='utf-8')
            except Exception as e:
                print(f"Error saving graph: {e}")

    def load_graph(self, filename, is_directed=False, is_weighted=False):
        try:
            create_using = nx.DiGraph() if is_directed else nx.Graph()
            
            if is_weighted:
                self.G = nx.read_edgelist(filename, nodetype=int, create_using=create_using, data=(('weight', int),), encoding='utf-8')
            else:
                self.G = nx.read_edgelist(filename, nodetype=int, create_using=create_using, data=False, encoding='utf-8')
                
            self.is_weighted = is_weighted
            return True
        except:
            return False

    def save_all_metrics(self, filename):
        if self.metrics:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['Metric', 'Value'])
                    for key, value in self.metrics.items():
                        writer.writerow([key, value])
                return True
            except Exception:
                return False
        return False