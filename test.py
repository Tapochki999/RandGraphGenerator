import networkx as nx
import csv
import inspect
import random 
n = 1000
p = 0.1
seed = random.randint(0, 1000000)
minweight = 0
maxweight = 10
userandomweight = False
arrr = nx.gnp_random_graph(n, p, seed)
data = [["node1","node2","weight"]]

if userandomweight == False:
    for u, v in arrr.edges():
        arrr[u][v]["weight"] = 0
else:
    for u, v in arrr.edges():
        rand = round(random.uniform(minweight, maxweight), 2)
        arrr[u][v]["weight"] = rand

List1 = list(arrr.edges())
list2 = []
for u, v, datan in arrr.edges(data=True):
    list2.append([u, v, datan.get("weight")])
    pass
data.extend(list2)

    
with open("Output.csv", 'w', newline='', encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerows(data)


# print(List1)
# print(list2)
# print("data: ", data)
print(seed)
print(arrr)
