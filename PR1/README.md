# Frequent Itemset Mining
The objective of this assignment was to perform frequent itemset mining on  UCI Adult Census Dataset.

## Getting Started
The following will guide you through the file structure so that you can get a copy running locally.

### Prerequisites
You will need Python3 installed on your computer. 

### Installing

Copy the PR1 folder to your machine.

Navigate into the directory

```
cd PR1
```

And run main.py

```
python3 main.py
```
The console output will show a number of sample runs of the various algorithms at varying support and confidence levels. When you run main.py, it will also generate text files with all of the frequent itemsets and associations. These are saved to an output directory. To see this output, navigate to:
```
cd output
```
You can delete these files and run main.py again to see these are in fact generated.  

Note that due to rounding of the support levels in the partitioning enhancement to the Apriori algorithm, there is a small variation in the output. However, the vanilla Aprioiri and FPGrowth algorithms produce the exact same results. A test is inlcuded in the main script which confirms that the results are identical. 

You can delete these files and run main.py again to see these are in fact generated. 

#### File Structure 
```bash
/PR1
|-- apriori_partition.py
|-- apriori.py
|-- fpgrowth.py
|-- main.py
|-- test.py  
|-- Report.pdf
|-- README.md
|-- data
|   |-- data_clean.csv
|-- output
|   |-- [multiple files generated when run]
|-- output_generated
|   |-- [files with output already generated]
```
Additional information regarding the data cleaning process, data structures used to implement the algorithms, and output analysis is avaialble in the report (Report.pdf).

## Author
Erin Witmer 
CSC 440