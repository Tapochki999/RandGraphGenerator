from logic.Graph import GraphGen
import networkx as nx

def main():
    p1 = GraphGen()
    n = 10
    p = 0.5
    m = 3
    p1.erdos_renya_gnp(n, p)
    
    nx.erdos_renyi_graph(n, p)
    # print("Виберіть тип генерації випадкового графу:\n"
    # "1) Граф Ердоша Реньї\n"
    # "2) Конфігураційна модель\n")
    # name = input("Ваш вибір: ")
    # match name:
    #     case 1:
    #         print("Виберіть модель генерації графу:\n" \
    #         "1) Генерація за певною імовірністю (GNP)\n" \
    #         "2) Генерація за кількістю вузлів\n")
            
    #         pass
        

    

if __name__ == "__main__":
    main()