# Mime Common

An package containing misc helper libraries for projects

* console - contains Console class for terminal output including som coler support
* logg - A logging wrapper that do some standardisation

## Installation

Run the following to install:

```python
pip install mime-common
```

## Usage

```python
from console import Console

cons = Console(use_colors=True)

cons.green("Hello World")
```

# Developing Mime Common

To install Mime Common, along with the tools you need to develop and run tests, run the following in your virtualenv:

```bash
$ pip install -e .[dev]
```

