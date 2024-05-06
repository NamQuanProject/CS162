import math
import json
import os
from datetime import datetime
import heapq
from collections import deque

class Edge():
    def __init__(self, from_stop, to_stop, coordinates_path, distance, time):
        self.from_stop = from_stop
        self.to_stop = to_stop
        self.coordinates = coordinates_path
        self.distance = distance
        self.time = time

    def getEdge(self, *argv):
        result = {}
        allowed_properties = list(self.__dict__.keys())
        for arg in argv:
            if arg not in allowed_properties:
                raise ValueError(f"Invalid property {arg} in the property of Stop" + '\n' + f"Properties should look for {allowed_properties}")
        for arg in argv:
            result[arg] = getattr(self, arg)
        return result

    def setEdge(self, **kwargs):
        allowed_properties = list(self.__dict__.keys())
        for key, value in kwargs.items():
            if key not in allowed_properties:
                raise ValueError(f"Invalid property: {key}")
            
        for key, value in kwargs.items():
            setattr(self, key, value)
                
            print("Successfully reset the RouteVar properties!")
        return True
        

class EdgesQuery():
    def __init__(self):
        self.edges = {}
    
    def point_distance(self,lat1, lon1, lat2, lon2):
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        r = 6371

        distance_km = r * c
        
        return distance_km
    
    def distance_edges(self, coordinates):
        distance = 0
        for i in range(1, len(coordinates)):
            lat1, lon1 = coordinates[i - 1]
            lat2, lon2 = coordinates[i]
            distance += self.point_distance(lat1, lon1, lat2, lon2)
        return distance

    def handle_data(self, stopsquery, stop_dict, pathsquery, route_dict):
        coordinates_dict = {}
        edges_dict = {stop.getStop("stopId")["stopId"]: [] for stop in stopsquery.stopquery}
        for path in pathsquery.paths:
            path_info = path.getPath("routeId", "routeVarId", "coordinates")
            coordinates = path_info["coordinates"]
            path_distance, path_runningtime = route_dict[path_info["routeId"]][path_info["routeVarId"]]
            path_velocity = path_distance / path_runningtime

            stops = stop_dict[path_info["routeId"]][path_info["routeVarId"]]
            
            for j in range(len(stops) - 1):
                from_stop = stops[j]
                from_stop_id = from_stop.getStop("stopId")["stopId"]
                to_stop = stops[j + 1]
                to_stop_id = to_stop.getStop("stopId")["stopId"]
                
                
                closest_index_1 = min(range(len(coordinates)), key=lambda i: self.point_distance(coordinates[i][1], coordinates[i][0], from_stop.getStop("lat")["lat"], from_stop.getStop("lng")["lng"]))
                closest_index_2 = min(range(len(coordinates)), key=lambda i: self.point_distance(coordinates[i][1], coordinates[i][0], to_stop.getStop("lat")["lat"], to_stop.getStop("lng")["lng"]))
                
               
                coordinates_path = coordinates[closest_index_1: closest_index_2 + 1]
                distance = self.distance_edges(coordinates_path)
                time = distance / path_velocity

                
                newEdge = Edge(from_stop=from_stop_id, to_stop=to_stop_id, coordinates_path = coordinates_path, distance= distance , time = time)

                if from_stop_id not in edges_dict:
                    edges_dict[from_stop_id] = []
                edges_dict[from_stop_id].append(newEdge)

                if from_stop_id not in coordinates_dict:
                    coordinates_dict[from_stop_id] = {}
                coordinates_dict[from_stop_id][to_stop_id] = coordinates_path
                self.edges = edges_dict
        
        return self.edges, coordinates_dict
        
    



class BusGraph():
    def __init__(self, stops, edges, coordinates_dict):
        self.stops = stops
        self.edges = edges
        self.coordinates_dict = coordinates_dict

    # DIJSKSTRAS ALGORITHMS: 
    def dijkstras(self, start_stop):
        times = {stop: math.inf for stop in self.stops}
        times[start_stop] = 0
        previous_node = {}
        pq = [(0, start_stop)]  
        while pq:
            dist, current_stop = heapq.heappop(pq)
            if dist > times[current_stop]:
                continue
            current_stop_edges = self.edges[current_stop]
            for edge in current_stop_edges:
                to_stop = edge.getEdge("to_stop")["to_stop"]
                distance_to_edge = edge.time
                new_distance = times[current_stop] + distance_to_edge
                if new_distance < times[to_stop]:
                    times[to_stop] = new_distance
                    previous_node[to_stop] = current_stop
                    heapq.heappush(pq, (new_distance, to_stop))
        return times
    
    def dijkstras_find(self, start_stop):
        times = {stop: math.inf for stop in self.stops}
        times[start_stop] = 0
        previous_node = {}
        pq = [(0, start_stop)]  
        while pq:
            dist, current_stop = heapq.heappop(pq)
            if dist > times[current_stop]:
                continue
            current_stop_edges = self.edges[current_stop]
            for edge in current_stop_edges:
                to_stop = edge.getEdge("to_stop")["to_stop"]
                distance_to_edge = edge.time
                new_distance = times[current_stop] + distance_to_edge
                if new_distance < times[to_stop]:
                    times[to_stop] = new_distance
                    previous_node[to_stop] = current_stop
                    heapq.heappush(pq, (new_distance, to_stop))
        result = {}
        for end_stop in self.stops:
            if times[end_stop] != math.inf:
                temp = end_stop
                path = []
                coordinates_path = []
                while temp != start_stop:
                    coordinates_path.append(self.coordinates_dict[previous_node[temp]][temp])
                    path.append(temp)
                    temp = previous_node[temp]
                path.append(end_stop)
                result[end_stop] = {"time": times[end_stop], "path": path[::-1], "coordinates": sum(coordinates_path[::-1],[])}
        return result

    def dijkstras_all_stops(self):
        start_time = datetime.now()
        all_shortest_paths = {}
        set_stop = {stop for stop in self.stops}  
        file_path = os.path.join("DijkstrasOutput", "DijkstrasOutput.json") 
        count = 1
        slowest = 0
        sum = 0
        fastest = math.inf 
        for start_stop_id in set_stop:
            temp_start_time = datetime.now()
            result = self.dijkstras(start_stop_id)  
            temp_end_time = datetime.now()
            temp_duration = temp_end_time- temp_start_time
            temp_duration_minutes = temp_duration.total_seconds() / 60
            sum += temp_duration_minutes
            slowest = max(slowest, temp_duration_minutes )
            fastest = min(fastest, temp_duration_minutes)
            all_shortest_paths[start_stop_id] = result
            print(f"......Progress:{count}/{len(set_stop)}......")
            count = count + 1
        endtime = datetime.now()
        duration = endtime- start_time
        duration_minutes = duration.total_seconds() / 60
        print(duration_minutes)
        print(fastest, slowest, sum/len(self.stops))
        
        with open(file_path, 'w') as f:
            json.dump(all_shortest_paths, f, indent=4)     
    
    def dijkstras_find_path(self, start_stop):
        times = {stop: math.inf for stop in self.stops}
        times[start_stop] = 0
        previous_node = {}
        pq = [(0, start_stop)]  
        while pq:
            dist, current_stop = heapq.heappop(pq)
            if dist > times[current_stop]:
                continue
            current_stop_edges = self.edges[current_stop]
            for edge in current_stop_edges:
                to_stop = edge.getEdge("to_stop")["to_stop"]
                distance_to_edge = edge.time
                new_distance = times[current_stop] + distance_to_edge
                if new_distance < times[to_stop]:
                    times[to_stop] = new_distance
                    previous_node[to_stop] = current_stop
                    heapq.heappush(pq, (new_distance, to_stop))
        result = {}
        for end_stop in self.stops:
            if times[end_stop] != math.inf:
                temp = end_stop
                path = []
                while temp != start_stop:
                    path.append(temp)
                    temp = previous_node[temp]
                path.append(start_stop)
                result[end_stop] = path[::-1]
        return result

    def dijkstras_go(self, start_stop, end_stop):
        times = {stop: math.inf for stop in self.stops}
        times[start_stop] = 0
        previous_node = {}
        pq = [(0, start_stop)]  
        while pq:
            dist, current_stop = heapq.heappop(pq)
            if dist > times[current_stop]:
                continue
            current_stop_edges = self.edges[current_stop]
            for edge in current_stop_edges:
                to_stop = edge.getEdge("to_stop")["to_stop"]
                distance_to_edge = edge.time
                new_distance = times[current_stop] + distance_to_edge
                if new_distance < times[to_stop]:
                    times[to_stop] = new_distance
                    previous_node[to_stop] = current_stop
                    heapq.heappush(pq, (new_distance, to_stop))
        result = {}
        if times[end_stop] != math.inf:
            temp = end_stop
            path = []
            coordinates_path = []
            while temp != start_stop:
                coordinates_path.append(self.coordinates_dict[previous_node[temp]][temp])
                path.append(temp)
                temp = previous_node[temp]
            path.append(start_stop)
            result= {"time": times[end_stop], "path": path[::-1], "coordinates": sum(coordinates_path[::-1],[])}
            self.formingToGeoJson(result["coordinates"])
            return result
        
        else:
            print("Can not go")

    def dijkstras_k_important(self, k):
        start_time = datetime.now()
        file_path = os.path.join("DijkstrasOutput", "Importances.json")
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                sorted_importance = json.load(f)
                sorted_importance = {k: int(v) for k, v in sorted_importance.items()}
            top_k_stops = list(sorted_importance.keys())[:k]
            return top_k_stops
        set_stop = {stop for stop in self.stops}  
        count = 1
        importance = {stop : 0 for stop in self.stops} 
        for start_stop_id in set_stop:
            result = self.dijkstras_find_path(start_stop_id)
            for path in result:
                for stop in result[path]:
                    importance[stop] += 1
            print(f"......Progress:{count}/{len(set_stop)}......")
            count = count + 1
        sorted_importance = {k: v for k, v in sorted(importance.items(), key=lambda item: item[1], reverse=True)}
        top_k_stops = list(sorted_importance.keys())[:k]
        end_time = datetime.now()
        duration = end_time-start_time
        duration_minutes = duration.total_seconds() / 60
        print(duration_minutes)
        with open(file_path, 'w') as f:
            json.dump(sorted_importance, f, indent=4)  
        return top_k_stops
    
    
    
    # FLOYD WARSHALL ALGORITHMS: 
    def floyd_warshall(self):
        distances = {stop1: {stop2: math.inf for stop2 in self.stops} for stop1 in self.stops}
        for start_stop in self.edges:
            for current_edge in self.edges[start_stop]:
                to_stop = current_edge.getEdge("to_stop")["to_stop"]
                distance_to_edge = current_edge.time
                distances[start_stop][to_stop] = distance_to_edge
        
        num_stop = len(self.stops)
        count = 1
        for k in self.stops:
            print(f"Progress {count} // {num_stop}")
            for i in self.stops:
                for j in self.stops:
                    if distances[i][k] + distances[k][j] < distances[i][j]:
                        distances[i][j] = distances[i][k] + distances[k][j]
            count += 1 
        file_path = os.path.join("FloyOutput", "Output.json")
        with open(file_path, 'w') as f:
            json.dump(distances, f)
        return distances
    
    # BFS ALGORITHMS: 
    def bfs(self, start_stop):
        distances = {stop: math.inf for stop in self.stops}
        distances[start_stop] = 0
        visited = set()
        queue = deque([start_stop])

        while queue:
            updated = False  
            for _ in range(len(queue)):  
                current_stop = queue.popleft()
                visited.add(current_stop)
                for edge in self.edges[current_stop]:
                    to_stop = edge.getEdge("to_stop")["to_stop"]
                    distance_to_edge = edge.time
                    new_distance = distances[current_stop] + distance_to_edge
                    if new_distance < distances[to_stop]:
                        distances[to_stop] = new_distance
                        if to_stop not in visited:
                            queue.append(to_stop)
                        updated = True  
            if not updated:
                break  
        return distances
    
    def bfs_all_pairs(self):
        start_time = datetime.now()
        all_shortest_paths = {}
        set_stop = {stop for stop in self.stops}  
        file_path = os.path.join("BFSOutput", "BFSOutput.json") 
        count = 1
        slowest = 0
        sum = 0
        fastest = math.inf 
        for start_stop_id in set_stop:
            temp_start_time = datetime.now()
            result = self.bfs(start_stop_id)
            temp_end_time = datetime.now()
            temp_duration = temp_end_time- temp_start_time
            temp_duration_minutes = temp_duration.total_seconds() / 60
            sum += temp_duration_minutes
            slowest = max(slowest, temp_duration_minutes )
            fastest = min(fastest, temp_duration_minutes)
            all_shortest_paths[start_stop_id] = result
            print(f"......Progress:{count}/{len(set_stop)}......")
            count = count + 1
        endtime = datetime.now()
        duration = endtime- start_time
        duration_minutes = duration.total_seconds() / 60
        print(fastest, slowest, sum/len(self.stops))
        print(duration_minutes)
        with open(file_path, 'w') as f:
            json.dump(all_shortest_paths, f, indent=4)  
    
   
    
    # ASTAR ALGORITHMS
    def point_distance(self,lat1, lon1, lat2, lon2):
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        r = 6371

        distance_km = r * c
        
        return distance_km
    
    def heuristic_estimate(self, stop1, stop2):
        edge1 = self.coordinates_dict[stop1]
        for ind,i in enumerate(edge1):
            coordinate1 = self.coordinates_dict[stop1][i][0]
            break 
        edge2 = self.coordinates_dict[stop2]
        for ind, i in enumerate(edge2):
            coordinate2 = self.coordinates_dict[stop2][i][0]
            break 
        distance  = self.point_distance(coordinate2[0], coordinate1[1], coordinate2[0], coordinate2[1])
        return distance
        
    def astar(self, start_stop, goal_stop=None):
        start_time = datetime.now()
        times = {stop: math.inf for stop in self.stops}
        times[start_stop] = 0
        previous_node = {}
        pq = [(0 + self.heuristic_estimate(start_stop, goal_stop), start_stop)] if goal_stop else [(0, start_stop)]
        while pq:
            _, current_stop = heapq.heappop(pq)
            if goal_stop and current_stop == goal_stop:
                break
            current_stop_edges = self.edges[current_stop]
            for edge in current_stop_edges:
                to_stop = edge.getEdge("to_stop")["to_stop"]
                distance_to_edge = edge.time
                new_distance = times[current_stop] + distance_to_edge
                if new_distance < times[to_stop]:
                    times[to_stop] = new_distance
                    previous_node[to_stop] = current_stop
                    if goal_stop:
                        try: 
                            addition = self.heuristic_estimate(to_stop, goal_stop)
                            heapq.heappush(pq, (new_distance + addition, to_stop))
                        except:
                            addition = 0
                            heapq.heappush(pq, (new_distance + addition, to_stop))
                    else:
                        heapq.heappush(pq, (new_distance, to_stop))
        end_time = datetime.now()
        duration = end_time - start_time 
        duration_minutes = duration.total_seconds()/ 60
        print(duration_minutes)
        return times


    # ESOSPO PAPE ALGORITHMS:
    def esopo_pape(self, start_stop):
        shortest_distances = {stop: math.inf for stop in self.stops}
        shortest_distances[start_stop] = 0
        mark = {stop: 2 for stop in self.stops}
        
        queue = deque()
        queue.append(start_stop)
        while queue:
            current_stop = queue.popleft()
            mark[current_stop] = 2 
            current_stop_edges = self.edges[current_stop]
            for edge in current_stop_edges:
                neighbor_stop = edge.to_stop
                if shortest_distances[neighbor_stop] > shortest_distances[current_stop] + edge.time:
                    shortest_distances[neighbor_stop] = shortest_distances[current_stop] + edge.time
                    if mark[neighbor_stop] != 1:
                        if queue and shortest_distances[neighbor_stop] < shortest_distances[queue[0]]:
                            queue.appendleft(neighbor_stop)
                        else:
                            queue.append(neighbor_stop)
                        mark[neighbor_stop] = 1 
        return shortest_distances

    def esopo_pape_all_pairs(self):
        start_time = datetime.now()
        all_shortest_paths = {}
        set_stop = {stop for stop in self.stops}  
        file_path = os.path.join("Esopo", "EsopoOutput.json") 
        count = 1
        sum = 0
        fastest = math.inf
        slowest = 0
        for start_stop_id in set_stop:
            temp_start_time = datetime.now()
            result = self.esopo_pape(start_stop_id)   
            temp_end_time = datetime.now()
            temp_duration = temp_end_time- temp_start_time
            temp_duration_minutes = temp_duration.total_seconds() / 60
            sum += temp_duration_minutes
            slowest = max(slowest, temp_duration_minutes )
            fastest = min(fastest, temp_duration_minutes)
            temp_start_time = datetime.now()
            all_shortest_paths[start_stop_id] = result
            print(f"......Progress:{count}/{len(set_stop)}......")
            count = count + 1
        
        endtime = datetime.now()
        duration = endtime- start_time
        duration_minutes = duration.total_seconds() / 60
        print(duration_minutes)
        print(fastest, slowest, sum/len(self.stops))
        with open(file_path, 'w') as f:
            json.dump(all_shortest_paths, f, indent=4) 

    def esopo_pape_importante(self, start_stop):
        previous = {stop: None for stop in self.stops}
        shortest_distances = {stop: math.inf for stop in self.stops}
        shortest_distances[start_stop] = 0
        mark = {stop: 2 for stop in self.stops}
        queue = deque()
        queue.append(start_stop)
        while queue:
            current_stop = queue.popleft()
            mark[current_stop] = 2 
            current_stop_edges = self.edges[current_stop]
            for edge in current_stop_edges:
                neighbor_stop = edge.to_stop
                if shortest_distances[neighbor_stop] > shortest_distances[current_stop] + edge.time:
                    shortest_distances[neighbor_stop] = shortest_distances[current_stop] + edge.time
                    previous[neighbor_stop] = current_stop  
                    if mark[neighbor_stop] != 1: 
                        if queue and shortest_distances[neighbor_stop] < shortest_distances[queue[0]]:
                            queue.appendleft(neighbor_stop)
                        else:
                            queue.append(neighbor_stop)
                        mark[neighbor_stop] = 1 
        result = {}
        for end_stop in self.stops:
            if shortest_distances[end_stop] != math.inf:
                temp = end_stop
                path = []
                while temp != start_stop:
                    path.append(temp)
                    temp = previous[temp]
                path.append(start_stop)
                result[end_stop] = path[::-1]
        return result
    
    def esopo_k_important(self, k):
        start_time = datetime.now()
        file_path = os.path.join("Esopo", "Importances.json")
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                sorted_importance = json.load(f)
                sorted_importance = {k: int(v) for k, v in sorted_importance.items()}
            top_k_stops = list(sorted_importance.keys())[:k]
            return top_k_stops
        set_stop = {stop for stop in self.stops}  
        count = 1
        importance = {stop : 0 for stop in self.stops} 
        for start_stop_id in set_stop:
            result = self.esopo_pape_importante(start_stop_id)
            for path in result:
                for stop in result[path]:
                    importance[stop] += 1
            print(f"......Progress:{count}/{len(set_stop)}......")
            count = count + 1
        sorted_importance = {k: v for k, v in sorted(importance.items(), key=lambda item: item[1], reverse=True)}
        top_k_stops = list(sorted_importance.keys())[:k]
        end_time = datetime.now()
        duration = end_time - start_time
        duration_minutes = duration.total_seconds() / 60 
        print(duration_minutes)
        with open(file_path, 'w') as f:
            json.dump(sorted_importance, f, indent=4)  
        return top_k_stops
    

    # FORMING TO GEOJSON FILE FOR CHECKING:
    def formingToGeoJson(self, coordinates):
        if coordinates == []:
            return None
        start_point = coordinates[0]
        end_point = coordinates[-1]

        line_string_geometry = {
            "type": "LineString",
            "coordinates": coordinates
        }
        
        start_point_geometry = {
            "type": "Point",
            "coordinates": start_point
        }
        
        end_point_geometry = {
            "type": "Point",
            "coordinates": end_point
        }

        line_string_feature = {
            "type": "Feature",
            "geometry": line_string_geometry,
            "properties": {
                "Type": "LineString"
            }
        }
        
        start_point_feature = {
            "type": "Feature",
            "geometry": start_point_geometry,
            "properties": {
                "Type": "StartPoint"
            }
        }
        
        end_point_feature = {
            "type": "Feature",
            "geometry": end_point_geometry,
            "properties": {
                "Type": "EndPoint"
            }
        }

        geojson_data = {
            "type": "FeatureCollection",
            "features": [line_string_feature, start_point_feature, end_point_feature]
        }
        
        formatted_geojson = json.dumps(geojson_data, indent=4)
        
        file_path = os.path.join(os.getcwd(), "GeoJsonOutput", "GeoJsonOutput.geojson")
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(formatted_geojson)
        
        print("GeoJSON data has been formed and written to GeoJsonOutput.geojson file.")
        return formatted_geojson