import os
from Path import * 
from RouteVar import *
from Stop import *
from Graph import *
from GPT_Gorrilla.model import predict

print("...........Handling data ...........")
pathquery = PathQuery()
stopquery = StopQuery()
routevarquery = RouteVarQuery()
data_dir = os.path.join(os.getcwd(), "data")
path_dir = os.path.join(data_dir, "paths.json")
route_dir = os.path.join(data_dir, "vars.json")
stop_dir = os.path.join(data_dir,  "stops.json")
pathquery.read_data(path_dir)
print("....Reading path data complete.....")
route_dict = routevarquery.readData(route_dir)
print("....Reading route data complete.....")
stop_dict = stopquery.read_data(stop_dir)
print("....Reading stop data complete.....")
edgesquery = EdgesQuery()
needed_data, coordinates_dict = edgesquery.handle_data(stopsquery= stopquery, pathsquery=pathquery, route_dict = route_dict, stop_dict= stop_dict)
set_stop = set(stop.getStop("stopId")["stopId"] for stop in stopquery.stopquery)
busgraph = BusGraph(stops = set_stop, edges = needed_data, coordinates_dict = coordinates_dict)
print("......Handling edges complete.....")



busgraph.bfs_all_pairs()
"""

# Week 10: 
try:
    # For a specific one 
    busgraph.astar(start_stop = 1, goal_stop=10)

    # All pairs 
    busgraph.dijkstras_all_stops()
    busgraph.esopo_pape_all_pairs()
    busgraph.bfs_all_pairs()

    # K importances
    busgraph.esopo_k_important(10)
    busgraph.dijkstras_k_important(10)

except ValueError:
    print("Can not do it")
"""

""" 
# Week 11:
queries = {
    "routevarquery": routevarquery,
    "pathquery": pathquery,
    "stopquery": stopquery,
    "busgraph": busgraph,
    "edgesquery": edgesquery,
}

query = "Find the shortest path from stop 1 to stop 10"
try :
    result = predict(query, queries=queries)
    print(result)
except:
    print("Can not do it")
"""
