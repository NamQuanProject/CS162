import os
import json 
import csv



class Stop():
    def __init__(self, StopId, Code, Name , StopType, Zone , Ward, AddressNo, Street, SupportDisability, Status, Lng, Lat, Search, Routes, RouteId, RouteVarId):
        self.stopId = StopId
        self.code = Code
        self.name = Name 
        self.stopType = StopType
        self.zone = Zone 
        self.ward = Ward 
        self.addressNo = AddressNo 
        self.street = Street 
        self.supportDisability = SupportDisability 
        self.status = Status 
        self.lng = Lng 
        self.lat = Lat
        self.search = Search
        self.routes = Routes 
        self.routeId = RouteId
        self.routeVarId = RouteVarId
    
    def getStop(self, *argv):
        result = {}
        allowed_properties = list(self.__dict__.keys())
        for arg in argv:
            if arg not in allowed_properties:
                raise ValueError(f"Invalid property {arg} in the property of Stop" + '\n' + f"Properties should look for {allowed_properties}")
        for arg in argv:
            result[arg] = getattr(self, arg)
        return result

    def setStop(self, **kwargs):
        allowed_properties = list(self.__dict__.keys())


        for key, value in kwargs.items():
            if key not in allowed_properties:
                raise ValueError(f"Invalid property: {key}")
            
        for key, value in kwargs.items():
            setattr(self, key, value)
            print("Successfully reset the RouteVar properties!")
            return True
    

class StopQuery():
    def __init__(self):
        self.stopquery = []
    
    def read_data(self, file_path):
        try:
            with open(file_path, "r", newline="") as file:
                data_list = [json.loads(line.strip()) for line in file]
                stop_data = [data["Stops"] for data in data_list]
                result = []
                stop_dict = {}
                for ind, list_of_stop in enumerate(stop_data):
                    for element in list_of_stop:
                        result.append(Stop(RouteId = data_list[ind]["RouteId"], RouteVarId = data_list[ind]["RouteVarId"], **element)) 
                        if data_list[ind]["RouteId"] not in stop_dict: 
                            stop_dict[data_list[ind]["RouteId"]] = {}
                        if data_list[ind]["RouteVarId"] not in stop_dict[data_list[ind]["RouteId"]]:
                            stop_dict[data_list[ind]["RouteId"]][data_list[ind]["RouteVarId"]] = []
                        stop_dict[data_list[ind]["RouteId"]][data_list[ind]["RouteVarId"]].append(Stop(RouteId = data_list[ind]["RouteId"], RouteVarId = data_list[ind]["RouteVarId"], **element))
                self.stopquery = result 
                return stop_dict
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found:")


    def searchByABC(self, **kwargs):
        stop_data = self.stopquery
        searchStop =  [data for data in stop_data if all(data.getStop(key)[key] == value for key, value in kwargs.items())]
        return searchStop
    

    def outputAsCSV(self, query_list):
        home_dir = os.getcwd()
        filename =  os.path.join(home_dir,"Output", "StopOutputAsCSV.csv")
        """

        
        """
        fieldnames = ["stopId","code","name","stopType","zone","ward","addressNo","street","supportDisability","status","lng","lat","search","routes", "routeId", "routeVarId"]

        try:
            with open(filename, newline='', mode='w') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for stop in query_list:
                    data = stop.getStop(*fieldnames)
                    writer.writerow(data)
        except Exception as e:
            print(f"Error with CSV: {str(e)}")
    
    
    def outputAsJson(self , query_list):
        home_dir = os.getcwd()
        filename =  os.path.join(home_dir,"Output", "StopOutputAsJSON.json")
        """
        query_list_shape = [{object, a, b}, {[], a, b}, ...]
        """
        fieldnames = ["stopId","code","name","stopType","zone","ward","addressNo","street","supportDisability","status","lng","lat","search","routes", "routeId", "routeVarId"]
        stop_list = [element.getStop(*fieldnames) for element in query_list]
        
        with open(filename, "w") as file:
            for data in stop_list:
                file.write(json.dumps(data, ensure_ascii= False) + '\n')
