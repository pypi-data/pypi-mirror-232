Flask-Tenable
=============

[![PyPI version](https://badge.fury.io/py/Flask-Tenable.svg)](https://pypi.org/project/Flask-Tenable)
[![Python version](https://img.shields.io/badge/Python-3.7_%7C_3.8_%7C_3.9_%7C_3.10_%7C_3.11-blue)]()

---

Flask-Tenable is a thin wrapper for [pyTenable](https://pypi.org/project/pyTenable/)
that enables the easy integration of [pyTenable](https://pypi.org/project/pyTenable/)
into [flask](https://pypi.org/project/flask/) applications.

To use the wrapped [pyTenable objects](https://pytenable.readthedocs.io/en/stable/)
app.config must contain the following configs:

| Product   | Required configs                                                          |
|-----------|---------------------------------------------------------------------------|
| Downloads | TENABLE_DOWNLOADS_API_TOKEN                                               |
| Nessus    | TENABLE_NESSUS_HOST, TENABLE_NESSUS_ACCESS_KEY, TENABLE_NESSUS_SECRET_KEY |
| TenableAD | TENABLE_AD_API_KEY                                                        |
| TenableIO | TENABLE_IO_ACCESS_KEY, TENABLE_IO_SECRET_KEY                              |
| TenableOT | TENABLE_OT_API_KEY                                                        |
| TenableSC | TENABLE_SC_HOST, TENABLE_SC_ACCESS_KEY, TENABLE_SC_SECRET_KEY             |

---

### Usage

#### Basic workflow

```python
from flask import Flask
from flask_tenable import Tenable

app = Flask(__name__)

# Add the configs for the products you want to use
app.config['TENABLE_SC_HOST'] = 'localhost:8834'
app.config['TENABLE_SC_ACCESS_KEY'] = '<access_key>'
app.config['TENABLE_SC_SECRET_KEY'] = '<secret_key>'

# Initialize the extension
tenable = Tenable()
tenable.init_app(app)

# Access the pyTenable objects through the tenable object
@app.route('/scans')
def scans():
    return f'Scans in TenableSC: {tenable.sc.scans.list()}'

if __name__ == '__main__':
    app.run()
```

#### Accessing the different pyTenable APIs

```python
from flask import Flask
from flask_tenable import Tenable

app = Flask(__name__)

# Initialize the extension
tenable = Tenable()
tenable.init_app(app)

# Access the APIs with their pyTenable module name
tenable.dl      # Downloads API
tenable.nessus  # Nessus API
tenable.ad      # TenableAD API
tenable.io      # TenableIO API
tenable.ot      # TenableOT API
tenable.sc      # TenableSC API
```