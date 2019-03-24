from apriori import Apriori
from fpgrowth import FPTree, FPNode

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

test = {'T100':['Mood','Only','N','Kale','Ear','Yes'],
        'T200':['D','Only','N','Kale','Ear','Yes'],
        'T300':['Mood','A','Kale','Ear'],
        'T400':['Mood','U','C','Kale','Yes'], 
        'T500':['C','Only','Only','Kale','I','Ear']}

a = Apriori(test, 2, .8)
fp = FPTree(test, 2, .8)
all_a = a.generate_all_rules()
all_fp = fp.generate_all_rules()

print("Asserts both algorithms generate the same rule set: ",test_algos(all_a, all_fp))


