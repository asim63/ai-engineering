myfamily = {
  "child1" : {
    "name" : "Emil",
    "year" : 2004
  },
  "child2" : {
    "name" : "Tobias",
    "year" : 2007
  },
  "child3" : {
    "name" : "Linus",
    "year" : 2011
  }
}
#access elements
print(myfamily["child1"]["name"])

#loop within
for x,y in myfamily.items():
    print(x + ":",y)
    
x = myfamily.get("child2")
print(x["name"])