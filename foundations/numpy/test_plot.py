# this is just to test the covarience and correlation funcitons and plot in scatter plot to under the relations 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

ages = np.linspace(20, 60, num=100) # ages from 20 to 60
income = ages * 1000 + np.random.normal(0, 5000, size=100) # income is roughly age*1000 with some noise
plt.scatter(ages, income)
plt.xlabel("Age")
plt.ylabel("Income")
plt.title("Age vs Income")  
# plt.show()

# calculate covariance and correlation and then plot it to visualize the relationship
covr = np.cov(ages, income)[0][1]   
crr = np.corrcoef(ages, income)[0][1]
print(f"Covariance: {covr}")
print(f"Correlation: {crr}")

# let's plot now
plt.scatter(ages, income, label=f"Cov: {covr:.2f}, Corr: {crr:.2f}")
plt.xlabel("Age")
plt.ylabel("Income")    
plt.title("Age vs Income with Covariance and Correlation")
plt.legend()
# plt.show()

# unable to understand the relation or distinguish the relationship between the two variables, we can use a regression line to visualize the trend, let's also calculate the regression line parameters and plot it along with the scatter plot to see the relationship more clearly.
from scipy import stats
slope, intercept, r_value, p_value, std_err = stats.linregress(ages, income)
print(f"Slope: {slope}, Intercept: {intercept}")  
# now let's plot the regression line along with the scatter plot
plt.scatter(ages, income, label=f"Cov: {covr:.2f}, Corr: {crr:.2f}")
plt.plot(ages, intercept + slope * ages, color='red', label='Regression Line')
plt.xlabel("Age")
plt.ylabel("Income")
plt.title("Age vs Income with Regression Line")
plt.legend()
plt.show()