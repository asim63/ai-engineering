person = {
    "name":"asim",
    "address":{
        "city":"Bhaktapur",
        "state":"Bagmati"
    }
}

print(person["address"]["city"])

# print(person["phone"]) # will throw error

print(person.get("phone"))
#OR
print(person.get("phone","Not found"))