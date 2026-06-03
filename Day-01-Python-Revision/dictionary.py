book = {
    "author":"J.K Rowling",
    "title":"Harry Potter",
    "year": 1945
}

print(type(book))

#access 
print(book["author"])
x = book.get("author")
print(x)
y = book.keys()
print(y)
print(type(y))

#change values
book["year"] = 1888
book["genre"] = "magic"
book.update({"year": 1899})
print(book)
print(y)

#loop 
for x in book.values():
    print(x)
    
for x in book.keys():
    print(x)