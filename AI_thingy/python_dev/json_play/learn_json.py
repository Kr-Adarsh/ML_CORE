import json

# ref: https://docs.python.org/3/library/json.html

""" quick_notes: 
json.load -> load file as json in python
json.loads -> load string as json in python
json.dump -> dump json as file
json.dumps -> dump json as string
"""

people_string ="""
{
    "people": [
    {
        "name": "John Smith",
        "phone": "615-555-7164",
        "emails": ["johnsmith@bogusemail.com", "john.smith@work-place.com"] ,
        "has license": false 
    },
    {
        "name": "Jane Doe",
        "phone": "560-555-5153",
        "emails": null,
        "has_license": true
    }]
}
"""


# ---------- #1 python-string to json
# let's convert the python-string to json - cnoversion happend according to conversion table : use ref~

data = json.loads(people_string)
# print(data)

for person in data["people"]:
    print(person)


# --------- #2 json to python_string
new_str = json.dumps(data, indent=2,) #use indent to cleanly see the string..
print(new_str)

# explore diffrent parameters of json.dumps(...)