# Package for testing pip uploading

Package for the first pip project with some simple code.

## Instructions

1. Install:

```
pip install test_geometry
```

2. Testing script:

```python
import test_geometry.planimetry as pl
import test_geometry.stereometry as st

# Create circle
c1 = pl.Circle(1)
print(c1.square())

# Create ball    
c2 = st.Ball(1)
print(c2.V())
```