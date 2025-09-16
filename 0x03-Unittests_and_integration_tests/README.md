# Utilities Module

This project provides a set of utility functions for working with nested maps, making HTTP requests, and memoizing method calls.

---

## Functions

### 1. `access_nested_map(nested_map, path)`
Access values inside nested maps using a path of keys.

**Example:**
```python
from utils import access_nested_map

nested_map = {"a": {"b": {"c": 1}}}
value = access_nested_map(nested_map, ["a", "b", "c"])
print(value)  # Output: 1
```

#### Test Cases
- **Valid paths**:
  - `{"a": 1}, ("a",)` → `1`
  - `{"a": {"b": 2}}, ("a",)` → `{"b": 2}`
  - `{"a": {"b": 2}}, ("a", "b")` → `2`
- **KeyError paths**:
  - `{"a": 1}, ("b",)` → raises `KeyError`
  - `{"a": {"b": 2}}, ("a", "c")` → raises `KeyError`

---

### 2. `get_json(url)`
Fetch JSON from a remote URL.

**Example:**
```python
from utils import get_json

url = "https://api.github.com"
data = get_json(url)
print(data)  # Prints the JSON response as a dict
```

---

### 3. `memoize(fn)`
Decorator to cache method results within a class.

**Example:**
```python
from utils import memoize

class MyClass:
    @memoize
    def a_method(self):
        print("a_method called")
        return 42

obj = MyClass()
print(obj.a_method)  # Prints: a_method called
42
print(obj.a_method)  # Prints: 42
```

---

## Running Tests

Tests are written with `unittest` and `parameterized`.

### Run all tests
```bash
python -m unittest discover
```

### Run a specific test file
```bash
python -m unittest test_utils.py
```

---
