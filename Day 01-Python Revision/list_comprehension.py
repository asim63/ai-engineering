names = ["ram","hari", "sita", "rohan", "dikshant", "asim"]
new_list = []
for x in names:
    if "i" in x:
        new_list.append(x)
        
print(new_list)


#Using list_comprehension
n_list = []
[n_list.append(x) for x in names if "i" in x]
print(n_list)

up_list = [x.upper() for x in names]
print(up_list)

newlist = [x*x for x in range(3) if x%2==0]
print(newlist)