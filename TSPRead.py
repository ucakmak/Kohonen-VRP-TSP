import os, linecache, numpy as np, math

directoryname = "TSPData/" #Directory to retrieve the TSP data

filelist = []
for fileinfolder in os.listdir(directoryname):
    if fileinfolder.endswith(".tsp"):
        filelist.append(fileinfolder) #List all of the files with a .tsp extension

randomfile = np.random.randint(len(filelist)-1) #Random integer between 0 and len(filelist)-1

whichfile = filelist[randomfile]
filename = directoryname + whichfile #Filename
#filename = "TSPData/eil101.tsp" #Filename declaration for faster (and non-random) data inspection
#filename = "TSPData/usa13509.tsp"
print filename
filetobeopened = open(filename, 'r')

def textbreaker(name,string1,string2): #Reads the text between two specified strings (help to partition the file)
    thelist = []
    with open(name) as input_data:
        for line in input_data:
            if line.strip() == string1:
                break
        for line in input_data:
            if line.strip() == string2:
                break
            thelist.append(line)
    return thelist

with open(filename) as myfile:
    for line in myfile:
        #if "CAPACITY" in line: #What is the capacity of the vehicle (irrelevant for TSP but useful for VRP)
        #    capacitylist = [float(s) for s in line.split() if s.isdigit()]
        #    capacity = capacitylist[0]
        if "DIMENSION" in line: #How many nodes are there
            dimensionlist = [float(s) for s in line.split() if s.isdigit()]
            dimension = dimensionlist[0]
        #if "No of trucks" in line: #Number of trucks (irrelevant for TSP but useful for VRP)
        #    truckslist = [s.split() for s in line.split(',')]
        #    trucks = float(truckslist[1][-1])
        #if "VEHICLES" in line: #Number of trucks (irrelevant for TSP but useful for VRP)
        #    truckslist = [float(s) for s in line.split() if s.isdigit()]
        #    trucks = truckslist[0]

filename2 = filename[:-4];
filename2 = filename2 + '.opt.tour'
if os.path.exists(filename2):
    opttourstring = textbreaker(filename2,"TOUR_SECTION","-1")
    opttourtuple = [tuple(float(y) for y in x.split()) for x in opttourstring]
    opttour = list(zip(*opttourtuple)[0])
else:
    opttour = "There is not an optimal tour file for this problem."

coordlist = textbreaker(filename,"NODE_COORD_SECTION","EOF") #Extracts the coordinates of the customers
nodesandcoords = [tuple(float(y) for y in x.split()) for x in coordlist]
nodes = zip(*nodesandcoords)[0] #Node numbers
xs = zip(*nodesandcoords)[1] #x-coordinates of nodes
ys = zip(*nodesandcoords)[2] #y-coordinates of nodes
if isinstance(opttour,basestring) == 0:
    opttourxs = []
    opttourys = []
    for i in opttour:
        opttourxs.append(nodesandcoords[int(i)-1][1])
        opttourys.append(nodesandcoords[int(i)-1][2])
    optdistances = [math.sqrt((opttourxs[:-1][oti]-opttourxs[1:][oti])**2+(opttourys[:-1][oti]-opttourys[1:][oti])**2) for oti in range(len(opttour)-1)]
    optcost = sum(optdistances)
