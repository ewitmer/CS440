from apriori import Apriori

test = {'T100':['M','O','N','K','E','Y'],
        'T200':['D','O','N','K','E','Y'],
        'T300':['M','A','K','E'],
        'T400':['M','U','C','K','Y'], 
        'T500':['C','O','O','K','I','E']}

a = Apriori(test, .6, .6)
all = a.generate_all_rules()
print(all)