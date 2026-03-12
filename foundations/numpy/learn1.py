"""
Note for LLM:
    - default language -> English
    - default desc -> short and to the point
"""
import numpy as np
import matplotlib.pyplot as plt

# n = np.array([[[1,2,3,4,5], [6,7,8,9,10], [11,12,13,14,15]], [16,17,18,19,20], [21,22,23,24,25]])

n = np.array([[[1,2,3,4,5], [6,7,8,9,10], [11,12,13,14,15]], [[16,17,18,19,20], [21,22,23,24,25], [26,27,28,29,30]], [[31,32,33,34,35], [36,37,38,39,40], [41,42,43,44,45]]])
# print(n)


# print(n.shape)
# print(n.ndim)

n1 = np.zeros((3,4))
# print(n1)
n2 = np.zeros(10)
# print(n2)

"""All about random numbers in numpy"""
########################
# random.random() -> gives a random number between 0 and 1
n3 = np.random.random(10)
print(n3)

n3_ = np.random.random((3,4))
print(n3_)


########################
# random.randint(a,b) -> gives a random integer between a and b-1
n4 = np.random.randint(10) 
print(n4)

n4_ = np.random.randint(1,10, size=(3,4))
print(n4_) # this give a matrix of sixe 3,4 with randon integers between 1 and 9

########################
# random.rand() -> gives a random number between 0 and 1 it's diffrent form random.random() because it can give you an array of random numbers.

n5 = np.random.rand(5)
print(n5)

n5_ = np.random.rand(3,4, 5,2) # matrix of 4 dimensions with size 3,4,5,2 with random numbers between 0 and 1 here the rows are 3, the columns are 4, the depth is 5 and the last dimension is 2

print(n5_, n5_.shape, n5_.ndim)

####################
np.random.seed(10) # this is used to make the random numbers reproducible, it means that every time you run the code with the same seed, you will get the same random numbers.

# testing seed
n6 = np.random.rand(3)
print(n6)

#####################
# random.choice() -> gives a random element from a given array

n7 = np.random.choice([1,2,3,4,5])
print(n7)

n7_ = np.random.choice([1,2,3,4,5], size=(3,4))
print(n7_)

##################
# random.shuffle() -> shuffles the elements of an array in placem while shufffels matrix elements in place but not the rows and columns

np.random.shuffle(n7_)
print(n7_)

#################
n8 = np.random.normal(0,5, size= (3,4)) # random nums from normal distri between 0 and 5 with size 3,4

print(n8)

n9 = np.random.permutation(n8) # just shiffels with out changing the original array
print(n9)

#################
n10 = np.random.uniform(0,1, size=(3,4)) # random nums from uniform distri between 0 and 1 with size 3,4
print(n10)
#same can be done for random.[binomial, poisson, gamma, beta, chisquare, f, multivariate_normal, dirichlet, multinomial, geometric, hypergeometric, pareto, power, rayleigh, wald, zipf and many more distributions]

################
print("End of the random numbers section", "\n\n")

"""matrix creations and manipulations"""

n11 = np.linspace(0,10, num=10) #specific numbers. gives 5 numbers between 0 and 10 with equal spacing
print(n11)

n12 = np.arange(0,10,2) #spedific the spacing.  gives numbers between 0 and 10 with step of 2
print(n12)

"""Arrays operations"""
a = np.array([1,2,3,4,5])
b = np.array([6,7,8,9,10])  

print(a+b) # element wise addition
print(a-b) # element wise subtraction
print(a*b) # element wise multiplication    
print(a/b) # element wise division
print(a**2) # element wise exponentiation
print(np.sqrt(a)) # element wise square root


a1 = np.array([[1,2,3], [4,5,6], [7,8,9]])
print(a1 > 5)
print(1/a1+2)


# this helps in ploting too
# i want to plot complete circle with radius 1 using numpy and matplotlib

x = np.linspace(0,1,1000)
r = 1  
y = np.sqrt(r**2-x**2) #i want to complete complete 
plt.plot(x,y)
plt.xlabel("x")
plt.ylabel("y")
plt.title("Plot of y = sqrt(1-x^2)")
# plt.show()

# to draw a complete circle we can use the following code
theta = np.linspace(0, 2*np.pi, 1000)
x = r * np.cos(theta)
y = r * np.sin(theta) # r is to scale the circle
plt.plot(x,y)
plt.xlabel("x")
plt.ylabel("y")
plt.title("Plot of a circle with radius 1")
plt.axis("equal") # to make the x and y axis have the same scale
# plt.show()

# To learn more refer: https://numpy.org/doc/stable/reference/routines.math.html

print("End of the array operations section", "\n\n")
"""Indexing and Slicing"""
a1 = np.array([[1,2,3], [4,5,6], [7,8,9]])
print(a1[1:, :2]) # this will give us the last two rows and the first two columns

arr = np.random.randint(1,10,size=(4,4))
print(arr)
print(arr[1:-1, 1:-1])
print(arr[2:, 2:])


names = np.array(['Jim', 'Luke', 'Josh', 'Pete'])
first_letter = np.vectorize(lambda x: x[0]) #vectorize applied any function to each element of the array

# to conditionals checks 
first_ltr = np.vectorize(lambda x: x[0])

print(first_letter(names)) # this will give us the first letter of each name in the array

names = np.array(['Jim', 'Luke', 'Josh', 'Pete'])
print(np.vectorize(lambda x: x[0])(names)=='J') # this will give us the first letter of each name in the array
print(names[np.vectorize(lambda x: x[0])(names)=='J']) # this will give us the names that start with J, using the prevoius T and F's

