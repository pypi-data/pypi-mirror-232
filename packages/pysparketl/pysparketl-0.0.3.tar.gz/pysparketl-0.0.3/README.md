## Pyspark ETL

This project aims at solving common problems that face data engineers.

One problem is to handle deeply nested json data and render data in a clean tabular format.

This kind of semistructured data may contain a combination of different data types that need to be handled differently to flatten the data properly.

This package does just that!

In this initial version of the package, there is one module named **pysparketl** which has one main function: **flattenDF** and two utility functions: **_getArrayCols**,  **_explodeArrayCols**.

### Usage
flattenDF(df) where df is a pyspark dataframe that has nested data in its columns.
The returned dataframe will be a completely flat/tabular structure.

#### Example
##### Install the Package
```zsh
pip install pysparketl
<!-- OR -->
pip3 install pysparketl
```

##### Import and Use
```python
# Import the library
from pysparketl.dataframes import flattenDF

# Read your input dataframe that contains Json data
rawJsonDF = spark.read.json(pathToFile)

# Pass your nested json dataframe as input to the flattenDF function
flattenedDF = flattenDF(rawJsonDF)

# flattenedDF will be a flat dataframe instead as a result.
```