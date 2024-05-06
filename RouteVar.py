import json 
import csv
import os


class RouteVar():
    def __init__(self, RouteId, RouteVarId, RouteVarName, RouteVarShortName, RouteNo, StartStop, EndStop, Distance, Outbound, RunningTime ):
        self.routeId = RouteId
        self.routeVarId = RouteVarId
        self.routeVarName = RouteVarName
        self.routeVarShortName = RouteVarShortName
        self.routeNo = RouteNo 
        self.startStop = StartStop 
        self.endStop = EndStop
        self.distance = Distance 
        self.outbound = Outbound
        self.runningTime = RunningTime

    def getRouteVar(self, *argv):
        result = {}
        allowed_properties = list(self.__dict__.keys())
        for arg in argv:
            if arg not in allowed_properties:
                raise ValueError(f"Invalid property {arg} in the property of RouteVar" + '\n' + f"Properties should look for {allowed_properties}")
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
    

class RouteVarQuery: 
    def __init__(self):
        self.route_vars = []

    def readData(self, file_path): 
        try:
            route_var_dict = {}
            with open(file_path, "r") as file:
                data_list = [json.loads(line.strip()) for line in file] 
                fixed_data_list = [data for data in data_list if data != []]
                for data in fixed_data_list:
                    for ind, innerdata in enumerate(data):
                        route_id = str(innerdata["RouteId"])
                        route_var_id = str(innerdata["RouteVarId"])
                        distance = float(innerdata["Distance"] / 1000)
                        running_time = float(innerdata["RunningTime"] / 60)
                        data[ind] = RouteVar(**innerdata)
                        if route_id not in route_var_dict:
                            route_var_dict[str(route_id)] = {}
                        if route_var_id not in route_var_dict[route_id]:
                            route_var_dict[route_id][route_var_id] = []
                        route_var_dict[route_id][route_var_id] = [distance, running_time]
                    self.route_vars.append(data)
                return route_var_dict
        except FileNotFoundError as e:
            print(f"error: {e}")


    def searchByABC(self, **kwargs):
        """
        Data shape: [[object1 , object2], [object1 , object2], [object1 , object2], ...]
        """
        datas = self.route_vars
        result = []
        try:
            for data in datas:
                searchData = [element for element in data if all(element.getRouteVar(key)[key] == value for key, value in kwargs.items())]
                if searchData != []:
                    result.append(searchData)
                    break
            return result
        except Exception as e:
            print(f"Error: {e}")  
        


    def outputAsCSV(self, query_list):
        home_dir = os.getcwd()
        filename =  os.path.join(home_dir,"Output", "RouteVarOutputAsCSV.csv")
        """
        Format of file: [ [{}, {}] ,  [{} , {}] , ... ]
        """
        try: 
            with open(filename, newline='', mode= 'w', encoding= "utf-8") as csvfile:
                fieldnames = ['routeId', 'routeVarId', 'routeVarName', 'routeVarShortName', 'routeNo', 'startStop', 'endStop', 'distance', 'outbound', 'runningTime']
                writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
                writer.writeheader()
                for data in query_list:
                    data = [element.getRouteVar(*fieldnames) for element in data]
                    writer.writerows(data)
        except Exception as e:
            print(f"Error with CSV: {str(e)}")
            
            
        

    def outputAsJSON(self, query_list):
        """
        Format of file: [ [{}, {}] , [{} , {}] , ... ]
        """
        home_dir = os.getcwd()
        file_path =  os.path.join(home_dir, "Output", "RouteVarOutputAsJSON.json")
        try:
            with open(file_path, 'w' , encoding= "utf-8") as file:
                fieldnames = ['routeId', 'routeVarId', 'routeVarName', 'routeVarShortName', 'routeNo', 'startStop', 'endStop', 'distance', 'outbound', 'runningTime']
                for data in query_list:
                    data = [element.getRouteVar(*fieldnames) for element in data]
                    file.write(json.dumps(data, ensure_ascii= False) + '\n')
        except Exception as e:
            print(f"There is and error : {str(e)}")




