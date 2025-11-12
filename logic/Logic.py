import random;

class MyGraph:    
    def __init__(self):
        self._adjacency_list = {}

    def add_node(self, node_id):
        if node_id not in self._adjacency_list:
            self._adjacency_list[node_id] = set()

    def add_edge(self, u, v):
        if u == v:
            return 

        self.add_node(u)
        self.add_node(v)
        
        # Додаємо зв'язок в обидва боки, бо граф неорієнтований
        self._adjacency_list[u].add(v)
        self._adjacency_list[v].add(u)

    def get_nodes(self):
        """Повертає список всіх ID вершин у графі."""
        return list(self._adjacency_list.keys())

    def get_neighbors(self, node_id):
        """Повертає множину (set) сусідів для даної вершини."""
        # .get() безпечно поверне None, якщо вершини немає, 
        # але краще повернути порожню множину
        return self._adjacency_list.get(node_id, set())

    def get_number_of_nodes(self):
        """Повертає загальну кількість вершин."""
        return len(self._adjacency_list)

    def get_number_of_edges(self):
        """Повертає загальну кількість ребер."""
        # Ми повинні бути обережні, щоб не порахувати кожне ребро двічі
        # (оскільки A->B і B->A зберігаються окремо)
        total_sum = 0
        for neighbors in self._adjacency_list.values():
            total_sum += len(neighbors)
        
        # Кожне ребро було додано до суми двічі, отже ділимо на 2
        # Використовуємо цілочисельне ділення //
        return total_sum // 2

    def get_degree(self, node_id):
        """Повертає ступінь (кількість сусідів) для вершини."""
        return len(self.get_neighbors(node_id))

    def are_connected(self, u, v):
        """Перевіряє, чи є ребро між u та v."""
        # Це буде надзвичайно важливо для розрахунку коеф. кластеризації
        if u not in self._adjacency_list:
            return False
        return v in self._adjacency_list[u]
        
    


print("hello")

    











