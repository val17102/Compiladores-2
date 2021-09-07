# Generated from decaf.g4 by ANTLR 4.9.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .decafParser import decafParser
else:
    from decafParser import decafParser

# This class defines a complete generic visitor for a parse tree produced by decafParser.

class decafVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by decafParser#program.
    def visitProgram(self, ctx:decafParser.ProgramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by decafParser#declaration.
    def visitDeclaration(self, ctx:decafParser.DeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by decafParser#varDeclaration.
    def visitVarDeclaration(self, ctx:decafParser.VarDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by decafParser#structDeclaration.
    def visitStructDeclaration(self, ctx:decafParser.StructDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by decafParser#structChildren.
    def visitStructChildren(self, ctx:decafParser.StructChildrenContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by decafParser#structInstance.
    def visitStructInstance(self, ctx:decafParser.StructInstanceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by decafParser#varType.
    def visitVarType(self, ctx:decafParser.VarTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by decafParser#methodDeclaration.
    def visitMethodDeclaration(self, ctx:decafParser.MethodDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by decafParser#methodType.
    def visitMethodType(self, ctx:decafParser.MethodTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by decafParser#parameter.
    def visitParameter(self, ctx:decafParser.ParameterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by decafParser#parameterType.
    def visitParameterType(self, ctx:decafParser.ParameterTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by decafParser#block.
    def visitBlock(self, ctx:decafParser.BlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by decafParser#ifScope.
    def visitIfScope(self, ctx:decafParser.IfScopeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by decafParser#whileScope.
    def visitWhileScope(self, ctx:decafParser.WhileScopeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by decafParser#stm_return.
    def visitStm_return(self, ctx:decafParser.Stm_returnContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by decafParser#stm_methodcall.
    def visitStm_methodcall(self, ctx:decafParser.Stm_methodcallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by decafParser#stm_block.
    def visitStm_block(self, ctx:decafParser.Stm_blockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by decafParser#stm_equal.
    def visitStm_equal(self, ctx:decafParser.Stm_equalContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by decafParser#stm_expression.
    def visitStm_expression(self, ctx:decafParser.Stm_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by decafParser#location.
    def visitLocation(self, ctx:decafParser.LocationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by decafParser#expr_cond_op.
    def visitExpr_cond_op(self, ctx:decafParser.Expr_cond_opContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by decafParser#expr_location.
    def visitExpr_location(self, ctx:decafParser.Expr_locationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by decafParser#expr_literal.
    def visitExpr_literal(self, ctx:decafParser.Expr_literalContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by decafParser#expr_op.
    def visitExpr_op(self, ctx:decafParser.Expr_opContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by decafParser#expr_eq_op.
    def visitExpr_eq_op(self, ctx:decafParser.Expr_eq_opContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by decafParser#expr_minus.
    def visitExpr_minus(self, ctx:decafParser.Expr_minusContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by decafParser#expr_par.
    def visitExpr_par(self, ctx:decafParser.Expr_parContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by decafParser#expr_arith_op.
    def visitExpr_arith_op(self, ctx:decafParser.Expr_arith_opContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by decafParser#expr_rel_op.
    def visitExpr_rel_op(self, ctx:decafParser.Expr_rel_opContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by decafParser#expr_methodCall.
    def visitExpr_methodCall(self, ctx:decafParser.Expr_methodCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by decafParser#expr_not.
    def visitExpr_not(self, ctx:decafParser.Expr_notContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by decafParser#methodCall.
    def visitMethodCall(self, ctx:decafParser.MethodCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by decafParser#arg.
    def visitArg(self, ctx:decafParser.ArgContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by decafParser#arith_op.
    def visitArith_op(self, ctx:decafParser.Arith_opContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by decafParser#p_arith_op.
    def visitP_arith_op(self, ctx:decafParser.P_arith_opContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by decafParser#rel_op.
    def visitRel_op(self, ctx:decafParser.Rel_opContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by decafParser#eq_op.
    def visitEq_op(self, ctx:decafParser.Eq_opContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by decafParser#cond_op.
    def visitCond_op(self, ctx:decafParser.Cond_opContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by decafParser#literal.
    def visitLiteral(self, ctx:decafParser.LiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by decafParser#int_literal.
    def visitInt_literal(self, ctx:decafParser.Int_literalContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by decafParser#char_literal.
    def visitChar_literal(self, ctx:decafParser.Char_literalContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by decafParser#bool_literal.
    def visitBool_literal(self, ctx:decafParser.Bool_literalContext):
        return self.visitChildren(ctx)



del decafParser