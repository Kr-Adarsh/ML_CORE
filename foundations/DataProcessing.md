# Data Preprocessing & Feature Engineering Cheat Sheet

## 1. Data Splitting (Do this FIRST!)
If you preprocess your entire dataset before splitting it, your model will "cheat" by learning the mean/variance of the test set during scaling or imputation. This is called data leakage. Always split first!


| Method | Scikit-Learn Class | Use Case |
| :--- | :--- | :--- |
| **Standard Split** | `train_test_split()` | The classic 70/30 or 80/20 split into Training and Testing sets. |
| **Stratified Split** | `StratifiedShuffleSplit()` | Ensures the proportion of classes in the target variable ($y$) is the same in both sets. Crucial for classification. |

```python
from sklearn.model_selection import train_test_split
import pandas as pd

# Dummy data
X = pd.DataFrame({'age': [22, 25, 47, 35, 46], 'salary': [50k, 60k, 120k, 80k, 110k]})
y = pd.Series([0, 1, 1, 0, 1])

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"Train size: {len(X_train)}, Test size: {len(X_test)}")

# Expected Output:
# Train size: 4, Test size: 1

```

---

## 2. Handling Missing Values (Imputation)

Missing data is a reality, and most models will flat-out crash if they encounter a `NaN`. Don't just delete rows with missing data unless absolutely necessary—you're throwing away valuable information.

| Imputer | Scikit-Learn Class | Strategy |
| --- | --- | --- |
| **Simple Imputer** | `SimpleImputer()` | `strategy='mean'` (symmetric data), `'median'` (skewed data/outliers), `'most_frequent'` (categorical). |
| **KNN Imputer** | `KNNImputer()` | Predicts missing values based on the 'k' nearest neighbors. Great when features are highly correlated. |

```python
from sklearn.impute import SimpleImputer
import numpy as np

# Data with a missing value
X_train = np.array([[7, 2, 3], [4, np.nan, 6], [10, 5, 9]])

imputer = SimpleImputer(strategy='mean')
X_train_imputed = imputer.fit_transform(X_train)
print(X_train_imputed)

# Expected Output:
# [[ 7.   2.   3. ]
#  [ 4.   3.5  6. ]
#  [10.   5.   9. ]]

```

---

## 3. Outlier Detection & Handling

Outliers can completely derail algorithms that rely on averages or distances (like Linear Regression). You need to handle them before you scale your data.

### Detection & Treatment

* **Z-Score Method:** Identifies outliers as data points usually $z > 3$ or $z < -3$ standard deviations from the mean.
* **IQR Method:** Based on quartiles. Lower Bound = $Q_1 - 1.5 \times \text{IQR}$, Upper Bound = $Q_3 + 1.5 \times \text{IQR}$.
* **Isolation Forest:** An algorithm that isolates anomalies instead of profiling normal points.

```python
from sklearn.ensemble import IsolationForest
import numpy as np

# Normal data + one massive outlier
X_train = np.array([[10], [12], [11], [14], [1000]]) 

iso = IsolationForest(contamination=0.2, random_state=42)
predictions = iso.fit_predict(X_train)
print(predictions) 

# Expected Output:
# [ 1  1  1  1 -1]  <- The '-1' indicates the anomaly (1000)

```

---

## 4. Encoding Categorical Data

Machine learning models are just fancy calculators; they only understand math. If you feed them text like "Red" or "Blue", they will panic. We have to convert text to numbers.

* **Rule of Thumb:** Features ($X$) are usually 2-D arrays. The Target ($y$) is a 1-D array.

| Data Type | Scikit-Learn Class | Description |
| --- | --- | --- |
| **Nominal** (No order, e.g., Colors) | `OneHotEncoder()` | Creates binary columns for each category (0s and 1s). Prevents false numerical order. |
| **Ordinal** (Has order, e.g., Low/Med/High) | `OrdinalEncoder()` | Assigns integers to categories based on order (0, 1, 2). |
| **Target Variable ($y$)** | `LabelEncoder()` | Converts categorical targets (like 'Spam'/'Not Spam'). **Never use on features ($X$).** |

```python
from sklearn.preprocessing import OneHotEncoder
import numpy as np

# Categorical feature: ['Red', 'Blue', 'Green']
X_train_colors = np.array([['Red'], ['Blue'], ['Red']])

encoder = OneHotEncoder(sparse_output=False)
X_encoded = encoder.fit_transform(X_train_colors)
print(X_encoded)

# Expected Output (Alphabetical order: Blue, Red):
# [[0. 1.]  <- Red
#  [1. 0.]  <- Blue
#  [0. 1.]] <- Red
```
#### why ohe > label encoding for features?
For features like race, religion, and gender, there is no mathematical "order."

- If you map {Christian: 1 and Muslim: 2}, a machine learning model might think that *"Muslim" is "twice as much" as "Christian" or that 2 is "greater than" 1*.

- OHE avoids this by giving each category its own "on/off" (1 or 0) switch. This is the standard "correct" way for most algorithms (like Linear Regression or SVMs).


---

## 5. Feature Scaling

If one feature is measured in thousands (like Salary) and another in single digits (like Years of Experience), distance-based algorithms (KNN, SVM, PCA) will blindly assume the larger number is more important. Scaling levels the playing field.

| Scaler | Class | Formula / Behavior | Best For |
| --- | --- | --- | --- |
| **Standardization** | `StandardScaler()` | $z = \frac{x - \mu}{\sigma}$ (Mean=0, Var=1) | Algorithms assuming normal distribution (Linear Reg, SVM). |
| **Normalization** | `MinMaxScaler()` | $x_{scaled} = \frac{x - x_{min}}{x_{max} - x_{min}}$ | Hard boundaries (images, Neural Nets). |
| **Outlier-Proof** | `RobustScaler()` | Uses median and IQR. | Data severely skewed by extreme outliers. |

```python
from sklearn.preprocessing import StandardScaler
import numpy as np

# [Salary, Years Experience]
X_train = np.array([[50000, 1], [100000, 5], [150000, 10]])

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_train)
print(X_scaled)

# Expected Output:
# [[-1.22  -1.13]
#  [ 0.     -0.11]
#  [ 1.22   1.25]]

```

---

## 6. Feature Transformation & Engineering

Sometimes raw numbers are fine, but their shape needs tweaking so the algorithm can digest them better.

* **Log Transformation (`np.log1p()`):** Tames heavily right-skewed data (like income) into a normal curve.
* **Polynomial Features (`PolynomialFeatures()`):** Generates new features by multiplying existing ones together. Helps linear models capture curves.

```python
import numpy as np

# Highly skewed income data
income = np.array([1000, 2000, 500000])

# Apply log(1 + x) transformation
log_income = np.log1p(income)
print(log_income)

# Expected Output:
# [ 6.908  7.601 13.122] <- The massive outlier is mathematically tamed

```

---

## 7. Dimensionality Reduction (Curse of Dimensionality)

Having 1,000 features sounds great until your model starts memorizing noise, overfitting, and taking three days to train.

* **PCA (Principal Component Analysis):** Squishes features down into fewer dimensions while keeping the most important statistical variance. Creates entirely *new* abstract features.
* **Feature Selection (`SelectKBest`, RFE):** Actually drops the useless columns and keeps the best original ones.
* **RFE (Recursive Feature Elimination):** Iteratively removes the least important features based on model coefficients.

```python
from sklearn.decomposition import PCA
import numpy as np

# 3 Features
X_train = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

# Reduce down to 2 dimensions
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_train)
print(X_pca)

# Expected Output (Dimensions reduced from 3 to 2):
# [[-5.19  0.  ]
#  [ 0.    0.  ]
#  [ 5.19  0.  ]]

```

---

## 8. Handling Imbalanced Datasets

If you're predicting bank fraud, 99.9% of your data will be "Not Fraud". If your model just guesses "Not Fraud" every single time, it boasts 99.9% accuracy, but it's completely useless.

* **Oversampling (SMOTE):** Uses KNN to artificially synthesize new data points for the minority class.
* **Class Weights:** Built into most `sklearn` models (`class_weight='balanced'`). It heavily penalizes the model for getting the rare class wrong.

```python
from sklearn.ensemble import RandomForestClassifier

# Instead of manually resampling, tell the model to pay attention to the rare class
clf = RandomForestClassifier(class_weight='balanced', random_state=42)
print(clf.get_params()['class_weight'])

# Expected Output:
# 'balanced'

```

---

## 9. Model Fit: Overfitting vs. Underfitting

This is the ultimate balancing act. You want a model that learns the underlying pattern, not one that memorizes the exact answers or fails to understand the assignment entirely.

### Underfitting (High Bias)

* **What it is:** The model is too simple. It performs poorly on *both* training and test data.
* **Fixes:** Use a more complex algorithm, engineer better features, or reduce regularization.

### Overfitting (High Variance)

* **What it is:** The model memorized the training data perfectly but fails completely on the test data.
* **Fixes:** Get more data, apply regularization (L1/Lasso, L2/Ridge), or remove noisy features.

```python
# Conceptual example of checking for overfitting
train_accuracy = 0.99  # 99%
test_accuracy = 0.65   # 65%

if train_accuracy - test_accuracy > 0.20:
    print("Warning: Model is likely Overfitting!")

# Expected Output:
# Warning: Model is likely Overfitting!

```

---

## 10. Cross-Validation

Don't trust a single Train/Test split. You might have just gotten lucky with an "easy" test set. Cross-validation forces the model to prove its worth multiple times.

* **K-Fold Cross-Validation:** Cuts the dataset into 'k' slices. It trains on k-1 slices and tests on the last one. It repeats this until every slice has been the test set.
* **Stratified K-Fold:** Same as above, but ensures each slice has the exact same ratio of target classes as the whole dataset.

```python
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.datasets import make_classification

# Generate dummy classification data
X, y = make_classification(n_samples=100, random_state=42)
model = LogisticRegression()

# 5-Fold Cross Validation
scores = cross_val_score(model, X, y, cv=5)
print(f"Scores: {scores}")
print(f"Mean Accuracy: {scores.mean():.2f}")

# Expected Output:
# Scores: [1.   0.95 1.   0.9  1.  ]
# Mean Accuracy: 0.97

```
---
*Might add/update more things later..*
