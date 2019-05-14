class FPTree(object):
    """
    The FPTree class is used to grow the FP-Tree and retrieve frequent itemsets from a database.
    """

    def __init__(self, supportThreshold: int, order='frequency', conditionalTree: bool = False):
        """
        :param supportThreshold: minimum support that a itemset should have to be considered as frequent
        :param order: order to be used to construct the FP-Tree. Either "frequency" or "lexicographic"
        :param conditionalTree: if conditional Tree, transactions will be prefix
        """
        self.root = Node('{}', 0, None)
        self.supportThreshold = supportThreshold
        self.header = {}  # keys are items' names, values are lists of 2 elements: support, and first linked Node
        self.order = order
        self.lastItemsetNodes = {}
        self.database_path = None
        self.conditionalTree = conditionalTree

    def grow(self, database_path: str, itemSeparator=','):
        """
        Mine the database for frequent itemsets of size 1 and build the FP-Tree

        :param database_path: path to the database (txt or csv files)
        :param itemSeparator: separator used in your database to separate items from the same transaction
        :return: None. Use print() to display the built FP-Tree
        """
        self.database_path = database_path
        with open(self.database_path) as file:  # First pass
            for n, transaction in enumerate(file):
                transaction = set(transaction[:-1].split(itemSeparator))  # Creating a set to avoid counting multiple
                                                                            # times a duplicated item from a basket
                for itemset in transaction:
                    self.header[itemset] = self.header.get(itemset, 0) + 1
            self.root.update_frequency(n)
        for key, value in self.header.items():
            self.header[key] = [value]

        with open(self.database_path) as file:  # Second pass
            for transaction in file:
                transaction = list(set(transaction[:-1].split(itemSeparator)))
                self.new_transaction(transaction)

    def new_transaction(self, transaction: list, support: int = 1):
        """
        Add the given transaction to FP-Tree.
        In the case of a conditional FP-Tree, the transaction is actually a prefix.

        :param transaction: list of items from the transaction (/prefix in case of conditional FP-Tree)
        :param support: prefix's support (not used when passing a transaction)
        :return: None
        """
        if not self.conditionalTree:
            transaction = self.sort_transaction(transaction)

        self.root.grow_or_branch(transaction, self, support)

    def is_frequent(self, itemset: list, verbose: int = 0):
        """
        Check the frequency of a itemset

        :param itemset: Itemset you would like to test
        :param verbose: 0 ->> No comment; 1 ->> Decision is commented
        :return: bool: True if the itemset is frequent, False otherwise
        """
        for item in itemset:
            support = self.header.get(item, [-1])[0]
            if support < self.supportThreshold:
                if verbose > 0:
                    if support == -1:
                        print('Item {} has not been found in the database'.format(item))
                    else:
                        print(
                            'Item {} has a support of {} which is '
                            'below the SupportThreshold: {}'.format(item, support, self.supportThreshold))
                return False
        else:
            sorted_itemset = self.sort_transaction(itemset)
            sorted_itemset.reverse()
            support = self.header[sorted_itemset[0]][1].check_frequent(sorted_itemset,
                                                                       sorted_itemset.copy(),
                                                                       self.header[sorted_itemset[0]][1])
            if verbose > 0:
                print('Support of {} is {}'.format(itemset, support))
            return False if support < self.supportThreshold else True

    def mine_frequent_itemsets(self, item: str, buildCondFPTree: bool = True):
        try:
            startingNode = self.header.get(item, [None, None])[1]
        except IndexError:
            print('This item is not frequent')
        else:
            assert startingNode is not None, 'This item is not in your database'
            conditionalPatternPrefixes = startingNode.collect_prefix({}, [], startingNode)
            if buildCondFPTree:
                conditionalFPTree = FPTree(self.supportThreshold, self.order, True)
                for prefix, support in conditionalPatternPrefixes.items():
                    for item in prefix:
                        conditionalFPTree.header[item] = conditionalFPTree.header.get(item, 0) + support
                for key, value in conditionalFPTree.header.items():
                    conditionalFPTree.header[key] = [value]

                for prefix, support in conditionalPatternPrefixes.items():
                    if support >= self.supportThreshold:
                        conditionalFPTree.new_transaction(list(prefix), support)
                print('Conditional FP-Tree for item {}:'.format(item))
                conditionalFPTree.show()
            else:
                print('Prefixes for item {}:'.format(item))
                print(conditionalPatternPrefixes)

    def sort_transaction(self, transaction: list):
        """
        Sort the transaction according to the predefined order

        :param transaction: list of items to be sorted
        :return: a sorted transaction
        """
        if self.order == 'frequency':
            transaction.sort(key=lambda itemset: self.header[itemset][0], reverse=True)  # Sort the transaction by item's support
        elif self.order == 'lexicographic':
            transaction.sort()  # Sort the transaction alphabetically
        return transaction

    def show(self):
        """
        Display the FP-Tree
        """
        self.root.show(indentation=0)
        return ''

    def get_header(self):
        """
        Display the header
        """
        for key, value in self.header.items():
            if len(value) > 1:
                print('Item {}: Freq = {}, linked to Node id > {}'.format(key, value[0], value[1].id))
            else:
                print('Item {}: Freq = {}'.format(key, *value))


class Node(object):
    """
    Internal class used to build the FP-Tree
    """
    guid = 0

    def __init__(self, name: str, count: int, parentNode: object):
        """
        :param name: name given to the node, based on the item
        :param count: number of times this node has been reached when growing the FP-Tree
        :param parentNode: node from which the current node has descended
        """
        self.name = name
        self.frequency = count
        self.parent = parentNode
        self.nodeLink = None
        self.children = []
        self.id = Node.guid
        Node.guid += 1

    def grow_or_branch(self, transaction: list, Tree: object, support: int = 1):
        """
        Either an existing branch of the FP-Tree is reused or a new branch is created

        :param transaction: items from the transaction/prefix that still need to be
         included in the (conditional) FP-Tree
        :param Tree: used to pass some attributes from the main class
        :param support: used to update the frequency of a node
        :return: None
        """
        if not transaction:  # Base case for the recursion
            return None

        if not Tree.conditionalTree:
            if Tree.order == 'frequency'\
                    and Tree.header[transaction[0]][0] < Tree.supportThreshold:  # Discard unfrequent itemsets
                return None
            elif Tree.header[transaction[0]][0] < Tree.supportThreshold:
                del transaction[0]
                return self.grow_or_branch(transaction, Tree, support)

        for child in self.children:  # Grow
            if child.name == transaction[0]:
                child.update_frequency(support)
                del transaction[0]
                child.grow_or_branch(transaction, Tree, support)
                break
        else:  # Branch
            self.children.append(Node(transaction[0], support, self))
            if transaction[0] in Tree.lastItemsetNodes:
                self.update_nodeLink(Tree.lastItemsetNodes[transaction[0]],
                                     self.children[-1])  # Maintaining the nodeLink
            else:
                Tree.header[transaction[0]].append(self.children[-1])  # Maintaining the header
            Tree.lastItemsetNodes[transaction[0]] = self.children[-1]
            del transaction[0]
            self.children[-1].grow_or_branch(transaction, Tree, support)

    def collect_prefix(self, prefixDict: dict, placeholderPrefix: list, sourceNode: object):
        """
        Gradually collect in prefixDict the prefixes for a specific item, via a double recursion.
        Method used by conditional FP-Trees.

        :param prefixDict: accumulator storing as keys the prefixes and as values their corresponding support
        :param placeholderPrefix: accumulator containing items seen while ascending the conditional FP-Tree
        :param sourceNode: Node from which the next recursion should start
        :return: prefixDict
        """
        if self.parent is None:  # Root Node
            prefix = tuple(placeholderPrefix[1:][::-1])
            prefixDict[prefix] = sourceNode.frequency
            if sourceNode.nodeLink is None:
                return prefixDict
            else:
                return sourceNode.nodeLink.collect_prefix(prefixDict, [], sourceNode.nodeLink)
        else:
            placeholderPrefix.append(self.name)
            return self.parent.collect_prefix(prefixDict, placeholderPrefix, sourceNode)

    def update_frequency(self, count: int = 1):
        """
        Increment the frequency of the node/pattern. Note that this is not equivalent to
        the frequency/support of the itemset.

        :param count: amount by which the frequency of the node needs to be increased. Usually 1, except
         for conditional FP-Trees
        :return: None
        """
        self.frequency += count

    def update_nodeLink(self, other: object, nodeLink: object):
        """
        Update the nodeLink attribute of 'other' node

        :param other: node for which we need to update the attribute "nodeLink"
        :param nodeLink: node that should be linked
        :return: None
        """
        other.nodeLink = nodeLink

    def check_frequent(self, itemset: list, remainingItems: list, sourceNode: object):
        """
        Double recursions:
            1) through one branch of the tree
            2) through linked nodes of sourceNode
        """
        if not remainingItems:
            if sourceNode.nodeLink is None:
                return sourceNode.frequency  # Base case for second recursion
            else:
                return sourceNode.frequency + sourceNode.nodeLink.check_frequent(itemset, itemset.copy(), sourceNode.nodeLink)  # Base case for first recrusion and call towards second recursion
        elif self.parent is None:  # Root Node
            if sourceNode.nodeLink is None:
                return 0  # Base case for second recursion
            else:
                return sourceNode.nodeLink.check_frequent(itemset, itemset.copy(), sourceNode.nodeLink)  # Base case for first recursion and call towards second recursion

        elif self.name == remainingItems[0]:
            del remainingItems[0]

        return self.parent.check_frequent(itemset, remainingItems, sourceNode)  # Call towards first recursion

    def show(self, indentation=1):
        if self.nodeLink is not None:
            print('--> Itemset:', self.name, '(ID:', self.id, 'Link:', self.nodeLink.id, '), freq:', self.frequency)
        else:
            print('--> Itemset:', self.name, '(ID:', self.id, '), freq:', self.frequency)
        for child in self.children:
            print(' ' * indentation, '|', end='')
            child.show(indentation + 1)
        return ''
