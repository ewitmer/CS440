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
        print ('\t'*level, self.name, ':\t', self.count)
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

        remove = [key for key, value in candidates.items() if value < self.support_count]    
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

        self.prune_itemsets(freq_data) # remove infrequent 
        freq_sorted = sorted(freq_data.items(), key=itemgetter(1), reverse=True)  # sort by value
        f1_sorted = list(map(lambda x: x[0], freq_sorted))  # sorted list of items

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
        if len(self.node_links[node.name]) != 0: # if nodes already exist in the list for value, add lateral link
            self.node_links[node.name][-1].set_lateral_node(node)
        self.node_links[node.name].append(node)  # add node to list at key: node name
    
    def add_node(self, name):
        """Adds node.
        Args:
          name: node name.
        """  
        new_node = FPNode(name, self.current_node, 1)  # create new node
        self.current_node.add_child(new_node) # add as child to new node
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
                self.process_node(item, n) # process the item
    
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
        self.head.print_node() # print tree
        
    def get_path_from_node(self, node):
        """Takes in a single node from tree, returns the prefix path, 
            conditional count and conditional.
        Args:
            node: node on FPTree
        Returns:
            Prefix path, conditional count and conditional value.
        """
        curr = node
        count = node.count
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
        while curr.lateral_node != None: 
            curr = curr.lateral_node
            path = self.get_path_from_node(curr)
            cp.append(path)
        return cp
            
    def build_data_from_cp(self, cp):
        cp_data = {}
        count = 0
        for i in range(len(cp)):
            for j in range(cp[i][1]):
                cp_data.update({count:cp[i][0]})
                count+=1
        return cp_data

    def build_data_from_node(self, node):
        cp = self.get_conditional_pattern(node)
        data = self.build_data_from_cp(cp)
        return data

    def add_to_all_frequent(self, fp):
        self.all_frequent.update(fp)

    @staticmethod
    def mine_data(tree, support_count, confidence_pct, prefix=set(), fp={}):
        for item in tree.f1_sorted[::-1]:
            prefix.add(item)
            header_node = tree.node_links[item][0]
            conditional_data = tree.build_data_from_node(header_node)
            next_tree = FPTree(conditional_data, support_count, confidence_pct)
            if next_tree.head.children != {}:
                for key, value in next_tree.pruned_candidates.items():
                    p = list(prefix)
                    k = list(key)
                    p.extend(k)
                    d = sorted(p)
                    fp.update({tuple(d): value})
                next_tree.mine_data(next_tree, support_count, confidence_pct, prefix, fp)
            prefix = set() 
        return fp

    def mine_all_data(self):
        self.add_to_all_frequent(self.pruned_candidates)
        sub_tree_fp = FPTree.mine_data( self, 
                                        self.support_count, 
                                        self.confidence_pct, 
                                        set(), 
                                        self.all_frequent)
        self.add_to_all_frequent(sub_tree_fp)
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

        diff = [tuple(sorted(subset)), tuple(sorted(set(itemset).difference(set(subset))))]

        if len(diff[0]) == 1:
            diff[0] = ''.join(diff[0])

        if len(diff[1]) == 1:
            diff[1] = ''.join(diff[1])        

        return diff
    
    def generate_candidate_rules(self, freq_itemset):
        """Generates a list of all rules candidates for an itemset: [(s), (l-s)].
        Args:
          freq_itemset: a frequent itemset in the form of a tuple.
        Returns:
          All possible rules for the itemset.
        """
        k = len(freq_itemset) 
        all_rules = []

        for i in range(k-1,0,-1):  # loop through k choose i
            combinations = list(itertools.combinations(freq_itemset, i))  # get all combinations
            candidates = list(map(lambda x: self.itemset_difference(freq_itemset, x), combinations))
            all_rules.extend(candidates)

        return all_rules

    def get_support_confidence(self, rule_set, curr_support_count):
        support = curr_support_count / self.length
        confidence = curr_support_count / self.all_frequent[rule_set[0]]

        rule_set.extend([support, confidence])
        return rule_set

    def prune_candidate_rules(self, freq_itemset, itemset_count):
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

        max_count = math.floor(itemset_count / self.confidence_pct)  # max denominator
        all_rules = self.generate_candidate_rules(freq_itemset)  # generate all rules from itemset
        pruned_rules = list(filter(lambda x: self.all_frequent[(x[0])] <= max_count, all_rules))  # filter out right side
        list(map(lambda x: self.get_support_confidence(x, itemset_count), pruned_rules))  # add support, confidence to rules

        return pruned_rules

    def generate_all_rules(self):
        self.mine_all_data()
        associations = [] 
        for key, value in self.all_frequent.items():
            pruned_rules = self.prune_candidate_rules(key, value)
            associations.extend(pruned_rules)

        return associations


test = {'T100':['M','O','N','K','E','Y'],
        'T200':['D','O','N','K','E','Y'],
        'T300':['M','A','K','E'],
        'T400':['M','U','C','K','Y'], 
        'T500':['C','O','O','K','I','E']}

fp = FPTree(test, 3, .8)
print(fp.generate_all_rules())

