# Data.json Classification 

Script to cluster and categorize datasets from our catalogs using 
data.json


## Install 

pip install -r requirements.txt

## Usage
This script will print out the grouped datasets to stout and also create a html file with d3 code to visualize the clusters.

```bash
python analyze.py data.json -c 10
```

After getting the results, you can visualize 


```bash
python -m "SimpleHTTPServer"
```

