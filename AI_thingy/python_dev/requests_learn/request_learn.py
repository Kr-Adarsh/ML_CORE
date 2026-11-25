import requests

#it's great for getting imformation from site but for parsing it's not great instead use something like Beautiful Soup or request-html.. 

# ------- #1 

r = requests.get('https://xkcd.com/353/')

#print(r) # we got <Response [200]>
# print(dir(r))
# print(help(r))

#print(r.text) #we'll get complete html of the page - to parse use some suitable parser as i said earlier...


# ------- #2
# let's try downloading the image from the url

image = requests.get("https://imgs.xkcd.com/comics/python.png")

#print(image.text) # encoded image: �*0�y�&ľ@߂)|,?K(٤{X��_�V�7�}�e�JM�*Z��-�N�@����..........-��h��h���̩\IEND�B`�


# but we know image is a type of content thus;
#print(image.content) #now we get the unicode: '.....c\xa9\\\x00\x00\x00\x00IEND\xaeB`\x82'

# instead let's save it : 
# with open('comic.png', 'wb') as img_file:
#     img_file.write(image.content)
#     print("image_saved..")


# ------- #3 fetch Status 
# print(r.status_code) #or
#print(r.ok) #true for all < 400 repsonses (>=400 are server errors)

print(r.headers)
