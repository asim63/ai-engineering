# Day 01 (Python Basics Revision)

## List

- Learned list in python along with manipulation of elements in list
- Learned list comprehension

Syntax: 
[expression for item in iterable if condition == True]

```python
newlist = [x*x for x in range(3) if x % 2 == 0]
```
## Dictionary

- Learned dictionaries along with nested dictionaries
- Access and manipulate key:value pairs in dictionaru

## JSON

- Learned to parse json to strings and vice versa
```python
import json

json.loads(x) #converts json to python dictionary

json.dumps(y)#converts python string to json
```

## File_handling

- Learned to open and close files in different modes.
- Learned to access the content of files.
- Learned basic error handling during file handling

```python
with open("filename.txt", mode="r") as file:
    content = file.read();
    print(content)

with open("filename.txt", mode="a") as f:
    f.write("text");
```

## API requests

- Learned the fundamentals of API handling in Python using the requests library
- practiced sending GET requests to fetch data

```python
import requests

url = "https://api.example.com/"
response = requests.get(url, timeout = 10) #response body (JSON)
data = response.json() #converts to python dictionary
print(data)

```