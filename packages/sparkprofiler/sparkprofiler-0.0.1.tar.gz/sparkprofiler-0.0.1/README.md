# PySpark Data Profiler
This development is designed to have an overview of the data you're working with using Spark as the tool to load the data.

---
## Install requirements
The first step is to install all the requirements needed for this development.

Assuming you're starting from scratch, you need to install the libraries that are available on the requirements.txt file.

```python
pip install -r requirements.txt
```

The development is done with the following versions:
* Python: 3.11.4
* PySpark: 3.5.0

---
## Data Profiler
```python
import pprint
from profiler.data_reader.reader import Reader
from profiler.data_profiler.profiler import Profiler

### READ DATA ###
# To create a spark data frame from a csv or parquet file
df = Reader('person.csv').data
print(df.show())

### PROFILE DATA ###
# To profile the data, load a Spark data frame
profiler = Profiler(df)

### GLOBAL STATS ###
# Generate a global report
global_stats = profiler.global_report()
pprint.pprint(global_stats) # using pprint to pretty print the JSON

### COLUMN LEVEL STATS ###
# generate a JSON to evaluate certain columns
config_cols = profiler.config()
pprint.pprint(config_cols)
# select columns to evaluate
# all columns are defaulted to 'Yes', change to 'No' to select certain columns
config_cols['COLUMN_1'] = 'No'
config_cols['COLUMN_2'] = 'No'
# generate report
data_stats = profiler.column_report(config=config_cols)
pprint.pprint(data_stats)

# if the config parameter is not populated, all the columns are evaluated
data_stats_full = profiler.column_report()
pprint.pprint(data_stats_full)
```
