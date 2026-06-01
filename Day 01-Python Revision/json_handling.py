import json

x = {
    "name":"asim",
    "age": 20,
    "city": "bkt"
}
#convert to json
y = json.dumps(x)
print(y)
print(type(y))


#json to python(parse)
x =  '{ "name":"John", "age":30, "city":"New York"}'
y = json.loads(x)
print(type(x))
print(type(y))
print(y["name"])

print(json.dumps({"name": "John", "age": 30}))
print(json.dumps(["apple", "bananas"]))
print(json.dumps(("apple", "bananas")))
print(json.dumps("hello"))
print(json.dumps(42))
print(json.dumps(31.76))
print(json.dumps(True))
print(json.dumps(False))
print(json.dumps(None))