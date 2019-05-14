# DM - Frequent Pattern Trees
Implementation of the FP-Growth algorithm for mining frequent itemsets in a database of transactions. This algorithm has been presented in 2000 by Han J. et al..

## Usage
Use the class `FPTree` to instantiate a new FP-Tree. One mandatory argument needs to be passed, the _support threshold_. Another optional argument can be passed _order_ to specify the order that will be used to build the FP-Tree. Two options are supported: _frequency_, or _lexicographic_.
```python
>>>fptree = FPTree(supportThreshold = 2, order = 'frequency')
```

To grow your FP-Tree, you need to reference the path to your database in the `grow()` method. Note that in the _dataset_ folder you can find two toy databases that you can use to familiarize yourself.
```python
>>>fptree.grow(database_path = 'dataset\Store_Transactions_db.txt')
```

Once your FP-Tree is fully grown, you can easily visualize it with the `show()` method:
```python
>>>fptree.show()
```
```
--> Itemset: {} (ID: 0 ), freq: 9
 |--> Itemset: Bread (ID: 1 Link: 7 ), freq: 2
  |--> Itemset: Apple (ID: 2 ), freq: 2
 |--> Itemset: Water (ID: 3 ), freq: 7
  |--> Itemset: Beer (ID: 4 Link: 11 ), freq: 5
   |--> Itemset: Book (ID: 5 ), freq: 4
    |--> Itemset: Soda (ID: 6 Link: 8 ), freq: 2
    |--> Itemset: Pizza (ID: 13 ), freq: 1
   |--> Itemset: Bread (ID: 7 Link: 12 ), freq: 1
  |--> Itemset: Soda (ID: 8 ), freq: 2
   |--> Itemset: Pizza (ID: 9 Link: 13 ), freq: 2
    |--> Itemset: Diaper (ID: 10 ), freq: 2
 |--> Itemset: Beer (ID: 11 ), freq: 1
  |--> Itemset: Bread (ID: 12 ), freq: 1
```
The _ID_ of the Itemset is useful for debugging. The _Link_ points to the _ID_ of the next same Itemset in the FP-Tree. The _freq_ is the frequency of the Itemset. Note that this is not the same as the support of the item. In the example above,
a frequency of 5 for Itemset Beer with ID=4 means that the support of this branch of the tree up to this node is 5. Hence the support of [Water, Beer] is 5.

You can also use the method `get_header()` to visualize the header of your FP-Tree. The header is used internally to build the tree. It is a dictionnary where its keys are keys are items' names and its values are lists of 2 elements: support, and first linked Node.
```python
>>>fptree.get_header()
```
```
Item Bread: Freq = 4, linked to Node id > 1
Item Apple: Freq = 2, linked to Node id > 2
Item Banana: Freq = 1
Item Book: Freq = 4, linked to Node id > 5
Item Beer: Freq = 6, linked to Node id > 4
Item Water: Freq = 7, linked to Node id > 3
Item Soda: Freq = 4, linked to Node id > 6
Item Pizza: Freq = 3, linked to Node id > 9
Item Diaper: Freq = 2, linked to Node id > 10
Item Cherry: Freq = 1
```

To check if a specific itemset is frequent, you can use the `is_frequent()` method which takes a list of items (which is interpreted as a itemset) and returns _True_ if this itemset has a support greater or equal to the _support threshold_, and _False_ otherwise.
```python
>>>fptree.is_frequent(['Soda', 'Beer'])
```
```
True
```
```python
>>>fptree.is_frequent(['Soda', 'Diaper', 'Pizza'], verbose = 1)
```
```
Support of ['Diaper', 'Pizza', 'Soda'] is 2
True
```
```python
>>>fptree.is_frequent(['Banana'], verbose = 1)
```
```
Item Banana has a support of 1 which is below the SupportThreshold: 2
False
```

To build a conditional FP-Tree, use the method `mine_frequent_itemsets` and pass the corresponding item as the first argument. The second argument is a boolean. _True_ if you want this method to return the conditional FP-Tree of that item; _False_ if you just want to see the prefixes of that item and the corresponding support.
```python
>>>fptree.mine_frequent_itemsets(cond_item = 'Soda', buildCondFPTree = True)
```
```
Conditional FP-Tree for item Soda:
--> Itemset: {} (ID: 14 ), freq: 0
 |--> Itemset: Water (ID: 15 ), freq: 4
  |--> Itemset: Beer (ID: 16 ), freq: 2
   |--> Itemset: Book (ID: 17 ), freq: 2
```
```python
>>>fptree.mine_frequent_itemsets(cond_item = 'Soda', , buildCondFPTree = False)
```
```
Prefixes for item Soda:
{('Water', 'Beer'): 2, ('Water',): 2}
```

## Requirements:
- Python 3.x

## Source:
__[Han J. et al.'s Original Paper: Mining Frequent Patterns without Candidate Generation](https://www.cs.sfu.ca/~jpei/publications/sigmod00.pdf)__
