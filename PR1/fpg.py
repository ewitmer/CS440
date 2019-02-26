import math
from operator import itemgetter

        
class FPNode:
    def __init__(self, name, parent_node):
        self.name = name
        self.count = 1
        self.parent_node = parent_node
        self.children = {}
    
    def incremenet_count(self):
        self.count +=1
        
    def add_child(self, node):
        self.children.update({node.name: node})
        
    def print_node(self, level=1):
        print ('\t'*level, self.name, ':\t', self.count)
        for key, node in self.children.items():
            node.print_node(level+1)

class FPTree:
    def __init__(self, data, support_pct, confidence_pct):
        self.data = self.remove_duplicates(data)
        self.support_pct = support_pct
        self.confidence_pct = confidence_pct
        self.length = len(data)
        self.support_count = self.get_min_support(data, support_pct)
        self.head = FPNode(None, None)
        self.current_node = self.head
        self.f1_sorted = self.generate_F1_sorted()
        self.node_links = self.generate_node_links()
        
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
        return {key: [] for key in self.f1_sorted}
    
    def add_node_link(self, node):
        self.node_links[node.name].append(node)
    
    def add_node(self, name):
        new_node = FPNode(name, self)  # create new node
        self.current_node.add_child(new_node) # add as child to new node
        self.add_node_link(new_node)  # add node to links path
        self.current_node = new_node  # make new_node current_node
        
    def increment_node(self, name):
        self.current_node = self.current_node.children[name]
        self.current_node.incremenet_count()
    
    def process_node(self, item): 
        if item in self.current_node.children:
            self.increment_node(item)
        else:
            self.add_node(item)
    
    def process_transaction(self, item_list):
        for item in self.f1_sorted:
            if item in item_list:
                self.process_node(item)
        self.current_node = self.head
    
    def process_all_transactions(self):
        for key, value in self.data.items():
            self.process_transaction(value)
        
    def print_tree(self):        
        self.head.print_node()


test = {'T100':['M','O','N','K','E','Y'],
        'T200':['D','O','N','K','E','Y'],
        'T300':['M','A','K','E'],
        'T400':['M','U','C','K','Y'], 
        'T500':['C','O','O','K','I','E']}
    
fp = FPTree(test, .6, .8)
fp.process_all_transactions()
fp.print_tree()