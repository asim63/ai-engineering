# Day 16 - Python for AI Essentials

## CSV Handling

### csv module
```python
import csv
```

* Learned how CSV files store tabular data.
* Practiced reading and writing CSV files using Python's built-in csv module.
---
### Pandas
```bash
pip install pandas
```

```python
import pandas as pd
```
* Learned to read CSV files using `pd.read_csv()`.
* Understood DataFrames as in-memory spreadsheet-like structures.
* Accessed columns and rows using:

  * `df["column"]`
  * `df.loc[]`
* Learned to create DataFrames from dictionaries.
* Exported DataFrames using `df.to_csv()`.
---
## Virtual Environment Troubleshooting

* Encountered a situation where pandas was installed globally but unavailable inside the virtual environment.
* Learned the importance of installing packages using:

```bash
python -m pip install package_name
```

* Understood the difference between global Python packages and venv packages.
---
## Project Structure

### Reusable Utilities

Created a plan for a reusable utility package:

* file_utils.py
* json_utils.py
* history_utils.py

Purpose:

* Avoid rewriting common functions.
* Improve project organization.
* Prepare for larger AI Engineering projects.
---
### Utility Functions

Implemented reusable functions for:

* Reading text files
* Writing text files
* Loading JSON
* Saving JSON
* Truncating conversation history
---