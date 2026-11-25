import requests

# ------- #4 : some advance http methods

# r = requests.get('https://httpbin.org/get?page=2&count=2') #prone to mistakes..

payload = {'page': 2, 'count': 25}
r = requests.get('https://httpbin.org/get', params=payload)


# print(r.url) #as we saw payload help clean executions.. 
# print(r.text) 

# -------- #5  sometimes we want to post data

payload = {'username': 'Kradarsh', 'password': 'testing'}
r = requests.post('https://httpbin.org/post', data=payload)

# print(r.url)
# print(r.text)

#print(r.json()) #so you can use the structre or format the website expects the post requests.. like; 

r_dict= r.json()
print(r_dict['form']) #it's clean.. 

# similar for put or other methods..  

# ------------- #6 basic authentication using requests.. 

auth = requests.post("https://httpbin.org/basic-auth/adarsh/testing", auth=('adarshhh', 'testing'))

#print(auth) # wrong username gave [401] that's Unauthorised status_code.. 

# ------------- #7 setting timeout 
# delayed = requests.post("https://httpbin.org/delay/6", timeout=3) # we want to timeout if no request in 3sec
# print(delayed)

# let's also practice the try and catch things.. 
try:
    delayed = requests.post("https://httpbin.org/delay/6", timeout=7) # we want to timeout if no request in 3sec
except requests.exceptions.Timeout:
    print("exited as no resposne in 3secs,, ")
else:
    print(delayed.status_code)

