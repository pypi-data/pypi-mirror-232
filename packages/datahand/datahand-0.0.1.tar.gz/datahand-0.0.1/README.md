# Data Handler (datahand)

DataHandler is a collection of algorithms to read and handle data for research (e.g., Web of Science, USPTO) in Python.

DataHandler allows to manage a variety of typical sources used for research in Pandas.

## Installation

To install DataHandler, we recommend to use PyPI:

```
pip install datahandler
```

## First steps

### 1. Read data from Web of Science

```
from datahandler import read_wos

df = read_wos("file/to/path.txt")
```
