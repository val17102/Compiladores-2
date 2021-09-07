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
        if table.getMethodData("main") == None:
            table.addError("Error: No existe metodo main")
    
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
                            else:
                                tempError = "Error: parametro "+paramName+" ya existe: "+ str(ctx.start.line)+","+str(ctx.start.column)
                                table.addError(tempError)
        else:
            tempError = "Error: metodo "+scopeName+" ya existe: "+ str(ctx.start.line)+","+str(ctx.start.column)
            table.addError(tempError)
                    
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
            else:
                tempError = "Error: el struct ya tiene atributo "+varId+": "+ str(ctx.start.line)+","+str(ctx.start.column)
                table.addError(tempError)
        elif (not table.getVariableExists(varId, currentScope)):
            if tempArray != None:
                tempSize = DEFAULT_TYPES[varType] * tempArray
            else:
                tempSize = DEFAULT_TYPES[varType]
            table.addVariable(varType, varId, currentScope, tempSize, tempArray)
        else:
            tempError = "Error: ya existe variable "+varId+" en el mismo scope: "+ str(ctx.start.line)+","+str(ctx.start.column)
            table.addError(tempError)
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
                else:
                    tempError = "Error: Atributo dentro de struct no es valido: "+ str(ctx.start.line)+","+str(ctx.start.column)
                    table.addError(tempError)

                #vName = i.ID().getText()
        else:
            tempError = "Error: ya existe struct "+structId+": "+ str(ctx.start.line)+","+str(ctx.start.column)
            table.addError(tempError)

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
        else:
            tempError = "Error: struct "+instanceParent+" no existe: "+ str(ctx.start.line)+","+str(ctx.start.column)
            table.addError(tempError)

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
        print(scopeName, " cantidad de scopes en stack ", scopeStack)
        self.visitChildren(ctx)
        if (len(scopeStack) > 0):
            scopeStack.pop()

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
                    if ("struct" not in tempType):
                        tempError = "Error: no es struct "+name+": "+ str(ctx.start.line)+","+str(ctx.start.column)
                        table.addError(tempError)
                        return None
                    else:
                        if (ctx.expression() != None):
                            if (table.checkVariableArray(name, tempStack[-1]) == None):
                                tempError = "Error: location "+name+" no es un array: "+ str(ctx.start.line)+","+str(ctx.start.column)
                                table.addError(tempError)
                                return None
                            if (self.visit(ctx.expression()) != "int"):
                                tempError = "Error: posicion de array invalido: "+ str(ctx.start.line)+","+str(ctx.start.column)
                                table.addError(tempError)
                                return None
                        structName = tempType.split("struct ")[1]
                        return self.visitLocation(ctx.location(), structName)
                else:
                    tempStack.pop()
            if (not found):
                tempError = "Error: no se encontro el location "+name+": "+ str(ctx.start.line)+","+str(ctx.start.column)
                table.addError(tempError)
                return None
        elif (ctx.location() != None and structParent != None):
            tempStruct = self.searchStruct(structParent)
            if (tempStruct != None):
                if (table.checkAttributeExists(name, tempStruct["structId"])):
                    tempAttribute = table.getStructAttribute(name, tempStruct["structId"])
                    if ("struct" not in tempAttribute["dataType"]):
                        tempError = str("Error: attribute "+name+" no es struct: "+ str(ctx.start.line)+","+str(ctx.start.column))
                        table.addError(tempError)
                        return None
                    else:
                        if (ctx.expression() != None):
                            if (tempAttribute["array"] == None):
                                tempError = "Error: location "+name+"no es un array: "+ str(ctx.start.line)+","+str(ctx.start.column)
                                table.addError(tempError)
                                return None
                            if (self.visit(ctx.expression()) != "int"):
                                tempError = "Error: posicion de array invalido: "+ str(ctx.start.line)+","+str(ctx.start.column)
                                table.addError(tempError)
                                return None
                        structName = tempAttribute["dataType"].split("struct ")[1]
                        return self.visitLocation(ctx.location(), structName)
            else:
                tempError = "Error: struct no existe "+name+": "+ str(ctx.start.line)+","+str(ctx.start.column)
                table.addError(tempError)
                return None
        elif (structParent != None):
            print("searching for struct ",structParent)
            tempStruct = self.searchStruct(structParent)
            if (tempStruct != None):
                if (table.checkAttributeExists(name, tempStruct["structId"])):
                    tempAttribute = table.getStructAttribute(name, tempStruct["structId"])
                    if (ctx.expression() != None):
                            if (tempAttribute["array"] == None):
                                tempError = "Error: location"+name+" no es un array: "+ str(ctx.start.line)+","+str(ctx.start.column)
                                table.addError(tempError)
                                return None
                            if (self.visit(ctx.expression()) != "int"):
                                tempError = "Error: posicion de array invalido: "+ str(ctx.start.line)+","+str(ctx.start.column)
                                table.addError(tempError)
                                return None
                    return tempAttribute["dataType"]
                else:
                    tempError = "Error: no se encontro el attribute "+name+": "+ str(ctx.start.line)+","+str(ctx.start.column)
                    table.addError(str(tempError))
                    return None
            else:
                tempError = "Error: no se encontro el attribute "+name+": "+ str(ctx.start.line)+","+str(ctx.start.column)
                table.addError(str(tempError))
                return None
        else:
            while (len(tempStack) > 0):
                check = table.getVariableExists(name, tempStack[-1])
                if (check):
                    if (ctx.expression() != None):
                            if (table.checkVariableArray(name, tempStack[-1]) == None):
                                tempError = "Error: location "+name+" no es un array: "+ str(ctx.start.line)+","+str(ctx.start.column)
                                table.addError(tempError)
                                return None
                            if (self.visit(ctx.expression()) != "int"):
                                tempError = "Error: posicion de array invalido: "+ str(ctx.start.line)+","+str(ctx.start.column)
                                table.addError(tempError)
                                return None
                    found = True
                    tempType = table.checkVariableType(name, tempStack[-1])
                    return tempType
                else:
                    tempStack.pop()
            if not found:
                tempError = "Error: no existe el location "+name+": "+ str(ctx.start.line)+","+str(ctx.start.column)
                table.addError(tempError)
                return None

    def visitExpr_arith_op(self, ctx: decafParser.Expr_arith_opContext):
        left = self.visit(ctx.left)
        right = self.visit(ctx.right)
        print("Operacion: ")
        print(ctx.p_arith_op().getText())
        print("Instruccion: ", ctx.getText())
        if (left == "int" and right == "int"):
            return "int"
        else:
            tempError = "Error: no se puede realizar operacion "+str(left)+" "+ctx.p_arith_op().getText()+" "+str(right)+": "+ str(ctx.start.line)+","+str(ctx.start.column)
            table.addError(tempError)
            return "Error"

    def visitExpr_op(self, ctx: decafParser.Expr_opContext):
        left = self.visit(ctx.left)
        right = self.visit(ctx.right)
        print("Operacion: ")
        print(ctx.arith_op().getText())
        print("Instruccion: ", ctx.getText())
        if (left == "int" and right == "int"):
            return "int"
        else:
            tempError = "Error: no se puede realizar operacion"+str(left)+" "+ctx.arith_op().getText()+" "+str(right)+": "+ str(ctx.start.line)+","+str(ctx.start.column)
            table.addError(tempError)
            return "Error"

    def visitExpr_rel_op(self, ctx: decafParser.Expr_rel_opContext):
        left = self.visit(ctx.left)
        right = self.visit(ctx.right)
        print("Operacion: ")
        print(ctx.rel_op().getText())
        print("Instruccion: ", ctx.getText())
        if (left == "int" and right == "int"):
            return "boolean"
        else:
            tempError = "Error: no se puede realizar comparacion"+str(left)+" "+ctx.rel_op().getText()+" "+str(right)+": "+ str(ctx.start.line)+","+str(ctx.start.column)
            table.addError(tempError)
            return "Error"

    def visitExpr_eq_op(self, ctx: decafParser.Expr_eq_opContext):
        left = self.visit(ctx.left)
        right = self.visit(ctx.right)
        print("Operacion: ")
        print(ctx.eq_op().getText())
        print("Instruccion: ", ctx.getText())
        if (left == "int" and right == "int"):
            return "boolean"
        elif (left == "char" and right == "char"):
            return "boolean"
        elif (left == "boolean" and right == "boolean"):
            return "boolean"
        else:
            tempError = "Error: no se puede realizar comparacion "+str(left)+" "+ctx.eq_op().getText()+" "+str(right)+": "+ str(ctx.start.line)+","+str(ctx.start.column)
            table.addError(tempError)
            return "Error"

    def visitExpr_methodCall(self, ctx: decafParser.Expr_methodCallContext):
        methodName = ctx.methodCall().ID().getText()
        params = ctx.methodCall().arg()
        method = self.searchMethod(methodName)
        print("invocando ",methodName)
        if (method == None):
            tempError = "Error: No existe ese metodo"+methodName+": "+ str(ctx.start.line)+","+str(ctx.start.column)
            table.addError(tempError)
            return None
        methodParams = method["params"]
        methodType = method["dataType"]
        if (params != None):
            if (len(params) == len(methodParams)):
                for i,j in zip(params, methodParams):
                    tempType = self.visit(i)
                    if (tempType != j):
                        tempError = "Error: se esperaba parametro tipo "+str(j)+" pero se recibio "+str(tempType)+": "+ str(ctx.start.line)+","+str(ctx.start.column)
                        table.addError(tempError)
                        return None
                return methodType
            else:
                tempError = "Error: diferente cantidad de parametros dados: "+ str(ctx.start.line)+","+str(ctx.start.column)
                table.addError(tempError)
                return None
        else:
            if (len(methodParams) > 0):
                tempError = "Error: metodo requiere parametros: "+ str(ctx.start.line)+","+str(ctx.start.column)
                table.addError(tempError)
                return None
            else:
                return methodType

    def visitStm_methodcall(self, ctx: decafParser.Stm_methodcallContext):
        methodName = ctx.methodCall().ID().getText()
        params = ctx.methodCall().arg()
        method = self.searchMethod(methodName)
        print("invocando ",methodName)
        if (method == None):
            tempError = "Error: No existe metodo "+methodName+": "+ str(ctx.start.line)+","+str(ctx.start.column)
            table.addError(tempError)
            return None
        methodParams = method["params"]
        methodType = method["dataType"]
        if (params != None):
            if (len(params) == len(methodParams)):
                for i,j in zip(params, methodParams):
                    tempType = self.visit(i)
                    if (tempType != j):
                        tempError = "Error: se esperaba parametro tipo "+str(j)+" pero se recibio "+str(tempType)+": "+ str(ctx.start.line)+","+str(ctx.start.column)
                        table.addError(tempError)
                        return None
                return methodType
            else:
                tempError = "Error: diferente cantidad de parametros dados: "+ str(ctx.start.line)+","+str(ctx.start.column)
                table.addError(tempError)
                return None
        else:
            if (len(methodParams) > 0):
                tempError = "Error: metodo requiere parametros: "+ str(ctx.start.line)+","+str(ctx.start.column)
                table.addError(tempError)
                return None
            else:
                return methodType

    def visitStm_equal(self, ctx: decafParser.Stm_equalContext):
        left = self.visit(ctx.left)
        right = self.visit(ctx.right)
        print("Instruccion: ", ctx.getText())
        if (left != right):
            tempError = "Error: no se puede asignar "+str(right)+" a "+str(left)+": "+ str(ctx.start.line)+","+str(ctx.start.column)
            table.addError(tempError)


    def visitStm_return(self, ctx: decafParser.Stm_returnContext):
        tempType = table.getScopeType(scopeStack[-1])
        if (ctx.expression() != None):
            if (tempType == "void"):
                tempError = "Error: metodo no deberia tener un return con valor: "+ str(ctx.start.line)+","+str(ctx.start.column)
                table.addError(tempError)
            returnType = self.visit(ctx.expression())
            if (returnType != tempType):
                tempError = "Error: tipo de return es distinto al definido: "+ str(ctx.start.line)+","+str(ctx.start.column)
                table.addError(tempError)

    def visitIfScope(self, ctx: decafParser.IfScopeContext):
        expressionType = self.visit(ctx.expression())
        if (expressionType != "boolean"):
            tempError = "Error: condiciones de if solo pueden ser boolean: "+ str(ctx.start.line)+","+str(ctx.start.column)
            table.addError(tempError)
        self.visitChildren(ctx)
        
    def visitWhileScope(self, ctx: decafParser.WhileScopeContext):
        expressionType = self.visit(ctx.expression())
        if (expressionType != "boolean"):
            tempError = "Error: condiciones de while solo pueden ser boolean: "+ str(ctx.start.line)+","+str(ctx.start.column)
            table.addError(tempError)
        self.visitChildren(ctx)

    def visitExpr_minus(self, ctx: decafParser.Expr_minusContext):
        exp = self.visit(ctx.expression())
        if (exp == "int"):
            return "int"
        else:
            return "Error"

    def visitExpr_not(self, ctx: decafParser.Expr_notContext):
        exp = self.visit(ctx.expression())
        if (exp == "boolean"):
            return "boolean"
        else:
            return "Error"
    
    def visitExpr_par(self, ctx: decafParser.Expr_parContext):
        return self.visit(ctx.expression())

    def visitInt_literal(self, ctx: decafParser.Int_literalContext):
        return "int"

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
    for i in table.errors:
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