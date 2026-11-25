# f = open('testfile_.txt') #wrong file name.. 
# instead we're gonna use the try and except blocks

# ---------- #1 
# try: 
# 	f = open('textfile_.txt')
# except Exception:
# 	print("Sorry, this file doesn't exist..")

# print("Process still running..")

	#we try to predict and catch the exceptions and errors and handle it properly.. instead of blocking the python program.. 


# -----------#2

# try:
#     f= open('testfile.txt') #this is correct but
#     var = random_non_exisitng_var #what if this var doesn't exisits? 
    
# except FileNotFoundError:
	# print("Sorry, the var doesn't exist..")

""" we get this error if the issue is not with the file but with variable... 

.venv ❯ python errors_debug.py 
Traceback (most recent call last):
  File "/home/kradarsh/Desktop/ML_core/AI_thingy/python_dev/errors_debug.py", line 19, in <module>
    var = random_non_exisitng_var #what if this var doesn't exisits? 
          ^^^^^^^^^^^^^^^^^^^^^^^
NameError: name 'random_non_exisitng_var' is not defined
"""

# Order ---- #3

# specific errors first
#        ...
# general exceptions later

# try:
#     f = open('testfile.txt')
#     var = random_non_exisitng_var
# except FileNotFoundError as e:
#     print(e)
# except Exception as e:
#     print(e)

#to find the correct specific error.. 


# ---------- #4 else and finally blocks

# used when the try clause doesn't raise the error we desire.. 

# try:
#     f = open('testfile.txt')
# except FileNotFoundError as e:
#     print(e)
# except Exception as e:
#     print(e)
# else: #run if no errors.. 
#     print(f.read())
#     f.close()


# ---------- #5 finally run irrespective of try or except errors.. ideally when you need to use very important resources 

try:
    f = open('testfile.txt')
except FileNotFoundError as e:
    print(e)
except Exception as e:
    print(e)
else: #run if no errors.. 
    print(f.read())
finally:
    print("exiting all the files..")
    f.close()


# --------- # self raised errors

try:
    f = open("corrupt.txt")
    if f.name == 'corrupt.txt':
        raise Exception
except Exception as e:
    print("Error!", e)
else: #run if no errors.. 
    print(f.read())
finally:
    print("exiting all the files..")
    f.close()