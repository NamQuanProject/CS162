import json
import os

class Path():
    def __init__(self, Coordinates, RouteId, RouteVarId):
        self.coordinates = Coordinates 
        self.routeId = RouteId
        self.routeVarId = RouteVarId

    def getPath(self, *argv):
        result = {}
        allowed_properties = list(self.__dict__.keys())
        for arg in argv:
            if arg not in allowed_properties:
                raise ValueError(f"Invalid property {arg} in the property of Stop" + '\n' + f"Properties should look for {allowed_properties}")
        for arg in argv:
            result[arg] = getattr(self, arg)
        return result

    def setRouteVar(self, **kwargs):
        allowed_properties = list(self.__dict__.keys())
        for key, value in kwargs.items():
            if key not in allowed_properties:
                raise ValueError(f"Invalid property: {key}")
            
        for key, value in kwargs.items():
            setattr(self, key, value)
                    
                
            print("Successfully reset the RouteVar properties!")
            return True
        

class PathQuery():
    def __init__(self):
        self.paths = []
    
    def read_data(self, file_path):
        try:
            with open(file_path, "r") as file:
                data_list = [json.loads(line.strip()) for line in file]
                data = []
                for line in data_list:
                    lat_data = line["lat"]
                    lng_data = line["lng"]
                    coordinate_data = [[lng, lat] for lat, lng in zip(lat_data, lng_data)]
                    routeId = line["RouteId"]
                    routeVarId = line["RouteVarId"]
                    data.append(Path(Coordinates = coordinate_data, RouteId = routeId, RouteVarId = routeVarId))
                self.paths = data
                return self.paths
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        

    def searchByABC(self, **kwargs):
        path_datas = self.paths
        searchPath = [data for data in path_datas if all(str(data.getPath(key)[key]) == str(value) for key, value in kwargs.items())]
        return searchPath
    
    def formingToGeoJson(self, ind):
        if ind < 0 or ind >= len(self.paths):
            raise IndexError("Index out of range")
        
        path = self.paths[ind]
        
        start_point = path.coordinates[0]
        end_point = path.coordinates[-1]

        
        line_string_geometry = {
            "type": "LineString",
            "coordinates": path.coordinates
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
                "RouteId": path.routeId,
                "RouteVarId": path.routeVarId,
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
        
        print("Has Forming the geojson data in geoJsonOutput File")
        return formatted_geojson

    def outputAsJSON(self, query_list):
        try: 
            output_dir = os.path.join(os.getcwd(), "Output")
            file_path = os.path.join(output_dir, "OutputPath.json")
            field_names = ['coordinates', 'routeId', 'routeVarId']
            path_data = [element.getPath(*field_names) for element in query_list]

            with open(file_path, 'w', encoding="utf-8") as file:
                for data in path_data:
                    file.write(json.dumps(data, ensure_ascii=False) + '\n')
        except FileNotFoundError as e:
            print(f"File is not found: Error {e} occured")

                
