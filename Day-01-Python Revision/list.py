#List 
list = ["apple", "banana", "cherry", "apple", "guava", "orange"]
print(list[-1])
print(list[1:3]) # read as index 1 to index 3 i.e index 1 and 2
print(list[2:5]) # 2, 3, 4

list[2] = "changed"
print(list)

#add to the end of list
list.append("new_fruit")
print(list)

#to specific index
list.insert(1,"pear")
print(list) # apple, pear, banana ..., new_fruit

#extend
new_list = ["water", "milk", "juice"]
list.extend(new_list)
print(list)

#remove
list.pop() #removes last item
print(list)

#remove in specific index
list.pop(5)
print(list)
#OR
del list[4]
print(list)

#join two lists
list1 = [1,2,3]
list2 = ['a','b','c']
list3 = list1 + list2
print(list3)