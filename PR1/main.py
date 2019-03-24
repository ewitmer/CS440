from sys import argv
import csv
from apriori import Apriori
from fpgrowth import FPTree, FPNode

# import the clean dataset
file = "data/data_clean.csv"
f = open(file, "r")
lines = f.read().split("\n")

transactions = {}
index = 0

for line in lines:
  add = {index: line.split(',')}
  transactions.update(add)
  index += 1

a = Apriori(transactions, 10000, .5)
print(a.all_frequent)
