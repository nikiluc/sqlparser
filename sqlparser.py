
#
# simple demo of using the parsing library to do simple-minded SQL parsing
# could be extended to include where clauses etc.
#
#
#
from pyparsing import Word, delimitedList, Optional, \
    Group, alphas, alphanums, punc8bit, Forward, oneOf, quotedString, \
    infixNotation, opAssoc, \
    ZeroOrMore, restOfLine, CaselessKeyword, pyparsing_common as ppc

# define SQL tokens
selectStmt = Forward()
insertStmt = Forward()
CREATE, TABLE, INSERT, DELETE,\
DROP, INDEX, INTO, VALUES, SELECT,\
FROM, WHERE, AND, OR, IN, IS, NOT,\
NULL, DEFAULT, TRUE, FALSE, UPDATE,\
    AS, SET, ON, GROUP, ORDER = map(CaselessKeyword,
    "create table insert delete drop index into values select from where"
    " and or in is not null default true false update as set on group order".split())
NOT_NULL = NOT + NULL

ident          = Word(alphas, alphanums + "_$" ).setName("identifier")
columnName     = delimitedList(ident, ".", combine=True).setName("column name")
columnName.addParseAction(ppc.upcaseTokens)
columnNameList = Group( delimitedList(columnName))
tableName      = delimitedList(ident, ".", combine=True).setName("table name")
tableName.addParseAction(ppc.upcaseTokens)
tableNameList  = Group(delimitedList(tableName))

keywords = DEFAULT | NULL | TRUE | FALSE

binop = oneOf("= != < > >= <= eq ne lt le gt ge", caseless=True)
realNum = ppc.real()
intNum = ppc.signed_integer()

columnRval = realNum | intNum | quotedString | columnName | keywords# need to add support for alg expressions
ins_values = Group(delimitedList(columnRval))

whereCondition = Group(
    ( columnName + binop + columnRval ) |
    ( columnName + IN + Group("(" + delimitedList( columnRval ) + ")" )) |
    ( columnName + IN + Group("(" + selectStmt + ")" )) |
    ( columnName + IS + (NULL | NOT_NULL))
    )

whereExpression = infixNotation(whereCondition,
    [
        (NOT, 1, opAssoc.RIGHT),
        (AND, 2, opAssoc.LEFT),
        (OR, 2, opAssoc.LEFT),
    ])

# define the grammar
selectStmt <<= (SELECT + ('*' | columnNameList)("columns") +
                FROM + tableNameList( "tables" ) +
                Optional(Group(WHERE + whereExpression), "")("where"))

insertStmt <<= (INSERT + INTO + tableNameList("table") \
              + Optional("(" + columnNameList("columns") + ")") \
              + VALUES + "(" + ins_values.setResultsName("vals") + ")" + ';')

simpleSQL = insertStmt

# define Oracle comment format, and ignore them
oracleSqlComment = "--" + restOfLine
simpleSQL.ignore( oracleSqlComment )

if __name__ == "__main__":
    simpleSQL.runTests("""\

        # multiple tables
        SELECT * from XYZZY, ABC

        INSERT INTO personnel (hometown, firstname, beststate) values (city, name, state);

        # dotted table name
        select * from SYS.XYZZY

        Select A from Sys.dual

        Select A,B,C from Sys.dual

        Select A, B, C from Sys.dual, Table2

        # FAIL - invalid SELECT keyword
        Xelect A, B, C from Sys.dual

        # FAIL - invalid FROM keyword
        Select A, B, C frox Sys.dual

        # FAIL - incomplete statement
        Select

        # FAIL - incomplete statement
        Select * from

        # FAIL - invalid column
        Select &&& frox Sys.dual

        # where clause
        Select A from Sys.dual where a in ('RED','GREEN','BLUE')

        # compound where clause
        Select A from Sys.dual where a in ('RED','GREEN','BLUE') and b in (10,20,30)

        # where clause with comparison operator
        Select A,b from table1,table2 where table1.id eq table2.id
        """)
