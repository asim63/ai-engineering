#opening a file
#append mode
with open(r"Day 01-Python Revision\data.txt","a") as file:
    file.write("Opening a file, creates a new one by itself\n")
    
#write mode  
with open(r"Day 01-Python Revision\data2.txt","w") as file:
    file.write("Replace the previous content in write mode\n")
    file.write("Test another test")
    
#read mode
with open(r"Day 01-Python Revision\data2.txt","r") as file:
    content = file.read()
    print(content)
    
    
#closing a file(if not using with statement must write a close statement)
f = open(r"Day 01-Python Revision\data2.txt")
print(f.readlines()) #readline reads single line, readlines creates list of multiple lines
f.close()

#deleting a file
import os
# os.remove(r"Day 01-Python Revision\data.txt")

#exception handling
try:
    with open("abc.txt", "r") as file:
        content = file.read()

except FileNotFoundError:
    print("File not found")
    
#count words in a file
try:
    with open("Day 01-Python Revision\data2.txt","r") as file:
        content = file.read()
        x = len(content.split())
        print(f"No of words: {x}")
        
except FileNotFoundError:
    print("File not found")