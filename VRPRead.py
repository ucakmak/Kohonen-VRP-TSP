import os, linecache, numpy as np

setlist = ["A","B","CMT","F","Golden","Li","M","P","X"]
randomset = np.random.randint(len(setlist)-1)
setname = setlist[randomset]
directoryname = "VRPData/" + setname #Directory to retrieve the VRP data

filelist = []
for fileinfolder in os.listdir(directoryname):
    if fileinfolder.endswith(".vrp"):
        filelist.append(fileinfolder) #List all of the files with a .vrp extension

randomfile = np.random.randint(len(filelist)-1) #Random integer between 0 and len(filelist)-1

whichfile = filelist[randomfile]
filename = directoryname + "/" + whichfile #Filename
#filename = "VRPData/CMT/CMT5.vrp" #Filename declaration for faster (and non-random) data inspection
#filename = "VRPData/A/A-n36-k5.vrp"
#filename = "VRPData/A/A-n54-k7.vrp"
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
        if "CAPACITY" in line: #What is the capacity of the vehicle
            capacitylist = [float(s) for s in line.split() if s.isdigit()]
            capacity = capacitylist[0]
        if "DIMENSION" in line: #How many nodes are there, including the depot
            dimensionlist = [float(s) for s in line.split() if s.isdigit()]
            dimension = dimensionlist[0]
        if "No of trucks" in line: #Number of trucks (some files state the number of trucks like this)
            truckslist = [s.split() for s in line.split(',')]
            trucks = float(truckslist[1][-1])
        if "VEHICLES" in line: #Number of trucks (some files state the number of trucks like this)
            truckslist = [float(s) for s in line.split() if s.isdigit()]
            trucks = truckslist[0]
            
if setname == "Li":
    trucks = float(filename[-6:-4])

filename2 = filename[:-4];
filename3 = filename2 + '.opt'
filename4 = filename2 + '.sol'
if os.path.exists(filename3):
    filename2 = filename3
    with open(filename2) as myfile2:
        for line in myfile2:
            if "cost" in line or "Cost" in line: #Optimal Cost
                optcostlist = [float(s) for s in line.split() if s.isdigit()]
                optcost = optcostlist[0]
elif os.path.exists(filename4):
    filename2 = filename4
    with open(filename2) as myfile2:
        optcoststring = myfile2.readline().strip()
        optcost = float(optcoststring)

#print optcost
coordlist = textbreaker(filename,"NODE_COORD_SECTION","DEMAND_SECTION") #Extracts the coordinates of the customers
nodesandcoords = [tuple(float(y) for y in x.split()) for x in coordlist]
demandlist = textbreaker(filename,"DEMAND_SECTION","DEPOT_SECTION") #Extracts the demands of the customers
nodesanddemands = [tuple(float(y) for y in x.split()) for x in demandlist]
nodes = zip(*nodesandcoords)[0] #Node numbers
xs = zip(*nodesandcoords)[1] #x-coordinate of nodes
ys = zip(*nodesandcoords)[2] #y-coordinate of nodes
demands = zip(*nodesanddemands)[1] #demands of nodes

depotlist = textbreaker(filename,"DEPOT_SECTION","-1") #Extracts the depot info
depots = [tuple(float(y) for y in x.split()) for x in depotlist]
#Two different types of assigning the depot (inside or outside of the customer set)
if len(depots[0]) == 1: #Inside the customer set - remove the depot from the customers
    depotx = nodesandcoords[int(depots[0][0])-1][1] #Get the x-coordinate of the depot
    depoty = nodesandcoords[int(depots[0][0])-1][2] #Get the y-coordinate of the depot
    nodes = list(nodes)
    xs = list(xs)
    ys = list(ys)
    del nodes[int(depots[0][0])-1]
    del xs[int(depots[0][0])-1]
    del ys[int(depots[0][0])-1]
if len(depots[0]) == 2: #Outside of the customer set
    depotx = depots[0][0] #Get the x-coordinate of the depot
    depoty = depots[0][1] #Get the y-coordinate of the depot
