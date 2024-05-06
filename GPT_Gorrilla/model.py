import openai
import json

def get_gorilla_response(prompt, model="gorilla-openfunctions-v1", functions=[]):
  openai.api_key = "EMPTY"
  openai.api_base = "http://luigi.millennium.berkeley.edu:8000/v1"
  try:
    completion = openai.ChatCompletion.create(
      model="gorilla-openfunctions-v2",
      temperature=0.0,
      messages=[{"role": "user", "content": prompt}],
      functions=functions,
    )
    return completion.choices[0].message.content
  except Exception as e:
    print(e, model, prompt)


functions_map = [
    {
       "name": "pathquery",
       'api_name': "pathquery.searchByABC",
       "description": "Find a path of a route that has routeId and the routeVarId",
       "parameters": [
            {"name": "routeId", "description": "Identification of the routeId of the path and can be None"},
            {"name": "routeVarId", "description": "Identification of the routeVarId of the path and can be None"}
        ]
    },
    {
        "name": "routevarquery",
        "api_name": "routevarquery.searchByABC",
        "description": "Find a route or routes",
        "parameters": [
            {"name": "routeId", "description": "Identification of the routeId and can be None"},
            {"name": "routeVarId", "description": "Identification of the routeVarId and can be None"}
        ]
    },
    {
       "name": "stopquery",
       "api_name": "stopquery.searchByABC",
       "description": "Find a bus stop from the bus map",
        "parameters": [
            {"name": "stopId", "description": "Identification of the stop"}
        ]
    },
    {
       "name": "busgraph",
       "api_name": "busgraph.dijkstras_go",
       "description": "Find the path from one place to another and look for the shortest path using dijstras",
       "parameters": [
          {
          "name": "start_stop",
          "description": "where it start",
          },
          {
            "name": "end_stop",
            "description": "Where it end",
          },
       ]
    },
]

def get_prompt(user_query: str, functions: list = []) -> str:
    system = "You are an AI programming assistant, utilizing the Gorilla LLM model, developed by Gorilla LLM, and you only answer questions related to computer science. For politically sensitive questions, security and privacy issues, and other non-computer science questions, you will refuse to answer."
    if len(functions) == 0:
        return f"{system}\n### Instruction: <<question>> {user_query}\n### Response: "
    functions_string = json.dumps(functions)
    return f"{system}\n### Instruction: <<function>>{functions_string}\n<<question>>{user_query}\n### Response: "


def dynamic_function_call(function_string):
    array = function_string.split(".")
    class_name = array[0]
    method_end = array[-1]

    if '(' in method_end:
        method_name, param_part = method_end.split('(', 1)
        parameters = {}
        for param in param_part[:-1].split(","):
            key, value = param.split("=")
            if value != "None":
                parameters[key.strip()] = int(value)
        method_end = method_name
    else:
        method_end = method_name
        parameters = {}

    return class_name, method_end, parameters


def predict (query, queries):
    prompt = get_prompt(user_query = query, functions = functions_map)
    function = get_gorilla_response(prompt = prompt, functions= functions_map)

    print(function)
    class_name, method_last, parameters = dynamic_function_call(function)
   
    # Getting the class dynamically
    cls = queries[class_name]

    
    # Getting and calling the method dynamically
    obj = cls
    result = getattr(obj, method_last)(**parameters)
    return result