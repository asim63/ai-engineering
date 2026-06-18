import json
def load_json(path):
    try:
        with open(path,"r",encoding = "utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"{path} not found")
        return {}
    except json.JSONDecodeError:
        print(f"{path} contains invalid JSON")
        return {}
    except Exception as e:
        print(f"Unexpected error : {e}")
        return {}

def save_json(path, data):
    with open(path,"w",encoding = "utf-8") as file:
        json.dump(data, file, indent= 4)