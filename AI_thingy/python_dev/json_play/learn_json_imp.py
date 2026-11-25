import json 
# from urllib.request import urlopen
import requests

response = requests.get('https://open.er-api.com/v6/latest/USD') 
source = response.text 


data = json.loads(source)

# print(json.dumps(data, indent=2))

usd_rates = {}
for rate in data['rates']: #just for practice re-created.. 
    usd_rates[rate] = data['rates'][rate]
# let's try building a currency converions form usd to X

# print(usd_rates)
# print(usd_rates['INR'])

curr = input("enter the currency code of yours.. ")
amt = int(input("enter the amount: "))

print(usd_rates[curr.upper()]*amt, "ruppes")
