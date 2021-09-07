# Generated from decaf.g4 by ANTLR 4.9.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .decafParser import decafParser
else:
    from decafParser import decafParser

# This class defines a complete listener for a parse tree produced by decafParser.
class decafListener(ParseTreeListener):

    # Enter a parse tree produced by decafParser#program.
    def enterProgram(self, ctx:decafParser.ProgramContext):
        pass

    # Exit a parse tree produced by decafParser#program.
    def exitProgram(self, ctx:decafParser.ProgramContext):
        pass


    # Enter a parse tree produced by decafParser#declaration.
    def enterDeclaration(self, ctx:decafParser.DeclarationContext):
        pass

    # Exit a parse tree produced by decafParser#declaration.
    def exitDeclaration(self, ctx:decafParser.DeclarationContext):
        pass


    # Enter a parse tree produced by decafParser#varDeclaration.
    def enterVarDeclaration(self, ctx:decafParser.VarDeclarationContext):
        pass

    # Exit a parse tree produced by decafParser#varDeclaration.
    def exitVarDeclaration(self, ctx:decafParser.VarDeclarationContext):
        pass


    # Enter a parse tree produced by decafParser#structDeclaration.
    def enterStructDeclaration(self, ctx:decafParser.StructDeclarationContext):
        pass

    # Exit a parse tree produced by decafParser#structDeclaration.
    def exitStructDeclaration(self, ctx:decafParser.StructDeclarationContext):
        pass


    # Enter a parse tree produced by decafParser#structChildren.
    def enterStructChildren(self, ctx:decafParser.StructChildrenContext):
        pass

    # Exit a parse tree produced by decafParser#structChildren.
    def exitStructChildren(self, ctx:decafParser.StructChildrenContext):
        pass


    # Enter a parse tree produced by decafParser#structInstance.
    def enterStructInstance(self, ctx:decafParser.StructInstanceContext):
        pass

    # Exit a parse tree produced by decafParser#structInstance.
    def exitStructInstance(self, ctx:decafParser.StructInstanceContext):
        pass


    # Enter a parse tree produced by decafParser#varType.
    def enterVarType(self, ctx:decafParser.VarTypeContext):
        pass

    # Exit a parse tree produced by decafParser#varType.
    def exitVarType(self, ctx:decafParser.VarTypeContext):
        pass


    # Enter a parse tree produced by decafParser#methodDeclaration.
    def enterMethodDeclaration(self, ctx:decafParser.MethodDeclarationContext):
        pass

    # Exit a parse tree produced by decafParser#methodDeclaration.
    def exitMethodDeclaration(self, ctx:decafParser.MethodDeclarationContext):
        pass


    # Enter a parse tree produced by decafParser#methodType.
    def enterMethodType(self, ctx:decafParser.MethodTypeContext):
        pass

    # Exit a parse tree produced by decafParser#methodType.
    def exitMethodType(self, ctx:decafParser.MethodTypeContext):
        pass


    # Enter a parse tree produced by decafParser#parameter.
    def enterParameter(self, ctx:decafParser.ParameterContext):
        pass

    # Exit a parse tree produced by decafParser#parameter.
    def exitParameter(self, ctx:decafParser.ParameterContext):
        pass


    # Enter a parse tree produced by decafParser#parameterType.
    def enterParameterType(self, ctx:decafParser.ParameterTypeContext):
        pass

    # Exit a parse tree produced by decafParser#parameterType.
    def exitParameterType(self, ctx:decafParser.ParameterTypeContext):
        pass


    # Enter a parse tree produced by decafParser#block.
    def enterBlock(self, ctx:decafParser.BlockContext):
        pass

    # Exit a parse tree produced by decafParser#block.
    def exitBlock(self, ctx:decafParser.BlockContext):
        pass


    # Enter a parse tree produced by decafParser#ifScope.
    def enterIfScope(self, ctx:decafParser.IfScopeContext):
        pass

    # Exit a parse tree produced by decafParser#ifScope.
    def exitIfScope(self, ctx:decafParser.IfScopeContext):
        pass


    # Enter a parse tree produced by decafParser#whileScope.
    def enterWhileScope(self, ctx:decafParser.WhileScopeContext):
        pass

    # Exit a parse tree produced by decafParser#whileScope.
    def exitWhileScope(self, ctx:decafParser.WhileScopeContext):
        pass


    # Enter a parse tree produced by decafParser#stm_return.
    def enterStm_return(self, ctx:decafParser.Stm_returnContext):
        pass

    # Exit a parse tree produced by decafParser#stm_return.
    def exitStm_return(self, ctx:decafParser.Stm_returnContext):
        pass


    # Enter a parse tree produced by decafParser#stm_methodcall.
    def enterStm_methodcall(self, ctx:decafParser.Stm_methodcallContext):
        pass

    # Exit a parse tree produced by decafParser#stm_methodcall.
    def exitStm_methodcall(self, ctx:decafParser.Stm_methodcallContext):
        pass


    # Enter a parse tree produced by decafParser#stm_block.
    def enterStm_block(self, ctx:decafParser.Stm_blockContext):
        pass

    # Exit a parse tree produced by decafParser#stm_block.
    def exitStm_block(self, ctx:decafParser.Stm_blockContext):
        pass


    # Enter a parse tree produced by decafParser#stm_equal.
    def enterStm_equal(self, ctx:decafParser.Stm_equalContext):
        pass

    # Exit a parse tree produced by decafParser#stm_equal.
    def exitStm_equal(self, ctx:decafParser.Stm_equalContext):
        pass


    # Enter a parse tree produced by decafParser#stm_expression.
    def enterStm_expression(self, ctx:decafParser.Stm_expressionContext):
        pass

    # Exit a parse tree produced by decafParser#stm_expression.
    def exitStm_expression(self, ctx:decafParser.Stm_expressionContext):
        pass


    # Enter a parse tree produced by decafParser#location.
    def enterLocation(self, ctx:decafParser.LocationContext):
        pass

    # Exit a parse tree produced by decafParser#location.
    def exitLocation(self, ctx:decafParser.LocationContext):
        pass


    # Enter a parse tree produced by decafParser#expr_cond_op.
    def enterExpr_cond_op(self, ctx:decafParser.Expr_cond_opContext):
        pass

    # Exit a parse tree produced by decafParser#expr_cond_op.
    def exitExpr_cond_op(self, ctx:decafParser.Expr_cond_opContext):
        pass


    # Enter a parse tree produced by decafParser#expr_location.
    def enterExpr_location(self, ctx:decafParser.Expr_locationContext):
        pass

    # Exit a parse tree produced by decafParser#expr_location.
    def exitExpr_location(self, ctx:decafParser.Expr_locationContext):
        pass


    # Enter a parse tree produced by decafParser#expr_literal.
    def enterExpr_literal(self, ctx:decafParser.Expr_literalContext):
        pass

    # Exit a parse tree produced by decafParser#expr_literal.
    def exitExpr_literal(self, ctx:decafParser.Expr_literalContext):
        pass


    # Enter a parse tree produced by decafParser#expr_op.
    def enterExpr_op(self, ctx:decafParser.Expr_opContext):
        pass

    # Exit a parse tree produced by decafParser#expr_op.
    def exitExpr_op(self, ctx:decafParser.Expr_opContext):
        pass


    # Enter a parse tree produced by decafParser#expr_eq_op.
    def enterExpr_eq_op(self, ctx:decafParser.Expr_eq_opContext):
        pass

    # Exit a parse tree produced by decafParser#expr_eq_op.
    def exitExpr_eq_op(self, ctx:decafParser.Expr_eq_opContext):
        pass


    # Enter a parse tree produced by decafParser#expr_minus.
    def enterExpr_minus(self, ctx:decafParser.Expr_minusContext):
        pass

    # Exit a parse tree produced by decafParser#expr_minus.
    def exitExpr_minus(self, ctx:decafParser.Expr_minusContext):
        pass


    # Enter a parse tree produced by decafParser#expr_par.
    def enterExpr_par(self, ctx:decafParser.Expr_parContext):
        pass

    # Exit a parse tree produced by decafParser#expr_par.
    def exitExpr_par(self, ctx:decafParser.Expr_parContext):
        pass


    # Enter a parse tree produced by decafParser#expr_arith_op.
    def enterExpr_arith_op(self, ctx:decafParser.Expr_arith_opContext):
        pass

    # Exit a parse tree produced by decafParser#expr_arith_op.
    def exitExpr_arith_op(self, ctx:decafParser.Expr_arith_opContext):
        pass


    # Enter a parse tree produced by decafParser#expr_rel_op.
    def enterExpr_rel_op(self, ctx:decafParser.Expr_rel_opContext):
        pass

    # Exit a parse tree produced by decafParser#expr_rel_op.
    def exitExpr_rel_op(self, ctx:decafParser.Expr_rel_opContext):
        pass


    # Enter a parse tree produced by decafParser#expr_methodCall.
    def enterExpr_methodCall(self, ctx:decafParser.Expr_methodCallContext):
        pass

    # Exit a parse tree produced by decafParser#expr_methodCall.
    def exitExpr_methodCall(self, ctx:decafParser.Expr_methodCallContext):
        pass


    # Enter a parse tree produced by decafParser#expr_not.
    def enterExpr_not(self, ctx:decafParser.Expr_notContext):
        pass

    # Exit a parse tree produced by decafParser#expr_not.
    def exitExpr_not(self, ctx:decafParser.Expr_notContext):
        pass


    # Enter a parse tree produced by decafParser#methodCall.
    def enterMethodCall(self, ctx:decafParser.MethodCallContext):
        pass

    # Exit a parse tree produced by decafParser#methodCall.
    def exitMethodCall(self, ctx:decafParser.MethodCallContext):
        pass


    # Enter a parse tree produced by decafParser#arg.
    def enterArg(self, ctx:decafParser.ArgContext):
        pass

    # Exit a parse tree produced by decafParser#arg.
    def exitArg(self, ctx:decafParser.ArgContext):
        pass


    # Enter a parse tree produced by decafParser#arith_op.
    def enterArith_op(self, ctx:decafParser.Arith_opContext):
        pass

    # Exit a parse tree produced by decafParser#arith_op.
    def exitArith_op(self, ctx:decafParser.Arith_opContext):
        pass


    # Enter a parse tree produced by decafParser#p_arith_op.
    def enterP_arith_op(self, ctx:decafParser.P_arith_opContext):
        pass

    # Exit a parse tree produced by decafParser#p_arith_op.
    def exitP_arith_op(self, ctx:decafParser.P_arith_opContext):
        pass


    # Enter a parse tree produced by decafParser#rel_op.
    def enterRel_op(self, ctx:decafParser.Rel_opContext):
        pass

    # Exit a parse tree produced by decafParser#rel_op.
    def exitRel_op(self, ctx:decafParser.Rel_opContext):
        pass


    # Enter a parse tree produced by decafParser#eq_op.
    def enterEq_op(self, ctx:decafParser.Eq_opContext):
        pass

    # Exit a parse tree produced by decafParser#eq_op.
    def exitEq_op(self, ctx:decafParser.Eq_opContext):
        pass


    # Enter a parse tree produced by decafParser#cond_op.
    def enterCond_op(self, ctx:decafParser.Cond_opContext):
        pass

    # Exit a parse tree produced by decafParser#cond_op.
    def exitCond_op(self, ctx:decafParser.Cond_opContext):
        pass


    # Enter a parse tree produced by decafParser#literal.
    def enterLiteral(self, ctx:decafParser.LiteralContext):
        pass

    # Exit a parse tree produced by decafParser#literal.
    def exitLiteral(self, ctx:decafParser.LiteralContext):
        pass


    # Enter a parse tree produced by decafParser#int_literal.
    def enterInt_literal(self, ctx:decafParser.Int_literalContext):
        pass

    # Exit a parse tree produced by decafParser#int_literal.
    def exitInt_literal(self, ctx:decafParser.Int_literalContext):
        pass


    # Enter a parse tree produced by decafParser#char_literal.
    def enterChar_literal(self, ctx:decafParser.Char_literalContext):
        pass

    # Exit a parse tree produced by decafParser#char_literal.
    def exitChar_literal(self, ctx:decafParser.Char_literalContext):
        pass


    # Enter a parse tree produced by decafParser#bool_literal.
    def enterBool_literal(self, ctx:decafParser.Bool_literalContext):
        pass

    # Exit a parse tree produced by decafParser#bool_literal.
    def exitBool_literal(self, ctx:decafParser.Bool_literalContext):
        pass



del decafParser