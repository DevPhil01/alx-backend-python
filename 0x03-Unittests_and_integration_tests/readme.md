# Utils Unit Tests

This project contains **unit tests** for the `access_nested_map` function defined in `utils.py`.  
The tests validate both **successful lookups** and **KeyError exception cases** using Python’s built-in `unittest` framework.

---

## 📂 Project Structure

* utils.py
* test_utils.py
* README.md


```
- **`utils.py`** → Contains the `access_nested_map`, `get_json`, and `memoize` utilities.
- **`test_utils.py`** → Contains the test cases for `access_nested_map`.
- **`README.md`** → Documentation file.

---

## 🛠 Requirements

- Ubuntu 18.04 LTS  
- Python 3.7  
- `pycodestyle` 2.5  
- `parameterized` library for parameterized tests  

Install dependencies:

```bash
pip install parameterized pycodestyle
```
## 🧪 Tests Implemented
### ✅ Successful lookups
The following cases are tested with assertEqual:

1. nested_map={"a": 1}, path=("a",) → returns 1

2. nested_map={"a": {"b": 2}}, path=("a",) → returns {"b": 2}

3. nested_map={"a": {"b": 2}}, path=("a", "b") → returns 2

### ❌ Exception cases
The following cases are tested with assertRaises(KeyError):

1. nested_map={}, path=("a",) → raises KeyError("a")

2. nested_map={"a": 1}, path=("a", "b") → raises KeyError("b")

The tests also check that the exception message matches the expected missing key.

## ▶️ Running the Tests
Run the tests using:

```
bash
Copy code
python3 -m unittest test_utils.py
```

You should see output similar to:

```
..
----------------------------------------------------------------------
Ran 2 tests in 0.001s

OK
```
