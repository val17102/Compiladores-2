grammar decaf;

fragment
DIGIT: [0-9];

fragment
LETTER: [a-zA-Z_];

NUM: DIGIT (DIGIT)* ;


ID: LETTER (LETTER|DIGIT)* ;
CHAR:'\'' LETTER '\'';
SPACES : [ \t\r\n\f]+  ->channel(HIDDEN);
LineComment:   '//' ~[\r\n]*-> skip;

program: 'class' 'Program' '{' (declaration)* '}' EOF;

declaration: structDeclaration | structInstance | varDeclaration | methodDeclaration;

varDeclaration: varType ID ';'  | varType ID '[' NUM ']' ';' ;

structDeclaration: 'struct' ID '{' (structChildren)* '}' ';';

structChildren: varDeclaration | structInstance;

structInstance: 'struct' ID ID ';' | 'struct' ID ID '[' NUM ']' ';' ;

varType: 'int' | 'char' | 'boolean' | 'void';

methodDeclaration: methodType ID '(' (parameter | parameter (',' parameter)*)?  ')' block ;

methodType: 'int' | 'char' | 'boolean' | 'void';

parameter: parameterType ID | parameterType ID '[' ']' | 'void';

parameterType: 'int' | 'char' | 'boolean';

block: '{' (varDeclaration | structDeclaration | structInstance)* (statement)* '}';

statement: 'if' '(' expression ')' block1 = block ('else' block2 = block)? #ifScope
        | 'while' '(' expression ')' block #whileScope
        | 'return' (expression)? ';'  #stm_return
        | methodCall ';' #stm_methodcall
        | block  #stm_block
        | left = location '=' right = expression  #stm_equal
        | (expression)? ';' #stm_expression; 

location: (ID | ID '[' expression ']' ) ('.' location)?;

expression: methodCall #expr_methodCall | location #expr_location  | literal #expr_literal
        | left = expression p_arith_op right = expression #expr_arith_op
        | left = expression arith_op right = expression #expr_op
        | left = expression rel_op right = expression #expr_rel_op
        | left = expression eq_op right = expression #expr_eq_op
        | left = expression cond_op right = expression #expr_cond_op
        | '-' expression #expr_minus
        | '!' expression #expr_not
        | '(' expression ')' #expr_par; 

methodCall: ID '(' (arg | arg (',' arg)*)?    ')';

arg: expression;
arith_op: '+' | '-' ;
p_arith_op: '*' | '/' | '%';

rel_op: '<' | '>' | '<=' | '>=';

eq_op: '==' | '!=';

cond_op: '&&' | '||';

literal: int_literal | char_literal | bool_literal;
int_literal: NUM;
char_literal: CHAR; 
bool_literal: 'true' | 'false';
