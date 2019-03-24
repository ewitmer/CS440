from sys import argv
import csv
from apriori import Apriori
from fpgrowth import FPTree, FPNode
from apriori_partition import AprioriPartition
import time
import json

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

# writes association results to text file


def write_list_to_file(filename, output, algo, timer):
    with open('output/%s.txt' % filename, 'w') as file:  # write all associations to file
        file.write("=== RESULTS ===\n\n")
        file.write("Algorithm:\t%s\n" % algo)
        file.write("Count:\t\t%d\n\n" % len(output))
        file.write("Finished in %.2f seconds" % timer)
        for item in output:
            file.write("%s\n" % item)

# writes frequen itemset results to text file


def write_dict_to_file(filename, output, algo, timer):
    with open('output/%s.txt' % filename, 'w') as file:
        file.write("=== RESULTS ===\n\n")
        file.write("Algorithm:\t%s\n" % algo)
        file.write("Count:\t\t%d\n\n" % len(output))
        file.write("Finished in %.2f seconds" % timer)
        for key, value in output.items():
            key_str = ''.join(key)
            file.write('%s: %s\n' % (key_str, value))


def test_algos(rules_a, rules_fp):
    for rule in rules_a:
        if rule in rules_fp:
            rules_fp.remove(rule)
        else:
            return False

    if len(rules_fp) == 0:
        return True
    else:
        return False


def run_algorithms(support, confidence):
    start = time.time()
    ap = AprioriPartition(transactions, support, confidence, 4)
    end = time.time()
    ap_time = end - start
    assoc_filename = str(support) + '_associations_ap'
    freq_filename = str(support)+'_freqItemsets_ap'
    write_list_to_file(assoc_filename,
                       ap.associations, 'AprioriPartition', ap_time)
    write_dict_to_file(freq_filename, ap.all_frequent,
                       'AprioriParition', ap_time)
    print("AprioriPartition at support: " + str(support) +
          ", confidence:" + str(confidence))
    print("Frequent Itemsets: " + str(len(ap.all_frequent)))
    print("Associations: " + str(len(ap.associations)))
    print("Time to run: "+str(ap_time)+"\n")

    start = time.time()
    a = Apriori(transactions, support, confidence)
    end = time.time()
    a_time = end - start
    assoc_filename = str(support) + '_associations_a'
    freq_filename = str(support)+'_freqItemsets_a'
    write_list_to_file(assoc_filename,
                       a.associations, 'Apriori', a_time)
    write_dict_to_file(freq_filename, a.all_frequent, 'Apriori', a_time)
    print("Apriori at support: " + str(support) +
          ", confidence:" + str(confidence))
    print("Frequent Itemsets: " + str(len(a.all_frequent)))
    print("Associations: " + str(len(a.associations)))
    print("Time to run: "+str(a_time)+"\n")

    start = time.time()
    fp = FPTree(transactions, support, confidence)
    end = time.time()
    fp_time = end - start
    assoc_filename = str(support) + '_associations_fp'
    freq_filename = str(support) + '_freqItemsets_fp'
    write_list_to_file(assoc_filename,
                       fp.associations, 'FPGrowth', fp_time)
    write_dict_to_file(freq_filename, fp.all_frequent, 'FPGrowth', fp_time)
    print("FPGrowth at support: " + str(support) +
          ", confidence:" + str(confidence))
    print("Frequent Itemsets: " + str(len(fp.all_frequent)))
    print("Associations: " + str(len(fp.associations)))
    print("Time to run: " + str(fp_time) + "\n")
    print("Asserts both algorithms generate the same association rule set: ",
          test_algos(a.associations, fp.associations))
    print("==========================\n")


run_algorithms(15000, .7)
run_algorithms(17500, .7)
run_algorithms(20000, .7)
