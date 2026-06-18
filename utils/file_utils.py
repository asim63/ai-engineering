def read_text(path):
    try:
        with open(path,"r",encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        print(f"{path} not found")
        return {}
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {}

def write_text(path, data):
    with open(path,"w", encoding="utf-8") as file:
        file.write(data)