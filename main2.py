from os import name
from tkinter.constants import END, INSERT
from typing import Literal
from decafListener import decafListener
import sys
from numpy import *
from antlr4 import *
from decafLexer import decafLexer
from decafParser import decafParser
from decafVisitor import decafVisitor
import typeSystem as sisTypes
import tkinter as tk
from tkinter import filedialog as fd

DEFAULT_TYPES = {
    'int': 4,
    'boolean': 1,
    'char': 1,
}

currentScope = 0
lastScope = 0
currentStruct = 0
scopeStack = []
operationStack = []

table = sisTypes.typeTable()
window = tk.Tk()
text = tk.Text(window)
text2 = tk.Text(window)
text3 = tk.Text(window)
text4 = tk.Text(window)

class decVisitor(decafVisitor):

    def visitProgram(self, ctx: decafParser.ProgramContext):
        table.addScope(currentScope, None, "global")
        self.visitChildren(ctx)
    
    def visitMethodDeclaration(self, ctx: decafParser.MethodDeclarationContext):
        global currentScope, lastScope
        scopeName = ctx.ID().getText()
        methodType = ctx.methodType().getText()
        parameters = ctx.parameter()
        currentScope += 1
        if (not table.getScope(scopeName)):
            table.addScope(currentScope, methodType, scopeName)
            parametersN = []
            if (parameters != None):
                if (len(parameters) > 0):
                    temp = parameters[0].getText()
                    if (temp != 'void'):
                        for i in parameters:
                            paramName = i.ID().getText()
                            paramType = i.parameterType().getText()
                            tempArray = None
                            if ("[" in i.getText() and "]" in i.getText()):
                                tempArray = 0
                            if (paramName not in parametersN):
                                table.addVariable(paramType, paramName, currentScope, DEFAULT_TYPES[paramType], tempArray)
                                table.addScopeParams(currentScope, paramType)
                                parametersN.append(paramName)
                    
        return self.visitChildren(ctx)
    
        

    def visitVarDeclaration(self, ctx: decafParser.VarDeclarationContext, structParent = None):
        varId = ctx.ID().getText()
        varType = ctx.varType().getText()
        tempArray = None
        if (ctx.NUM() != None):
            tempArray = int(ctx.NUM().getText())
        if (structParent != None):
            if (not table.checkAttributeExists(varId, structParent)):
                if tempArray != None:
                    tempSize = DEFAULT_TYPES[varType] * tempArray
                else:
                    tempSize = DEFAULT_TYPES[varType]
                table.addStructAttribute(varType, varId, tempSize, structParent, tempArray)
        elif (not table.getVariableExists(varId, currentScope)):
            if tempArray != None:
                tempSize = DEFAULT_TYPES[varType] * tempArray
            else:
                tempSize = DEFAULT_TYPES[varType]
            table.addVariable(varType, varId, currentScope, tempSize, tempArray)
        return self.visitChildren(ctx)

    def visitStructDeclaration(self, ctx: decafParser.StructDeclarationContext):
        global currentStruct, currentScope
        structId = ctx.ID().getText()
        vars = ctx.structChildren()
        flag = table.checkStructUniqueInScope(currentScope, structId)
        if (not flag):
            currentStruct += 1
            table.addStruct(currentStruct, structId, currentScope)
            for i in vars:
                if (i.structInstance() != None):
                    temp = i.structInstance()
                    self.visitStructInstance(temp, currentStruct)
                    print("instance struct ", temp)
                elif (i.varDeclaration() != None):
                    temp = i.varDeclaration()
                    self.visitVarDeclaration(temp, currentStruct)
                    print("declaracion var ", temp)

                #vName = i.ID().getText()

    def visitStructInstance(self, ctx: decafParser.StructInstanceContext, structParent = None):
        instanceParent = ctx.ID()[0].getText()
        instanceId = ctx.ID()[1].getText()
        tempArray = None
        if (table.checkStructExist(instanceParent)):
            if (ctx.NUM() != None):
                    tempArray = int(ctx.NUM().getText())
            if (structParent != None):
                table.addStructAttribute("struct "+instanceParent, instanceId, None, structParent, tempArray)
            else:
                table.addVariable("struct "+instanceParent, instanceId, currentScope, None, tempArray)

class asiVisitor(decafVisitor):    
    def visitProgram(self, ctx: decafParser.ProgramContext):
        global scopeStack
        scopeStack.append(0)
        return self.visitChildren(ctx)

    def visitMethodDeclaration(self, ctx: decafParser.MethodDeclarationContext):
        global scopeStack
        scopeName = ctx.ID().getText()
        scopeId = table.getScopeId(scopeName)
        scopeStack.append(scopeId)
        scopeVariables = table.getScopeVariables(scopeStack[-1])
        print(scopeName, " cantidad de scopes en stack ", scopeStack)
        table.addGeneratedCode("Def "+scopeName+":")
        params = table.getScopeParams(scopeId)
        for i in range(len(params)):
            table.addGeneratedCode("tv["+str(scopeVariables[i]["address"])+"] = ParamPop "+str(DEFAULT_TYPES[params[i]]))
        self.visitChildren(ctx)
        if (len(scopeStack) > 0):
            scopeStack.pop()
        table.addGeneratedCode("End "+scopeName+"\n")

    def visitLocation(self, ctx: decafParser.LocationContext, structParent = None):
        tempStack = scopeStack.copy()
        name = ctx.ID().getText()
        found = False
        if (ctx.location() != None and structParent == None):
            print("Se encontro ",ctx.getText())
            while (len(tempStack) > 0):
                check = table.getVariableExists(name, tempStack[-1])
                if (check):
                    tempType = table.checkVariableType(name, tempStack[-1])
                    structName = tempType.split("struct ")[1]
                    return self.visitLocation(ctx.location(), structName)
                else:
                    tempStack.pop()
        elif (ctx.location() != None and structParent != None):
            tempStruct = self.searchStruct(structParent)
            if (tempStruct != None):
                if (table.checkAttributeExists(name, tempStruct["structId"])):
                    tempAttribute = table.getStructAttribute(name, tempStruct["structId"])
                    structName = tempAttribute["dataType"].split("struct ")[1]
                    return self.visitLocation(ctx.location(), structName)
        elif (structParent != None):
            print("searching for struct ",structParent)
            tempStruct = self.searchStruct(structParent)
            if (tempStruct != None):
                if (table.checkAttributeExists(name, tempStruct["structId"])):
                    tempAttribute = table.getStructAttribute(name, tempStruct["structId"])
                    return tempAttribute["dataType"]
        else:
            while (len(tempStack) > 0):
                check = table.getVariableExists(name, tempStack[-1])
                if (check):
                    tempType = table.checkVariableType(name, tempStack[-1])
                    if (ctx.expression() != None):
                        tempPos = self.visit(ctx.expression())
                        if (tempPos["value"] != None):
                            table.addGeneratedCode(tempPos["address"]+" = "+str(tempPos["value"]))

                        table.addGeneratedCode("oli"+str(tempPos))
                    tempAddress = table.getVariableAddress(name, tempStack[-1])
                    tempValue = table.getVariableValue(name, tempStack[-1])
                    return {"address": "tv["+str(tempAddress)+"]", "value": tempValue}
                else:
                    tempStack.pop()

    def visitExpr_arith_op(self, ctx: decafParser.Expr_arith_opContext):
        global operationStack
        left = self.visit(ctx.left)
        right = self.visit(ctx.right)
        print("Operacion: ")
        print(ctx.p_arith_op().getText())
        print("Instruccion: ", ctx.getText())
        if (left["address"] == None):
            leftV = left["value"]
        else:
            leftV = left["address"]
            if ("tv" not in leftV):
                table.addGeneratedCode(leftV + " = " + left["value"])

        if (right["address"] == None):
            rightV = right["value"]
        else:
            rightV = right["address"]
            if ("tv" not in rightV):
                table.addGeneratedCode(rightV + " = " + right["value"])

        value = str(leftV) + ctx.p_arith_op().getText() + str(rightV)
        print("aqui "+value)
        operationStack.append(value)
        #table.addGeneratedCode("t- = " +  value)
        return {"address": "t"+str(len(operationStack)-1), "value": value}

    def visitExpr_op(self, ctx: decafParser.Expr_opContext):
        global operationStack
        left = self.visit(ctx.left)
        right = self.visit(ctx.right)
        print("Operacion: ")
        print(ctx.arith_op().getText())
        print("Instruccion: ", ctx.getText())
        if (left["address"] == None):
            leftV = left["value"]
        else:
            leftV = left["address"]
            if ("tv" not in leftV):
                table.addGeneratedCode(leftV + " = " + left["value"])

        if (right["address"] == None):
            rightV = right["value"]
        else:
            rightV = right["address"]
            if ("tv" not in rightV):
                table.addGeneratedCode(rightV + " = " + right["value"])

        value = str(leftV) + ctx.arith_op().getText() + str(rightV)
        print("aqui "+value)
        operationStack.append(value)
        #table.addGeneratedCode("t- = " +  value)
        return {"address": "t"+str(len(operationStack)-1), "value": value}

    def visitExpr_rel_op(self, ctx: decafParser.Expr_rel_opContext):
        left = self.visit(ctx.left)
        right = self.visit(ctx.right)
        print("Operacion: ")
        print(ctx.rel_op().getText())
        print("Instruccion: ", ctx.getText())
        if (left["address"] == None):
            leftV = left["value"]
        else:
            leftV = left["address"]
            if ("tv" not in leftV):
                table.addGeneratedCode(leftV + " = " + left["value"])

        if (right["address"] == None):
            rightV = right["value"]
        else:
            rightV = right["address"]
            if ("tv" not in rightV):
                table.addGeneratedCode(rightV + " = " + right["value"])

        value = str(leftV) + ctx.rel_op().getText() + str(rightV)
        print("aqui "+value)
        operationStack.append(value)
        #table.addGeneratedCode("t- = " +  value)
        return {"address": "t"+str(len(operationStack)-1), "value": value}

    def visitExpr_eq_op(self, ctx: decafParser.Expr_eq_opContext):
        left = self.visit(ctx.left)
        right = self.visit(ctx.right)
        print("Operacion: ")
        print(ctx.eq_op().getText())
        print("Instruccion: ", ctx.getText())
        if (left["address"] == None):
            leftV = left["value"]
        else:
            leftV = left["address"]
            if ("tv" not in leftV):
                table.addGeneratedCode(leftV + " = " + left["value"])

        if (right["address"] == None):
            rightV = right["value"]
        else:
            rightV = right["address"]
            if ("tv" not in rightV):
                table.addGeneratedCode(rightV + " = " + right["value"])

        value = str(leftV) + ctx.eq_op().getText() + str(rightV)
        print("aqui "+value)
        operationStack.append(value)
        #table.addGeneratedCode("t- = " +  value)
        return {"address": "t"+str(len(operationStack)-1), "value": value}

    def visitExpr_methodCall(self, ctx: decafParser.Expr_methodCallContext):
        methodName = ctx.methodCall().ID().getText()
        params = ctx.methodCall().arg()
        method = self.searchMethod(methodName)
        #print("invocando ",methodName)
        methodParams = method["params"]
        methodType = method["dataType"]
        countParam = 0
        #table.addGeneratedCode("Call "+methodName)
        if (params != None):
            for i in params:
                temp = self.visit(i)
                if temp["address"] == None:
                    table.addGeneratedCode("Parameter "+str(temp["value"]))
                elif "tv" not in temp["address"]:
                    table.addGeneratedCode(temp["address"]+" = "+str(temp["value"]))
                    table.addGeneratedCode("Parameter "+temp["address"])
                else:
                    table.addGeneratedCode("Parameter "+temp["address"])
                countParam +=1

        table.addGeneratedCode ("Call "+methodName+" ,"+str(countParam))
        operationStack.append("holi")
        return {"address": "t"+str(len(operationStack)-1),"value": "R"}

    def visitStm_methodcall(self, ctx: decafParser.Stm_methodcallContext):
        methodName = ctx.methodCall().ID().getText()
        params = ctx.methodCall().arg()
        method = self.searchMethod(methodName)
        print("invocando ",methodName)
        methodParams = method["params"]
        methodType = method["dataType"]
        countParam = 0
        table.addGeneratedCode("Call "+methodName)
        if (params != None):
            for i in params:
                temp = self.visit(i)
                if temp["address"] == None:
                    table.addGeneratedCode("Parameter "+str(temp["value"]))
                elif "tv" not in temp["address"]:
                    table.addGeneratedCode(temp["address"]+" = "+str(temp["value"]))
                    table.addGeneratedCode("Parameter "+temp["address"])
                else:
                    table.addGeneratedCode("Parameter "+temp["address"])
                countParam +=1

        table.addGeneratedCode ("Call "+methodName+" ,"+str(countParam))
        

    def visitStm_equal(self, ctx: decafParser.Stm_equalContext):
        global operationStack
        operationStack = []
        tempStack = scopeStack.copy()
        name = ctx.left.ID().getText()
        left = self.visit(ctx.left)
        right = self.visit(ctx.right)
        #print(str(table.scopeTable))
        while (len(tempStack) > 0):
                check = table.getVariableExists(name, tempStack[-1])
                if (check):
                    tempAddress = table.getVariableAddress(name, tempStack[-1])
                    break
                else:
                    tempStack.pop()
        table.addGeneratedCode("tv["+str(tempAddress)+"] ="+str(right["value"]))
        """
        for i in range(len(operationStack)):
            if (i == len(operationStack)-1):
                table.addGeneratedCode("tv["+str(tempAddress)+"] = "+ operationStack[i])
            else:
                table.addGeneratedCode("t"+str(i) + "= "+ operationStack[i])
        """

        operationStack = []
        print("Instruccion: ", ctx.getText())


    def visitStm_return(self, ctx: decafParser.Stm_returnContext):
        tempType = table.getScopeType(scopeStack[-1])
        if (ctx.expression() != None):
            returnType = self.visit(ctx.expression())
        table.addGeneratedCode("Return "+str(returnType["value"]))

    def visitIfScope(self, ctx: decafParser.IfScopeContext):
        expression = self.visit(ctx.expression())
        table.addGeneratedCode("If "+expression["value"])
        table.addGeneratedCode("GOTO IF-TRUE")
        if (ctx.block2 != None):
            table.addGeneratedCode("GOTO IF-FALSE")
        else:
            table.addGeneratedCode("GOTO END IF-TRUE")
        table.addGeneratedCode("IF-TRUE")
        self.visit(ctx.block1)
        table.addGeneratedCode("END IF-TRUE")
        if (ctx.block2 != None):
            table.addGeneratedCode("IF-FALSE")
            self.visit(ctx.block2)
            table.addGeneratedCode("END IF-FALSE")
        #self.visitChildren(ctx)
        
    def visitWhileScope(self, ctx: decafParser.WhileScopeContext):
        table.addGeneratedCode("WHILE-LOOP")
        expression = self.visit(ctx.expression())
        table.addGeneratedCode("If "+expression["value"])
        table.addGeneratedCode("GOTO IF-TRUE")
        table.addGeneratedCode("GOTO END-WHILE-LOOP")
        table.addGeneratedCode("IF-TRUE")
        self.visit(ctx.block())
        table.addGeneratedCode("GOTO WHILE-LOOP")
        table.addGeneratedCode("END-WHILE")



        self.visitChildren(ctx)

    def visitExpr_minus(self, ctx: decafParser.Expr_minusContext):
        exp = self.visit(ctx.expression())
        return -1 * int(exp)

    def visitExpr_not(self, ctx: decafParser.Expr_notContext):
        exp = self.visit(ctx.expression())
        if (exp == "boolean"):
            return "boolean"
    
    def visitExpr_par(self, ctx: decafParser.Expr_parContext):
        return self.visit(ctx.expression())

    def visitInt_literal(self, ctx: decafParser.Int_literalContext):
        return {"address": None, "value": int(ctx.NUM().getText())}

    def visitBool_literal(self, ctx: decafParser.Bool_literalContext):
        return "boolean"

    def visitChar_literal(self, ctx: decafParser.Char_literalContext):
        return "char"

    def searchStruct(self, structName):
        tempStack = scopeStack.copy()
        foundStruct = None
        while len(tempStack) > 0:
            check = table.checkStructUniqueInScope(tempStack[-1], structName)
            if (check):
                foundStruct = table.getStructInScope(tempStack[-1], structName)
                break
            else:
                tempStack.pop()
        return foundStruct

    def searchMethod(self, methodName):
        check = table.getMethodData(methodName)
        return check

def callback():
    global currentScope, lastScope, currentStruct, scopeStack, table
    currentScope = 0
    lastScope = 0
    currentStruct = 0
    scopeStack = []
    c=0
    text.delete(1.0, END)
    text2.delete(1.0, END)
    text3.delete(1.0, END)
    text4.delete(1.0, END)
    table = sisTypes.typeTable()
    name = fd.askopenfilename()
    #main(name)
    for i in table.errors:
        text.insert(INSERT, str(i)+"\n")
    f = open(name, "r")
    temp = f.readlines()
    for i in temp:
        c+=1
        text3.insert(INSERT, str(c)+": "+str(i))
        text2.insert(INSERT, str(i))

def tryCode():
    global currentScope, lastScope, currentStruct, scopeStack, table
    currentScope = 0
    lastScope = 0
    currentStruct = 0
    scopeStack = []
    table = sisTypes.typeTable()
    text.delete(1.0, END)
    text3.delete(1.0, END)
    text4.delete(1.0, END)
    stream = text2.get("1.0", END)
    main(stream)
    for i in table.generated:
        text.insert(INSERT, str(i)+"\n")
    lines = stream.split("\n")
    c = 0
    for l in lines:
        c+=1
        text3.insert(INSERT,  str(c)+": "+str(l)+"\n")
    for i in table.scopeTable:
        text4.insert(INSERT, "Scope: "+i["scopeName"]+"\n")
        text4.insert(INSERT, "Return: "+str(i["dataType"])+"\n")
        for j in i["variables"]:
            text4.insert(INSERT, str(j)+"\n")
    for i in table.structTable:
        text4.insert(INSERT, "Struct: "+i["dataId"]+"\n")
        for j in i["attributes"]:
            text4.insert(INSERT, str(j)+"\n")


    


def main(nombre):
    #input_stream = FileStream(nombre)
    input_stream = InputStream(nombre)
    lexer = decafLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = decafParser(stream)
    tree = parser.program()
    printer = decafListener()
    walker = ParseTreeWalker()
    walker.walk(printer, tree)
    ast = decVisitor()
    ast.visit(tree)
    asi = asiVisitor()
    asi.visit(tree)

    #print(decaf3Visitor.visitVarDeclaration())
    print(table.scopeTable)
    print("\n")
    print(table.structTable)
    print("\n")
    print(table.errors)
   
chooseFile = tk.Button(text='Choose File', command=callback).grid(column=0, row=0)
testFile = tk.Button(text='Test code', command=tryCode).grid(column=1, row=0)
text.grid(column=0, row=1)
text2.grid(column=1, row=1)
text3.grid(column=1,row=2)
text4.grid(column=0, row=2)
window.mainloop()