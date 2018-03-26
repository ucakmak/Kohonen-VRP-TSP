from sklearn.cluster import KMeans
import numpy as np, matplotlib.pylab as plt, VRPRead as FileRead, random

nodes = FileRead.nodes
xs = FileRead.xs
ys = FileRead.ys
demands = FileRead.demands
X = np.array(zip(xs,ys))
numtrucks = int(FileRead.trucks)
kmeans = KMeans(max_iter=500,n_clusters=numtrucks,random_state=0).fit(X) #Create clusters as many as the trucks available
kk = kmeans.fit_predict(X) #Assign every customer to a cluster
print len(kk)
capacity = FileRead.capacity
vehicles = max(kk)
FullList = zip(nodes,xs,ys,demands,kk) #Store the nodes, their x- and y- coordinates, demands, and the clusters assigned
FullList.sort(key=lambda t: t[4]) #Sort the list with respect to the clusters in the increasing order

clusters = range(max(kk)+1) #Store the clusters
dimension = FileRead.dimension
optcost = FileRead.optcost
filename = FileRead.filename

#Find the total demand of every cluster
sumclusterlist = []
for i in clusters:
    sumclusterlist.append(sum([w for x,y,z,w,t in FullList if t==i]))
    
#If the demand of a cluster exceeds the vehicle capacity, reassign some nodes from that cluster to undercapacitated clusters
while any(i>capacity for i in sumclusterlist):
    FullList = [list(i) for i in FullList]
    greaterindices = [x[0] for x in enumerate(sumclusterlist) if x[1]>capacity] #Clusters with higher demands than the vehicle capacity
    okayclusters = [x for x in clusters if x not in greaterindices] #Clusters with less demands than the vehicle capacity
    clustercount = [0] 
    for k in clusters:
        clustercount.append(list(zip(*FullList)[-1]).count(k))
    clustercount = np.cumsum(clustercount)
    for t in greaterindices:
        tlist = [x for x in FullList if x[-1]==t]
        aa = list(zip(*tlist)[3])
        mi = aa.index(max(aa))
        mi += clustercount[t]
        FullList[mi][-1] = random.choice(okayclusters) #Max demand node of the excess demand cluster is reassigned to another random cluster
    FullList = [tuple(i) for i in FullList]
    FullList.sort(key=lambda t: t[4])
    sumclusterlist = []
    for i in clusters:
        sumclusterlist.append(sum([w for x,y,z,w,t in FullList if t==i]))
print sumclusterlist

depotx = FileRead.depotx #x-coordinate of the depot
depoty = FileRead.depoty #y-coordinate of the depot

#Plot the clusters
#plt.scatter(*np.transpose(X),c=kk)
#plt.axis("equal")
#plt.show()
