```python
# Essential imports
import numpy as np

# Vector creation
x = np.array([1, 2, 3])          # From list
zeros = np.zeros(5)              # Zero vector
ones = np.ones(4)                # Ones vector
range_vec = np.arange(0, 10, 2)  # Range vector

# Operations
y = np.array([4, 5, 6])
addition = x + y                 # Element-wise addition
multiplication = x * y           # Element-wise multiplication
scaling = 3 * x                  # Scalar multiplication
dot_product = x @ y              # Dot product

# Properties
x.shape                          # Vector dimensions
x.ndim                          # Number of dimensions
np.linalg.norm(x)               # L2 norm
np.linalg.norm(x, ord=1)        # L1 norm

# Functions
np.sqrt(x)                      # Square root (element-wise)
np.log(x)                       # Natural logarithm
np.log10(x)                     # Base-10 logarithm
```

## **Matrix. QUICK REFERENCE CHEAT SHEET**

```python
# Creation
M = np.array([[1, 2], [3, 4]])    # From list
Z = np.zeros((2, 3))              # Zeros matrix  
I = np.eye(3)                     # Identity matrix

# Operations  
C = A + B                         # Addition
C = A * B                         # Element-wise multiplication
C = A @ B                         # Matrix multiplication
M_T = M.T                         # Transpose

# Access
element = M[i, j]                 # Single element
row = M[i, :]                     # Entire row
col = M[:, j]                     # Entire column
sub = M[r1:r2, c1:c2]            # Submatrix

# Properties
M.shape                           # Dimensions
np.linalg.matrix_rank(M)         # Rank
np.linalg.inv(M)                 # Inverse
np.linalg.pinv(M)                # Pseudoinverse

# Products
np.dot(x, y)                     # Dot product
np.outer(x, y)                   # Outer product
```


### **Quick Matrix Generation**
```python
# Test matrices for exam problems
identity = np.eye(4)                    # 4×4 identity
zeros = np.zeros((3, 4))               # 3×4 zeros
ones = np.ones((2, 5))                 # 2×5 ones  
range_matrix = np.arange(12).reshape(3, 4)  # Sequential numbers
random_matrix = np.random.randn(3, 3)  # Random normal distribution
```

### **Shape Manipulation Shortcuts**
```python
# Common exam operations
arr = np.arange(24)

# Reshape to different dimensions
matrices = {
    '2x12': arr.reshape(2, 12),
    '3x8':  arr.reshape(3, 8), 
    '4x6':  arr.reshape(4, 6),
    '6x4':  arr.reshape(6, 4),
    '2x3x4': arr.reshape(2, 3, 4)  # 3D tensor
}
```

---

## **11. EXAM TIME-SAVERS** ⚡

### **Verification Tricks**
```python
# Quick checks during exam
M = np.random.randn(3, 4)
print(f"Shape: {M.shape}")              # Verify dimensions
print(f"Total elements: {M.size}")      # Should equal shape product
print(f"Memory usage: {M.nbytes} bytes") # Check efficiency
```
---

## **12. QUICK REFERENCE CHEAT SHEET**

```python
# Essential imports & creation
import numpy as np
arr = np.arange(12).reshape(3, 4)      # Quick test array

# Reshaping
arr.reshape(2, 6)                      # New shape
arr.reshape(-1, 2)                     # Let NumPy calculate dimension
arr.flatten()                          # Always returns copy
arr.ravel()                            # Returns view when possible

# Broadcasting  
arr + np.array([1, 2, 3, 4])          # Row broadcast
arr + np.array([[10], [20], [30]])     # Column broadcast

# Axis operations
arr.sum(axis=0)                        # Column-wise sum
arr.mean(axis=1)                       # Row-wise mean
arr.max(axis=0)                        # Column-wise max

# Stacking
np.vstack((A, B))                      # Vertical stack
np.hstack((A, B))                      # Horizontal stack
np.concatenate((A, B), axis=0)         # General concatenation

# Search & sort
np.argmax(arr)                         # Index of maximum
np.sort(arr, axis=1)                   # Sort along axis
np.argsort(arr)                        # Indices that would sort

# Conditions
np.where(arr > 5, arr, 0)              # Conditional replacement
arr[arr > 5]                           # Boolean indexing
arr[(arr>0) & (arr<5)]

# Comparisons
np.array_equal(A, B)                   # Array equality
(A == B).all()                         # Element-wise equality check
```
