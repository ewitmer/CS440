import math
import itertools
from operator import itemgetter


class FPNode:
    def __init__(self, name, parent_node, count):
        self.name = name
        self.count = count
        self.parent_node = parent_node
        self.lateral_node = None
        self.children = {}

    def incremenet_count(self, n):
        self.count += n

    def add_child(self, node):
        self.children.update({node.name: node})

    def get_parent(self):
        return self.parent_node

    def set_lateral_node(self, node):
        self.lateral_node = node

    def print_node(self, level=1):
        print('\t'*level, self.name, ':\t', self.count)
        for key, node in self.children.items():
            node.print_node(level+1)


class FPTree:
    def __init__(self, data, support_count, confidence_pct):
        self.data = self.remove_duplicates(data)
        self.confidence_pct = confidence_pct
        self.length = len(data)
        self.support_count = support_count
        self.head = FPNode(None, None, 0)
        self.current_node = self.head
        self.pruned_candidates = None
        self.f1_sorted = self.generate_F1_sorted()
        self.node_links = self.generate_node_links()
        self.tree = self.process_all_transactions(self.data, self.head)
        self.all_frequent = {}
        self.itemset = []
        self.prefix = []
        self.cp_tree = None
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

        self.pruned_candidates = candidates
        return candidates

    def generate_F1_sorted(self):
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

        self.prune_itemsets(freq_data)  # remove infrequent
        freq_sorted = sorted(freq_data.items(), key=itemgetter(
            1), reverse=True)  # sort by value
        f1_sorted = []
        for item in freq_sorted:
            f1_sorted.append(item[0])  # sorted list of items

        return f1_sorted  # return the new dict

    def generate_node_links(self):
        """Returns a dict with key and empty list for nodes as value for each key.
        Returns:
          The dict for the key / node links.
        """
        return {key: [] for key in self.f1_sorted}  # new empty dict

    def add_node_link(self, node):
        """Adds node to dict of links for each key value.
        Args:
          node: Node to be added to list.
        """
        if len(self.node_links[node.name]) != 0:  # if nodes already exist in the list for value, add lateral link
            self.node_links[node.name][-1].set_lateral_node(node)
        # add node to list at key: node name
        self.node_links[node.name].append(node)

    def add_node(self, name):
        """Adds node.
        Args:
          name: node name.
        """
        new_node = FPNode(name, self.current_node, 1)  # create new node
        self.current_node.add_child(new_node)  # add as child to new node
        self.add_node_link(new_node)  # add node to links path/lateral links
        self.current_node = new_node  # make new_node current_node

    def increment_node(self, name, n):
        """If node already exists, increment the count.
        Args:
          name: node name.
        """
        self.current_node = self.current_node.children[name]  # move to node
        self.current_node.incremenet_count(1)  # increment count

    def process_node(self, item, n):
        """If node already exists, increment the count.
        Args:
          item: node name.
        """
        if item in self.current_node.children:  # if the node exists
            self.increment_node(item, n)  # increment
        else:
            self.add_node(item)  # add new node

    def process_transaction(self, item_list, n):
        """Process individual transaction.
        Args:
          item_list: a list of items in a transaction.
        """
        for item in self.f1_sorted:  # for every item in the F1 sorted list
            if item in item_list:  # if it is in the item list
                self.process_node(item, n)  # process the item

    def process_all_transactions(self, data, head, count=1):
        """Processes all transactions in a dataset.
        Returns:
          The FPTree.
        """
        for key, value in data.items():  # for every transaction in the data set
            self.process_transaction(value, count)  # process the transaction
            self.current_node = head  # reset current node to head
        return head  # return head

    def get_tree(self):
        """Method to get tree.
        Returns:
          The FPTree.
        """
        return self.head  # return head

    def print_tree(self):
        """Method to print tree.
        """
        self.head.print_node()  # print tree

    def get_path_from_node(self, node):
        """Takes in a single node from tree, returns the prefix path, 
            conditional count and conditional.
        Args:
            node: node on FPTree
        Returns:
            Prefix path, conditional count and conditional value.
        """
        curr = node  # set curr to node passed in
        count = node.count  # extract count from node
        path = []
        while curr.parent_node.name != None:
            path.insert(0, curr.parent_node.name)
            curr = curr.parent_node
        return (path, count)

    def get_conditional_pattern(self, node):
        """Takes in a node, loops through lateral nodes returns list of prefix paths, conditional counts and conditional.
        Args:
            node: node on FPTree
        Returns:
            Prefix paths, conditional count and conditional value.
        """
        cp = []  # conditional paths
        curr = node  # set current node
        path = self.get_path_from_node(curr)  # process path
        cp.append(path)  # append to list
        while curr.lateral_node != None:  # while there is a lateral link
            curr = curr.lateral_node  # step to the side
            path = self.get_path_from_node(curr)  # get the path
            cp.append(path)  # append the path
        return cp  # return conditional pattern for header node

    def build_data_from_cp(self, cp):
        """Takes in a conditional pattern database and builds a dataset from it.
        Args:
            cp: Conditional patterns with count
        Returns:
            A conditional database formatted as a dataset from which a tree can  be built.
        """
        cp_data = {}  # empty dict
        count = 0  # counter
        for i in range(len(cp)):  # for each set in conditional pattern
            for j in range(cp[i][1]):  # for each time the pattern appears
                # add the pattern to the data that many times
                cp_data.update({count: cp[i][0]})
                count += 1  # update the counter
        return cp_data  # return the new data set

    def build_data_from_node(self, node):
        """Takes in a node and builds a dataset from it.
        Args:
            node: starting node
        Returns:
            A conditional database formatted as a dataset from which a tree can  be built.
        """
        cp = self.get_conditional_pattern(node)  # get conditional pattern
        data = self.build_data_from_cp(cp)  # build data set
        return data  # return dataset

    def mine_node(self, node):
        curr_node = node
        data = self.build_data_from_node(curr_node)

    def mine_data(self, prefix=set(), all_p={}):
        """Static method recursively generates frequent patterns from all conditional databases.
        Args:
            tree: tree to mine
            support_count: from tree
            confidence_pct: from tree
            prefix: prefix pattern, builds through recursion but resets at change of header
            fp: builds through recursion
        Returns:
            All frequent patterns from the conditional database.
        """
        for item in self.f1_sorted[::-1]:  # for each item in the header table
            prefix.add(item)  # push the value to the prefix set
            # get the first node in the list
            header_node = self.node_links[item][0]
            conditional_data = self.build_data_from_node(
                header_node)  # get a dataset from that node
            # build a new tree from the dataset
            next_tree = FPTree(
                conditional_data, self.support_count, self.confidence_pct)
            if next_tree.head.children != {}:  # if that new tree is not a single path,
                # update all frequent patterns with the prefix + each pruned candidate
                for key, value in next_tree.pruned_candidates.items():
                    p = list(prefix)  # prefix
                    k = [key]  # pruned candidate
                    p.extend(k)  # together they are a frequent pattern
                    p.sort()  # sort the list so that it can be accessed
                    # update the frequent patterns data
                    all_p.update({tuple(p): value})
            next_tree.mine_data(prefix, all_p)  # recursively call mine tree
            # when switching to next node in the header tree, reset the prefix
            prefix.remove(item)
        return all_p

    def mine_all_data(self):
        """Returns all frequent patterns for a dataset.
        Returns:
            All frequent patterns from the conditional database.
        """
        self.all_frequent.update(
            self.pruned_candidates)  # add L1 frequent items
        sub_tree_fp = self.mine_data(set(), self.all_frequent)
        self.all_frequent.update(sub_tree_fp)  # add L2+ frequent items
        return self.all_frequent

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
        """Generates all frequent pattern rules
        Returns:
          All possible rules for the itemset.
        """

        self.mine_all_data()  # generate all frequent patterns
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
