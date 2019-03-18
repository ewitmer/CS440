import math
from operator import itemgetter

        
class FPNode:
    def __init__(self, name, parent_node, count):
        self.name = name
        self.count = count
        self.parent_node = parent_node
        self.lateral_node = None
        self.children = {}
    
    def incremenet_count(self, n):
        self.count +=n
        
    def add_child(self, node):
        self.children.update({node.name: node})
        
    def set_lateral_node(self, node):
        self.lateral_node = node
        
    def print_node(self, level=1):
        print ('\t'*level, self.name, ':\t', self.count)
        for key, node in self.children.items():
            node.print_node(level+1)
            
    def get_parent(self):
        return self.parent_node

        
class FPTree:
    def __init__(self, data, support_pct, confidence_pct):
        self.data = self.remove_duplicates(data)
        self.support_pct = support_pct
        self.confidence_pct = confidence_pct
        self.length = len(data)
        self.support_count = self.get_min_support(data, support_pct)
        self.head = FPNode(None, None, 0)
        self.current_node = self.head 
        self.f1_sorted = self.generate_F1_sorted()
        self.node_links = self.generate_node_links()
        self.tree = self.process_all_transactions(self.data, self.head)
        self.all_fp = []
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
        for key, value in data.items():
            self.process_transaction(value, count)
            self.current_node = head
        return head

    def get_tree(self):
        """Method to get tree.
        Returns:
          The FPTree.
        """ 
        return self.head
    
    def print_tree(self):        
        """Method to print tree.
        """ 
        self.head.print_node()
        

    def get_path_from_node(self, node):
        """Takes in a single node from tree, returns the prefix path, conditional count and conditional.
        Args:
            node: node on FPTree
        Returns:
            Prefix path, conditional count and conditional value.
        """
        curr = node
        count = node.count
        conditional = node.name   # update with prefix path
        path = []
        while curr.parent_node.name != None:
            path.insert(0, curr.parent_node.name)
            curr = curr.parent_node
        return (path, count, conditional)
            
            
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
            
    def process_cp(self, cp):
        """Takes in a list of nodes from tree, returns conditional pattern tree.
        Args:
            cp: list of conditional paths with counts
        Returns:
            Prefix path tree.
        """
        start = FPNode(None, None, 0)
        self.current_node = start
        for p in cp:
            self.process_transaction(p[0],p[1])
            self.current_node = start
        start.print_node()
        self.cp_tree = start
        return start
        
    def get_frequent_patterns(self, start):
        if start.children != {}:
            for key, node in start.children.items():

            #    if(node.count >= 1):#self.support_count): 
                self.itemset.append(node.name)
                self.get_frequent_patterns(node)
                self.all_fp.append(self.itemset)
             #   print(self.all_fp)
                self.itemset = []

test = {'T100':['M','O','N','K','E','Y'],
        'T200':['D','O','N','K','E','Y'],
        'T300':['M','A','K','E'],
        'T400':['M','U','C','K','Y'], 
        'T500':['C','O','O','K','I','E']}

fp = FPTree(test, .6, .8)

print(fp.f1_sorted)
path = (fp.get_conditional_pattern(fp.node_links.get('M')[0]))
start= fp.process_cp(path)
