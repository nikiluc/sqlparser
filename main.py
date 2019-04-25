import sys
from antlr4 import *
from antlr4.tree.Tree import TerminalNodeImpl
from SQLiteLexer import SQLiteLexer
from SQLiteParser import SQLiteParser
from SQLiteListener import SQLiteListener



def main(argv):
    while True:

        y = input()

        if y == 'x':
            break
        else:
            input_val = InputStream(y)
            lexer = SQLiteLexer(input_val)
            stream = CommonTokenStream(lexer)
            parser = SQLiteParser(stream)
            tree = parser.sql_stmt_list()
            #parsertree = parser.parse()
            #print(parsertree)
        #print(parser.ruleNames)
        #print(tree.toStringTree())

            traverse(tree, parser.ruleNames)
        #printer = SQLiteListener()
        #walker = ParseTreeWalker()
        #walker.walk(printer, tree)



def traverse(tree, rule_names, indent = 0):
    if tree.getText() == "<EOF>":
        return
    elif isinstance(tree, TerminalNodeImpl):
        print("{0}TOKEN='{1}'".format(" " * indent, tree.getText()))

    else:
        print("{0}{1}".format("  " * indent, rule_names[tree.getRuleIndex()]))



        for child in tree.children:
            traverse(child, rule_names, indent + 1)


if __name__ == '__main__':
    main(sys.argv)