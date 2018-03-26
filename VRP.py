from collections import deque
import math, numpy as np, random, matplotlib.pylab as plt, matplotlib.path as mpath, VRPKMeansClustering as FileRead, time
CodeStartTime = time.time()
class Node(object):
    def __init__(self, x, y):
        self.prev = None
        self.nxt = None
        self.x = x
        self.y = y

    def set_prev(self, prev): #Assigns a previous node to the node in question
        self.prev = prev

    def set_next(self, nxt): #Assigns a next node to the node in question
        self.nxt = nxt

    def set_x(self, x): #Assigns the x-coordinate to the node in question
        self.x = x

    def set_y(self, y): #Assigns the y-coordinate to the node in question
        self.y = y

    def __hash__(self):
        return hash(str(self.x) + str(self.y))
    
    def __eq__(self, node):
        return self.x == node.x and self.y == node.y

def plot(data, code):
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)

    color = plt.get_cmap('jet')(code)
    ax.scatter(data[:, 0], data[:, 1], color=color)
    ax.plot(data[:, 0], data[:, 1], color=color)
    
    red = plt.get_cmap('jet')(230)
    ax.scatter(cities[:, 0], cities[:, 1], color=red)

    plt.show()

def somtodata(somnodes):
    datalist = []
    for node in somnodes:
        datalist.append(np.array([node.x, node.y]))
    datalist.append(datalist[0])
    return np.array(datalist)

problemtype = "VRP"
dimension = FileRead.dimension
filename = FileRead.filename
totalDistance = 0
plots = []
FL = FileRead.FullList
Routes = []
Depot = FileRead.dimension
optcost = FileRead.optcost
vehicles = FileRead.vehicles
for truckrange in range(FileRead.numtrucks):
    w = [] #List of SOM nodes
    cities = []
    N = 0
    inf = float("inf")
    ns = [(n) for n,x,y,d,c in FL if c == truckrange] #Node numbers
    xs = [(x) for n,x,y,d,c in FL if c == truckrange] #x coordinates of the nodes
    ys = [(y) for n,x,y,d,c in FL if c == truckrange] #y coordinates of the nodes
    xs.append(FileRead.depotx)
    ys.append(FileRead.depoty)
    ns.append(Depot)

    BMU_dict = {} #To store the Best Matching Units
    NumIters = 1000 #Number of Iterations
    BMU_effect = 10 #Neighborhood of BMU (Size of the effect of BMU)
    expc = float(NumIters/4.0) #Exponential constant

    #max and min values to help initialize the Self-Organizing Map
    xmax = max(xs)
    ymax = max(ys)
    xmin = min(xs)
    ymin = min(ys)
    cities = np.array(zip(xs,ys))
    width = xmax-xmin
    height = ymax-ymin

    themax = np.abs(cities).max()
    cities = cities/themax #Normalizing the coordinates with respect to the maximum valued coordinate
    N = len(cities) #Number of cities to visit

    somnodes = [] #Nodes of the SOM
    xcenter = xmin + width/2
    ycenter = ymin + height/2
    radius = min(width,height)/6 #6:Random
    for i in range(2*N): #Number of SOM Nodes: 2*N: Random
        x = xcenter + math.cos(2*math.pi/(2*N)*i)*radius
        y = ycenter + math.cos(2*math.pi/(2*N)*i)*radius
        nodetoadd = Node(x/themax,y/themax) #Creation of the SOM node, with its coordinates normalized
        #nodetoadd = Node(x,y)
        if len(somnodes) > 0:
            prev = somnodes[-1]
            nodetoadd.set_prev(prev) #Connect the last known SOM node to the new one
            prev.set_next(nodetoadd) #Connect the new node to the last known SOM node 
        somnodes.append(nodetoadd) #Add the node to the list of SOM nodes
        
    #Connect the first and the last nodes of the SOM nodes
    first = somnodes[0]
    last = somnodes[-1]
    first.set_prev(last)
    last.set_next(first)

    w = somnodes #SOM nodes

#    plot(somtodata(w),30) #Plot the initial SOM nodes over the whole data
    for i in range(NumIters):
        indices = [x for x in range(len(cities))]
        random.shuffle(indices) #Random selection of the cities
        for index in indices:
            city = cities[index]
            BMU = None
            if i == 0: #If it is the first iteration
                mindist = inf #Minimum distance
                for node in w:
                    distance = math.sqrt((node.x-city[0])**2+(node.y-city[1])**2)
                    if distance < mindist: #SOM node with the minimum distance will be the BMU
                        mindist = distance
                        BMU = node
                BMU_dict[str(city[0])+str(city[1])] = BMU #BMU_dict stores the coordinates of the BMU as key, BMU as the corresponding value
            else:
                prev_BMU = BMU_dict[str(city[0])+str(city[1])] #Will compare the possible new BMUs to the previous one
                mindist = math.sqrt((prev_BMU.x-city[0])**2+(prev_BMU.y-city[1])**2) #Minimum known distance
                current_node = prev_BMU 
                BMU = prev_BMU
                for j in range(1,BMU_effect): #Pulls BMU's neighborhood along with BMU
                    neighbour = current_node.nxt
                    distance = math.sqrt((neighbour.x-city[0])**2+(neighbour.y-city[1])**2)
                    if distance < mindist:
                        mindist = distance
                        BMU = neighbour
                    current_node = neighbour
                for j in range(1,BMU_effect):
                    neighbour = current_node.prev
                    distance = math.sqrt((neighbour.x-city[0])**2+(neighbour.y-city[1])**2)
                    if distance < mindist:
                        mindist = distance
                        BMU = neighbour
                    current_node = neighbour
                BMU_dict[str(city[0])+str(city[1])] = BMU #Closest SOM node to the selected city is the new BMU

            #x- and y- coordinate updates for the BMU and its affected neighbors 
            current_node = BMU 
            BMU.x += math.exp(float(float(-i)/expc))*(1.0/float(distance+1.0))*(city[0]-BMU.x)
            BMU.y += math.exp(float(float(-i)/expc))*(1.0/float(distance+1.0))*(city[1]-BMU.y)
            
            upperbound = int(min(len(w)/10,50)*math.exp(float(float(-i)/expc)))
            for j in range(1,upperbound):
                neighbour = current_node.nxt
                distance = j
                
                if distance<upperbound:
                    neighbour.x += math.exp(float(float(-i)/expc))*(1.0/float(distance+1.0))*(city[0]-neighbour.x)
                    neighbour.y += math.exp(float(float(-i)/expc))*(1.0/float(distance+1.0))*(city[1]-neighbour.y)
                current_node = neighbour
                
            current_node = BMU
            for j in range(1,upperbound):
                neighbour = current_node.prev
                distance = j
                
                if distance<upperbound:
                    neighbour.x += math.exp(float(float(-i)/expc))*(1.0/float(distance+1.0))*(city[0]-neighbour.x)
                    neighbour.y += math.exp(float(float(-i)/expc))*(1.0/float(distance+1.0))*(city[1]-neighbour.y)
                current_node = neighbour

#        if i % 300 == 0: #Plot the SOM nodes vs the cities at every 300th iteration
#            plot(somtodata(w),30)
        if i % 100 == 0: #Print the iteration and the upperbound distance between SOM nodes and the cities
            print i
            print int(min(len(w)/10,50)*math.exp(float(float(-i)/expc)))

#    plot(somtodata(w),30) #Plot the SOM nodes vs the cities
    path = []
    node_to_cities = {}
    for city in cities:
        node = BMU_dict[str(city[0])+str(city[1])]
        if node not in node_to_cities.keys():
            node_to_cities[node] = []
        node_to_cities[node].append(city) #Correspond the city and its BMU
        
    current_node = node_to_cities.keys()[0] #Start from the first BMU
    for i in range(len(w)):
        if current_node in node_to_cities.keys():
            towns = node_to_cities[current_node] #All cities corresponding to this BMU
            if len(path)>0:
                temp_map = {}
                for town in towns:
                    distance = math.sqrt((town[0]-path[-1][0])**2+(town[1]-path[-1][1])**2) #Distance between the city and the BMU
                    temp_map[distance] = town
                sorted_keys = temp_map.keys()
                sorted_keys.sort()
                for key in sorted_keys:
                    path.append(temp_map[key])
            else:
                path.extend(towns)
        current_node = current_node.nxt

    path.append(path[0]) #Append the first node in the path to the last to have a full circle
    path = np.array(path)
    
    route = []
    for i in range(len(path)):
        wherein = np.where((cities==path[i]).all(axis=1))
        wherein = np.split(wherein[0],len(wherein[0]))
        route.extend(wherein)

    route = [int(ns[int(i)]) for i in route] #While path stores the coordinates of the nodes, route stores the node numbers
    droute = deque(route)
    if route[-1] != Depot: del droute[-1]
    index0 = route.index(Depot) 
    droute.rotate(-index0) #Move the depot to the beginning of the route for more accurate representation
    if route[-1] != Depot: droute.append(int(Depot))
    Routes.append(list(droute)) #Store the VRP routes
    
    totaldist = 0 #Total distance calculation
    for i in range(len(path)-1):
        city1 = path[i]
        city2 = path[i+1]
        distance = math.sqrt((city1[0]-city2[0])**2+(city1[1]-city2[1])**2)
        totaldist += distance

    print("Total distance of the route of vehicle %i is: %.10f"%(truckrange+1,totaldist*themax)) #Denormalize the total distance

#    plot(path,30) #Plot the path
    
    totalDistance += totaldist*themax #Total VRP distance/cost

print("Total distance of all of the routes is %.10f"%(totalDistance))
print("Optimal cost is %.10f"%optcost)
OptGap = np.true_divide(np.abs(optcost-totalDistance),totalDistance)*100
print("Optimality gap is %.2f%%."%OptGap)
CodeElapsedTime = time.time()-CodeStartTime
