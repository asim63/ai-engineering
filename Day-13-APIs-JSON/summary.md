# Day-13 APIs JSON and Environment Management

## API handling 
- Learned to handle get and post request 
- Used `requests` module 
```bash
pip install requests
```

```python
import requests
```
---

## Weather API 
- Used Openweather API to get weather data of a particular city
- Used params while calling the API
---

## requirements.txt
- A file that lists all project dependencies and their versions so the environment can be recreated exactly.
```bash
pip install -r requirements.txt
```
---

## pip freeze
```bash
pip freeze > requirements.txt
```
- It loads all the packages and modules on a project into requirements.txt file.
- Use a virtual environment (venv) per project then use it.