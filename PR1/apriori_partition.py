from apriori import Apriori
import math
import itertools
from collections import Counter


class AprioriPartition:
    def __init__(self, data, support_count, confidence_pct, k):
        self.k = k
        self.data = data
        self.length = len(data)
        self.support_pct = support_count / self.length
        self.confidence_pct = confidence_pct
        self.support_count = support_count
        self.candidates = {}
        self.all_frequent = self.prune_candidates()
        self.associations = self.generate_all_rules()

    def partition_data(self):
        chunks = self.k
        partitioned = {}
        chunksize = self.length // chunks
        items = iter(self.data.items())

        for i in range(chunks - 1):
            partitioned['chunk_{}'.format(i)] = dict(
                itertools.islice(items, chunksize))
        else:
            partitioned['chunk_{}'.format(chunks - 1)] = dict(items)
        return partitioned

    def generate_candidates(self):
        partitions = self.partition_data()
        for key, value in partitions.items():
            candidates = Apriori(
                value, self.support_count // self.k, self.confidence_pct).all_frequent
            A = Counter(self.candidates)
            B = Counter(candidates)
            C = A + B
            c = dict(C)
            self.candidates = c

    def prune_candidates(self):
        self.generate_candidates()
        print(self.support_count)
        freq = {key: value for key, value in self.candidates.items()
                if value > self.support_count}
        return freq

    def itemset_difference(self, itemset, subset):
        """Generates a list of two tuples: [(s), (l-s)].
        Args:
          itemset: a frequent itemset.
          subset: a subset of the frequent itemset.
        Raises:
          TypeError: If itemset is not of type tuple.
          TypeError: If subset is not of type tuple.
        Returns:
          The list: [s, (l-s)].
        """
        if (type(itemset)) != tuple:
            raise TypeError('itemset needs to be a tuple')
        if (type(subset)) != tuple:
            raise TypeError('subset needs to be a tuple')

        diff = [tuple(sorted(subset)), tuple(
            sorted(set(itemset).difference(set(subset))))]

        if len(diff[0]) == 1:
            diff[0] = ''.join(diff[0])

        if len(diff[1]) == 1:
            diff[1] = ''.join(diff[1])

        return diff

    def generate_candidate_rules(self, freq_itemset, k):
        """Generates a list of all rules candidates for an itemset: [(s), (l-s)].
        Args:
          freq_itemset: a frequent itemset in the form of a tuple.
        Returns:
          All possible rules for the itemset.
        """
        all_rules = []

        for i in range(k-1, 0, -1):  # loop through k choose i
            combinations = list(itertools.combinations(
                freq_itemset[0], i))  # get all combinations
            candidates = list(map(lambda x: self.itemset_difference(
                freq_itemset[0], x), combinations))
            all_rules.extend(candidates)

        return all_rules

    def get_support_confidence(self, rule_set, curr_support_count):
        support = curr_support_count / self.length
        confidence = curr_support_count / self.all_frequent[rule_set[0]]

        rule_set.extend([support, confidence])
        return rule_set

    def prune_candidate_rules(self, freq_itemset, itemset_count, k):
        """Tests the candidates for one frequent itemset and prunes < min_confidence
        Args:
          freq_itemset: a frequent itemset in the form of a tuple.
          itemset_count: count of the itemset in the data
        Raises:
          ValueError: If freq_itemset is not of type tuple.
        Returns:
          All possible rules for the itemset.
        """

        if self.confidence_pct > 1 or self.confidence_pct < 0:
            raise ValueError('support_pct must be in the range [0,1]')

        max_count = math.floor(
            itemset_count / self.confidence_pct)  # max denominator
        all_rules = self.generate_candidate_rules(
            freq_itemset, k)  # generate all rules from itemset
        pruned_rules = list(filter(lambda x: self.all_frequent[(
            x[0])] <= max_count, all_rules))  # filter out right side
        # add support, confidence to rules
        list(map(lambda x: self.get_support_confidence(
            x, itemset_count), pruned_rules))

        return pruned_rules

    def generate_all_rules(self):

        associations = []
        for key, value in self.all_frequent.items():
            if (isinstance(key, str)):
                k = 1
            else:
                k = len(key)
            pruned_rules = self.prune_candidate_rules([key], value, k)
            associations.extend(pruned_rules)
        self.associations = associations
        return associations
