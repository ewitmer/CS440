import math
import itertools


class Apriori:
    def __init__(self, data, support_count, confidence_pct):
        self.data = self.remove_duplicates(data)
        self.length = len(data)
        self.support_pct = support_count / self.length
        self.confidence_pct = confidence_pct
        self.support_count = support_count
        self.all_frequent = self.find_frequent_itemsets()
        self.associations = self.generate_all_rules()

    def remove_duplicates(self, data):
        """Remove duplicates in transactions.
        Args:
          data: A dict of {key: transactionID, value: transaction items}.
        Raises:
          TypeError: If the data is not of type dict.
        Returns:
          The data with only unique items in each transaction.
          """
        if (type(data)) != dict:
            raise TypeError('Data needs to be in dictionary format')

        for key, value in data.items():
            data[key] = list(set(value))

        return data

    def get_min_support(self, data, support_pct):
        """Returns minimum support count of a data set.
        Args:
            data: A dict of {key: transactionID, value: transaction items}.
            support_pct: minimum support required to be defined as frequent.
        Raises:
            TypeError: If the data is not of type dict.
            ValueErorr: If the support_pct is outside of the range [0,1]
            Returns:
                The support count required to meet the threshold of frequent itemset.
    """
        if (type(data)) != dict:
            raise TypeError('Data needs to be in dictionary format')

        if support_pct > 1 or support_pct < 0:
            raise ValueError('support_pct must be in the range [0,1]')

        return math.ceil(len(data) * support_pct)

    def prune_itemsets(self, candidates):
        """Returns frequent itemsets based on support count.
        Args:
          candidates: A dict of {key: itemset, value: count}.
          support_count: An integer based on number of transactions and support threshold
        Raises:
          TypeError: If the data is not of type dict.
          ValueError: If the support_count is not a positive number
        Returns:
          The frequent itemset.
        """
        if (type(candidates)) != dict:
            raise TypeError('Data needs to be in dictionary format')

        if self.support_count < 0:
            raise ValueError('support_count must be positive')

        remove = [key for key, value in candidates.items() if value <
                  self.support_count]
        for k in remove:  # remove all items that don't meet support count
            del candidates[k]

        return candidates

    def generate_F1(self):
        """Returns frequent itemsets of L1.
        Args:
          data: A dict of {key: transactionID, value: transaction items}.
        Raises:
          TypeError: If the data is not of type dict.
        Returns:
          The count required to meet the threshold of frequent itemset.
        """
        if (type(self.data)) != dict:
            raise TypeError('Data needs to be in dictionary format')

        if (type(self.support_count)) != int:
            raise TypeError('support_count needs to be an integer')

        freq_data = {}  # new dict to store item count

        for key, value in self.data.items():  # for each item in the transaction
            for i in range(len(value)):   # if the key is in the new dict
                if (value[i] in freq_data):
                    freq_data[value[i]] += 1  # increment
                else:
                    freq_data[value[i]] = 1  # else add with count of one

        self.prune_itemsets(freq_data)

        return freq_data  # return the new dict

    def candidate_generation(self, freq_data):
        """Generate L(k+1) from Fk.
        Args:
          freq_data: A dict of frequent itemsets of length k {key: itemset, value: count}.
        Raises:
          TypeError: If the data is not of type dict.
        Returns:
          A list of the possible candidates (tuples) of length k+1.
        """
        if (type(freq_data)) != dict:
            raise TypeError('Data needs to be in dictionary format')

        # sort Lk freq itemset alphabetically
        k_frequent = sorted(list(freq_data.keys()))
        for i in range(len(k_frequent)):
            if (isinstance(k_frequent[i], str)):
                l = (k_frequent[i],)
                k_frequent[i] = l

        k1_candidates = []  # L(k+1) candidates

        for i in range(len(k_frequent)):
            for j in range(i+1, len(k_frequent)):  # for every combination of current
                if (k_frequent[i][:-1] == k_frequent[j][:-1]):  # if (k-1) == (k-1)
                    prefix = k_frequent[i]
                    suffix = k_frequent[j][-1]  # new candidate = k + k[-1]
                    k1_candidates.append((*prefix, suffix))

        return k1_candidates  # return k+1 candidates

    def get_all_subsets(self, candidate, k):
        """Generate all k-1 subsets of a candidate.
        Args:
          candidate: A tuple.
          k: the length of the tuple
        Raises:
          TypeError: If candidates is not of type tuple.
          TypeError: If k is not of type integer.
        Returns:
          A list length k of k-1 length subsets.
        """
        if (type(candidate)) != tuple:
            raise TypeError('candidate needs to be a tuple')

        if (type(k)) != int:
            raise TypeError('k needs to be an integer')

        return list(itertools.combinations(candidate, k-1))

    def has_infrequent_subset(self, subsets, freq_data):
        """Check if candidate as an infrequent subset of length k-1.
        Args:
          candidate: A list L(k-1) of subsets.
          freq_data: freq_data: A dict of frequent itemsets.
        Raises:
          TypeError: If subsets is not of type list.
          TypeError: If freq_data is not of type dict.
        Returns:
          True if the list contains an infrequent subset, False if it doesn't.
        """
        for subset in subsets:
            if subset not in freq_data:
                return True
        return False

    def candidate_pruning(self, candidates, freq_data):
        """Prune candidate itemsets in L(k+1) containing subsets of L(k) that are infrequent.
        Args:
          candidates: A list of tuples of L(k+1).
          freq_data: A dict of frequent itemsets of L(k)
        Raises:
          TypeError: If candidates is not of type list.
          TypeError: If freq_data is not of type dict.
        Returns:
          A pruned list of the possible candidates (tuples) of length k+1.
        """
        if (type(candidates)) != list:
            raise TypeError('candidates needs to be in list format')

        if (type(freq_data)) != dict:
            raise TypeError('freq_data needs to be in dict format')

        k = len(candidates[0])
        if k == 2:  # all L1 subsets are assumed frequent
            return candidates

        for i in reversed(range(len(candidates))):  # for all candidates of length k
            # get all subsets of length k-1
            subsets = self.get_all_subsets(candidates[i], k)
            if (self.has_infrequent_subset(subsets, freq_data)):  # if any subsets are not freq
                candidates.remove(candidates[i])

        return candidates

    def candidate_count(self, candidates):
        """Generate support count of all candidates length k post-prune.
        Args:
          candidates: A list of tuples of L(k).
          data: A dict of transactions
        Raises:
          TypeError: If candidates is not of type list.
          TypeError: If data is not of type dict.
        Returns:
          A dict of candidates of length k with support count.
        """
        if (type(candidates)) != list:
            raise TypeError('candidates needs to be in list format')

        if (type(self.data)) != dict:
            raise TypeError('data needs to be in dict format')

        data_count = {}

        for key, value in self.data.items():
            for candidate in candidates:
                if set(candidate).issubset(set(value)):
                    if (candidate in data_count):
                        data_count[candidate] += 1
                    else:
                        data_count[candidate] = 1
        return data_count

    def find_frequent_itemsets(self):
        """Generate all frequent itemsets from a transaction database.
        Args:
          data: A dict of {key: transactionID, value: transaction items}.
          support_pct: minimum support required to be defined as frequent.
        Raises:
          TypeError: If data is not of type dict.
          ValueErorr: If the support_pct is outside of the range [0,1]
        Returns:
          A dict of all frequent itemsets.
        """
        if (type(self.data)) != dict:
            raise TypeError('Data needs to be in dictionary format')

        if self.support_pct > 1 or self.support_pct < 0:
            raise ValueError('support_pct must be in the range [0,1]')

        all_freq = {}

        frequent = self.generate_F1()  # generate L1 freqent
        all_freq.update(frequent)  # update dict
        candidates = self.candidate_generation(
            frequent)  # generate L2 candidates

        while (candidates != []):
            candidates = self.candidate_pruning(
                candidates, frequent)  # prune candidates
            count = self.candidate_count(candidates)  # support counting
            frequent = self.prune_itemsets(count)  # candidate elimination
            all_freq.update(frequent)  # update frequent itemset dict
            candidates = self.candidate_generation(
                frequent)  # generate new candidates

        return all_freq

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
