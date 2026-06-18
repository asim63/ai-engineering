import csv

#Write CSV
with open(r"Day-16-Python-for-AI\try.csv","w",newline = "")as file:
    
    writer = csv.writer(file)
    writer.writerow(["Name","Age","City"])
    writer.writerow(["Asim",20,"Bkt"])
    writer.writerow(["Sita",30,"Lat"])
    
#Read CSV
with open(r"Day-16-Python-for-AI\try.csv","r")as file:
    reader = csv.reader(file)
    next(reader) # This skips the header)
    print("\n after next(reader) ")
    for row in reader:
        print(row)
        
        print(row[2]) #access specific data
        
#Read as dictionary

with open(r"Day-16-Python-for-AI\try.csv","r")as file:
    reader = csv.DictReader(file)
    print(reader)
    # next(reader) # This skips the header) #dont use this no need
    # print("\n after next(reader)")
    for row in reader:
        print(row)
        
        print(row.get("Name")) #access specific data
                