from os import name, remove
from tkinter.constants import END, INSERT, RIGHT
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
ifCount = 0
whileCount = 0
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
        table.addressCount = 0
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
            table.calculateStructSize(structId)

                #vName = i.ID().getText()

    def visitStructInstance(self, ctx: decafParser.StructInstanceContext, structParent = None):
        instanceParent = ctx.ID()[0].getText()
        instanceId = ctx.ID()[1].getText()
        tempArray = None
        if (table.checkStructExist(instanceParent)):
            tempSize = table.getStructSize(instanceParent)
            if (ctx.NUM() != None):
                    tempArray = int(ctx.NUM().getText())
                    tempSize = tempSize * tempArray
            if (structParent != None):
                table.addStructAttribute("struct "+instanceParent, instanceId, tempSize, structParent, tempArray)
            else:
                table.addVariable("struct "+instanceParent, instanceId, currentScope, tempSize, tempArray)

class asiVisitor(decafVisitor):    
    def visitProgram(self, ctx: decafParser.ProgramContext):
        global scopeStack
        scopeStack.append(0)
        return self.visitChildren(ctx)

    def visitMethodDeclaration(self, ctx: decafParser.MethodDeclarationContext):
        global scopeStack, ifCount, whileCount
        scopeName = ctx.ID().getText()
        scopeId = table.getScopeId(scopeName)
        scopeStack.append(scopeId)
        scopeVariables = table.getScopeVariables(scopeStack[-1])
        print(scopeName, " cantidad de scopes en stack ", scopeStack)
        table.addGeneratedCode("Def "+scopeName+":")
        acc = 0
        for i in scopeVariables:
            acc += i["size"]
        table.addGeneratedCode("Allocate "+str(acc))
        params = table.getScopeParams(scopeId)
        for i in range(len(params)):
            table.addGeneratedCode("tv["+str(scopeVariables[i]["address"])+"] = ParamPop "+str(DEFAULT_TYPES[params[i]]))
        self.visitChildren(ctx)
        if (len(scopeStack) > 0):
            scopeStack.pop()
        table.addGeneratedCode("End "+scopeName+"\n")

    def visitLocation(self, ctx: decafParser.LocationContext, structParent = None):
        global operationStack
        tempStack = scopeStack.copy()
        name = ctx.ID().getText()
        found = False
        if (ctx.location() != None and structParent == None):
            print("Se encontro ",ctx.getText())
            while (len(tempStack) > 0):
                check = table.getVariableExists(name, tempStack[-1])
                if (check):
                    if (ctx.expression() != None):
                        tempAddress = 0
                        tempPos = self.visit(ctx.expression())
                        if (tempPos["value"] != None and tempPos["address"] != None):
                            table.addGeneratedCode(tempPos["address"]+" = "+str(tempPos["value"]))
                            table.addGeneratedCode("t"+str(len(operationStack))+" = "+tempPos["address"] +" * "+str(table.getVariableSizeArray(name, tempStack[-1]))) 
                            tempAddress = "t"+str(len(operationStack))
                            operationStack.append("location")
                        elif (tempPos["address"] == None and tempPos["value"] != None):
                            tempAddress += tempPos["value"] * table.getVariableSizeArray(name, tempStack[-1])
                            tempAddress += table.getVariableAddress(name, tempStack[-1])
                        elif (tempPos["address"] != None and tempPos["value"] == None):
                            table.addGeneratedCode("t"+str(len(operationStack))+" = "+tempPos["address"] +" * "+str(table.getVariableSizeArray(name, tempStack[-1]))) 
                            tempAddress = "t"+str(len(operationStack))
                            operationStack.append("location")
                    else:
                        tempType = table.checkVariableType(name, tempStack[-1])
                        structName = tempType.split("struct ")[1]
                        tempAddress = self.visitLocation(ctx.location(), structName)
                        tempAddress += table.getVariableAddress(name, tempStack[-1])
                    
                    return {"address": "tv["+str(tempAddress)+"]", "value": None}
                else:
                    tempStack.pop()
        elif (ctx.location() != None and structParent != None):
            tempStruct = self.searchStruct(structParent)
            if (tempStruct != None):
                if (ctx.expression() != None):
                        tempAddress = 0
                        tempPos = self.visit(ctx.expression())
                        if (tempPos["value"] != None and tempPos["address"] != None):
                            table.addGeneratedCode(tempPos["address"]+" = "+str(tempPos["value"]))
                            table.addGeneratedCode("t"+str(len(operationStack))+" = "+tempPos["address"] +" * "+str(table.getVariableSizeArray(name, tempStack[-1]))) 
                            tempAddress = "t"+str(len(operationStack))
                            operationStack.append("location")
                        elif (tempPos["address"] == None and tempPos["value"] != None):
                            tempAddress += tempPos["value"] * table.getVariableSizeArray(name, tempStack[-1])
                            tempAddress += table.getVariableAddress(name, tempStack[-1])
                        elif (tempPos["address"] != None and tempPos["value"] == None):
                            table.addGeneratedCode("t"+str(len(operationStack))+" = "+tempPos["address"] +" * "+str(table.getVariableSizeArray(name, tempStack[-1]))) 
                            tempAddress = "t"+str(len(operationStack))
                            operationStack.append("location")
                else:
                    if (table.checkAttributeExists(name, tempStruct["structId"])):
                        tempAttribute = table.getStructAttribute(name, tempStruct["structId"])
                        structName = tempAttribute["dataType"].split("struct ")[1]
                        tempAddress = self.visitLocation(ctx.location(), structName)
                        tempAddress += table.getAttributeAddress(tempStruct["dataId"],name)
                        return tempAddress
        elif (structParent != None):
            print("searching for struct ",structParent)
            tempStruct = self.searchStruct(structParent)
            if (tempStruct != None):
                if (table.checkAttributeExists(name, tempStruct["structId"])):
                    tempAttribute = table.getStructAttribute(name, tempStruct["structId"])
                    localAddress = table.getAttributeAddress(tempStruct["dataId"],name)
                    return localAddress
        else:
            while (len(tempStack) > 0):
                check = table.getVariableExists(name, tempStack[-1])
                if (check):
                    tempAddress = 0
                    tempType = table.checkVariableType(name, tempStack[-1])
                    if (ctx.expression() != None):
                        tempPos = self.visit(ctx.expression())
                        if (tempPos["value"] != None and tempPos["address"] != None):
                            table.addGeneratedCode(tempPos["address"]+" = "+str(tempPos["value"]))
                            table.addGeneratedCode("t"+str(len(operationStack))+" = "+tempPos["address"] +" * "+str(DEFAULT_TYPES[tempType])) 
                            tempAddress = "t"+str(len(operationStack))
                            operationStack.append("location")
                        elif (tempPos["address"] == None and tempPos["value"] != None):
                            tempAddress += tempPos["value"] * DEFAULT_TYPES[tempType]
                            tempAddress += table.getVariableAddress(name, tempStack[-1])
                        elif (tempPos["address"] != None and tempPos["value"] == None):
                            table.addGeneratedCode("t"+str(len(operationStack))+" = "+tempPos["address"] +" * "+str(DEFAULT_TYPES[tempType])) 
                            tempAddress = "t"+str(len(operationStack))
                            operationStack.append("location")
                    else: 
                        tempAddress = table.getVariableAddress(name, tempStack[-1])
                    tempValue = table.getVariableValue(name, tempStack[-1])
                    if tempStack[-1] == 0:
                        return {"address": "gl["+str(tempAddress)+"]", "value": tempValue}
                    else:    
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
        if(len(operationStack)-1 == 1):
            operationStack = []
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
        if(len(operationStack)-1 == 1):
            operationStack = []
        operationStack.append(value)
        #table.addGeneratedCode("t- = " +  value)
        return {"address": "t"+str(len(operationStack)-1), "value": value}

    def visitExpr_cond_op(self, ctx: decafParser.Expr_cond_opContext):
        global operationStack
        left = self.visit(ctx.left)
        right = self.visit(ctx.right)
        print("Operacion: ")
        print(ctx.cond_op().getText())
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

        value = str(leftV) + ctx.cond_op().getText() + str(rightV)
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
            if ("tv" not in leftV and "gl" not in leftV):
                table.addGeneratedCode(leftV + " = " + left["value"])

        if (right["address"] == None):
            rightV = right["value"]
        else:
            rightV = right["address"]
            if ("tv" not in rightV and "gl" not in rightV):
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
            if ("tv" not in leftV and "gl" not in leftV):
                table.addGeneratedCode(leftV + " = " + left["value"])

        if (right["address"] == None):
            rightV = right["value"]
        else:
            rightV = right["address"]
            if ("tv" not in rightV and "gl" not in rightV):
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
                elif "tv" not in temp["address"] and "gl" not in temp["address"]:
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
        if (params != None):
            for i in params:
                temp = self.visit(i)
                if temp["address"] == None:
                    table.addGeneratedCode("Parameter "+str(temp["value"]))
                elif "tv" not in temp["address"] and "gl" not in temp["address"]:
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
        if (right["value"] != None):
            table.addGeneratedCode(str(left["address"])+" = "+str(right["value"]))
        else:
            table.addGeneratedCode(str(left["address"])+" = "+str(right["address"]))
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
        if (returnType["value"] != None):
            table.addGeneratedCode("Return "+str(returnType["value"]))
        else:
            table.addGeneratedCode("Return "+str(returnType["address"]))

    def visitIfScope(self, ctx: decafParser.IfScopeContext):
        global ifCount
        expression = self.visit(ctx.expression())
        ifCount += 1
        tempifCount = ifCount
        table.addGeneratedCode("If "+expression["value"])
        table.addGeneratedCode("GOTO IF_"+str(tempifCount)+"_TRUE")
        if (ctx.block2 != None):
            table.addGeneratedCode("GOTO IF_"+str(tempifCount)+"_FALSE")
        else:
            table.addGeneratedCode("GOTO END_IF_"+str(tempifCount)+"_TRUE")
        table.addGeneratedCode("IF_"+str(tempifCount)+"_TRUE")
        self.visit(ctx.block1)
        table.addGeneratedCode("END_IF_"+str(tempifCount)+"_TRUE")
        if (ctx.block2 != None):
            table.addGeneratedCode("IF_"+str(tempifCount)+"_FALSE")
            self.visit(ctx.block2)
            table.addGeneratedCode("END_IF_"+str(tempifCount)+"_FALSE")
        
        #self.visitChildren(ctx)
        
    def visitWhileScope(self, ctx: decafParser.WhileScopeContext):
        global whileCount, ifCount
        whileCount += 1
        ifCount += 1
        tempwhileCount = whileCount
        tempifCount = ifCount
        table.addGeneratedCode("WHILE_LOOP"+str(tempwhileCount))
        expression = self.visit(ctx.expression())
        table.addGeneratedCode("If "+expression["value"])
        table.addGeneratedCode("GOTO IF_"+str(tempifCount)+"_TRUE")
        table.addGeneratedCode("GOTO END_WHILE_LOOP"+str(tempwhileCount))
        table.addGeneratedCode("IF_"+str(tempifCount)+"_TRUE")
        self.visit(ctx.block())
        table.addGeneratedCode("GOTO WHILE_LOOP"+str(tempwhileCount))
        table.addGeneratedCode("END_WHILE_LOOP"+str(tempwhileCount))



        #self.visitChildren(ctx)

    def visitExpr_minus(self, ctx: decafParser.Expr_minusContext):
        global operationStack
        exp = self.visit(ctx.expression())
        if (isinstance(exp["value"], str)):
            table.addGeneratedCode(exp["address"] + " = " + exp["value"])
            operationStack.append("minus")
            return {"address": "t"+str(len(operationStack)), "value": "-1 * " + str(exp["address"])}
        elif (exp["value"] != None):
            return {"address": None, "value": -1 * int(exp["value"])}
        else:
            return {"address": None, "value": "-" + str(exp["address"])}

    def visitExpr_not(self, ctx: decafParser.Expr_notContext):
        exp = self.visit(ctx.expression())
        if (isinstance(exp["value"], str)):
            table.addGeneratedCode(exp["address"] + " = " + exp["value"])
            return {"address": None, "value": "not " + str(exp["address"])}
        if (exp["value"] != None):
            return {"address": None, "value": "not " + str(exp["value"])}
        else:
            return {"address": None, "value": "not" + str(exp["address"])}
    
    def visitExpr_par(self, ctx: decafParser.Expr_parContext):
        return self.visit(ctx.expression())

    def visitInt_literal(self, ctx: decafParser.Int_literalContext):
        return {"address": None, "value": int(ctx.NUM().getText())}

    def visitBool_literal(self, ctx: decafParser.Bool_literalContext):
        return {"address": None, "value": int(ctx.getText())}

    def visitChar_literal(self, ctx: decafParser.Char_literalContext):
        return {"address": None, "value": int(ctx.CHAR().getText())}

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

registerDict = {
    "R0": "",
    "R1": "",
    "R2": "",
    "R3": "",
    "R4": "",
    "R5": "",
    "R6": "",
    "R7": "",
    "R8": "",
    "R9": "",
    "R10": "",
    "R11": "",
}

registerStatus = {
    "R0": "av",
    "R1": "av",
    "R2": "av",
    "R3": "av",
    "R4": "av",
    "R5": "av",
    "R6": "av",
    "R7": "av",
    "R8": "av",
    "R9": "av",
    "R10": "av",
    "R11": "un",
}

paramCount = 0
lineReader = 0
instruction = ""
gotoCount = 0
currentFunction = ""
currentAloc = 0
currentLeaf = False
currentReturn = False

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
    global currentScope, lastScope, currentStruct, scopeStack, table, lineReader
    currentScope = 0
    lastScope = 0
    currentStruct = 0
    lineReader = 0
    resetRegisters()
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
    convertToARM()
    text4.insert(INSERT, "endOfAll:")
    addGlobalVariables()



def convertToARM():
    global lineReader
    global paramCount
    global gotoCount
    global currentFunction
    global currentAloc
    global currentLeaf
    text4.insert(INSERT, ".global _start\n")
    for i in table.generated:
        if ("Def" in str(i)):
            temp = i.split(" ")
            currentLeaf = verifyLeaf(lineReader)
            currentReturn = verifyReturn(lineReader)
            if (temp[1] == "main:"):
                text4.insert(INSERT, "_start:\n")
                currentFunction = "_start:"
                text4.insert(INSERT, "\t push {r11, lr}\n")
            elif (not currentLeaf):
                text4.insert(INSERT, temp[1]+"\n")
                text4.insert(INSERT, "\t push {r11, lr}\n")
                currentFunction = temp[1]
            else:
                text4.insert(INSERT, temp[1]+"\n")
                text4.insert(INSERT, "\t push {r11}\n")
                currentFunction = temp[1]
            text4.insert(INSERT, "\t add  r11, sp, #0\n")
        elif ("Allocate" in str(i)):
            temp = i.split(" ")
            text4.insert(INSERT, "\t sub  sp, sp, #"+temp[1]+"\n")
            currentAloc = int(temp[1])
        elif (" = " in str(i)):
            temp = i.split(" = ")
            left = temp[0]
            right = temp[1]
            print(i)
            handleOperations(left, right)
        elif ("Parameter" in str(i)):
            temp = i.split(" ")
            handleParameter(temp[1])
        elif ("Call" in str(i)):
            temp = i.split(" ")
            text4.insert(INSERT, "\t bl   "+temp[1]+"\n")
            paramCount = 0
        elif ("Return" in str(i)):
            temp = i.split(" ")
            handleReturn(temp[1].replace(" ",""))
            if (not currentLeaf):
                text4.insert(INSERT, "\t sub  sp, r11, #0\n")
                text4.insert(INSERT, "\t pop  {r11, pc}\n")
                text4.insert(INSERT, "\t bx   lr\n")
            else:
                text4.insert(INSERT, "\t add  sp, r11, #0\n")
                text4.insert(INSERT, "\t pop  {r11}\n")
                text4.insert(INSERT, "\t bx   lr\n")
        elif ("If" in str(i)):
            temp = i.split(" ")
            handleIf(temp[1].replace(" ",""))
        elif ("GOTO" in str(i)):
            dest = i.split(" ")[1]
            if (gotoCount > 0):
                text4.insert(INSERT, "\t "+instruction+"  ."+dest+"\n")
                gotoCount = 0
            else:
                text4.insert(INSERT, "\t b    ."+dest+"\n")
        elif ("GOTO" not in str(i) and ("IF_" in str(i) or "END_WHILE" in str(i) or "WHILE_LOOP" in str(i))):
            text4.insert(INSERT, "."+str(i)+":\n")
        elif ("End" in str(i)):
            if (currentFunction == "OutputInt:"):
                text4.insert(INSERT, "\t ldr  R1, =0xff201000\n")
                text4.insert(INSERT, "\t add  R0, R0, #48\n")
                text4.insert(INSERT, "\t str  R0, [R1]\n")
                text4.insert(INSERT, "\t mov  R0, #10\n")
                text4.insert(INSERT, "\t str  R0, [R1]\n")
                
            if (currentFunction == "_start:"):
                text4.insert(INSERT, "\t b    endOfAll\n")
            elif (not currentReturn):
                if (not currentLeaf):
                    text4.insert(INSERT, "\t sub  sp, r11, #0\n")
                    text4.insert(INSERT, "\t pop  {r11, pc}\n")
                    text4.insert(INSERT, "\t bx   lr\n")
                else:
                    text4.insert(INSERT, "\t add  sp, r11, #0\n")
                    text4.insert(INSERT, "\t pop  {r11}\n")
                    text4.insert(INSERT, "\t bx   lr\n")
                

        lineReader += 1

def handleOperations(left,right):
    global paramCount
    aritOperators = ["+","-","*","/"]
    opRight = ""
    opLeft = ""
    flag = False
    temp = ""
    if ("ParamPop" in right):
        temp1 = left.replace(" ","")
        temp1 = temp1.split("[")
        offset = temp1[1][0:-1]
        temp2 = list(registerDict.keys())
        text4.insert(INSERT, "\t str  "+temp2[paramCount]+", [sp, #"+offset+"]\n")
        registerStatus[temp2[paramCount]] = "av"
        paramCount += 1
        if ("ParamPop" not in table.generated[lineReader+1]):
            paramCount = 0
    if ("ParamPop" not in right and right != " R"):
        for i in aritOperators:
            if (i in right):
                temp = i
                break
        if temp != "":
            op = right.split(temp)
            opLeft = handleOperator(op[0])
            opRight = handleOperator(op[1])

            regR = getAvailableRegister()
            if (temp == "+"):
                if ("#" in opLeft and "#" in opRight):
                    r = int(opLeft.replace("#","")) + int(opRight.replace("#",""))
                    text4.insert(INSERT, "\t mov "+regR+", #"+str(r)+"\n")
                    registerStatus[regR] = "un"
                else:
                    text4.insert(INSERT, "\t add  "+regR+", "+opLeft+", "+opRight+"\n")
                    registerStatus[opLeft] = "av"
            elif (temp == "-"):
                if ("#" in opLeft and "#" in opRight):
                    r = int(opLeft.replace("#","")) - int(opRight.replace("#",""))
                    text4.insert(INSERT, "\t mov "+regR+", #"+str(r)+"\n")
                    registerStatus[regR] = "un"
                else:
                    text4.insert(INSERT, "\t sub  "+regR+", "+opLeft+", "+opRight+"\n")
                    registerStatus[opLeft] = "av"
            elif (temp == "*"):
                if ("#" in opLeft and "#" in opRight):
                    r = int(opLeft.replace("#","")) * int(opRight.replace("#",""))
                    text4.insert(INSERT, "\t mov "+regR+", #"+str(r)+"\n")
                    registerStatus[regR] = "un"
                else:
                    if ("#" in opRight):
                        mulTemp = getAvailableRegister()
                        text4.insert(INSERT, "\t mov "+mulTemp+", "+str(opRight)+"\n")
                        opRight = mulTemp
                    text4.insert(INSERT, "\t mul  "+regR+", "+opLeft+", "+opRight+"\n")
                    registerStatus[opLeft] = "av"
        else:
            regR = getRegisterWithValue(right.replace(" ",""))
            if (regR == None):
                regR = handleRightValue(right.replace(" ",""))

        if ("[" in left):
            separation = left.split("[")
            sepL = separation[0]
            sepR = separation[1]
            if ("tv" in sepL):
                temp1 = sepL.replace(" ","")
                temp2 = sepR.replace(" ","")
                offset = temp2[0:-1]
                if ("t" in offset):
                    regT = getRegisterWithValue(offset)
                    text4.insert(INSERT, "\t str  "+regR+", [sp, "+regT+"]\n")
                    registerStatus[regR] = "av"
                else:    
                    text4.insert(INSERT, "\t str  "+regR+", [sp, #"+offset+"]\n")
                    registerStatus[regR] = "av"
                    registerDict[regR] = left.replace(" ","")
                removeTemp()
            if ("gl" in sepL):
                temp1 = sepL.replace(" ","")
                temp2 = sepR.replace(" ","")
                offset = temp2[0:-1]
                regGl = getRegisterWithValue(".globalS")
                if (regGl == None):
                    regGl = getAvailableRegister()
                    registerDict[regGl] = ".globalS"
                    registerStatus[regGl] = "un"
                    text4.insert(INSERT, "\t ldr  "+regGl+", .globalS\n")
                if ("t" in offset):
                    regT = getRegisterWithValue(offset)
                    text4.insert(INSERT, "\t str  "+regR+", ["+regGl+", "+regT+"]\n")
                    registerStatus[regR] = "av"
                    registerStatus[regGl] = "av"
                else:    
                    text4.insert(INSERT, "\t str  "+regR+", ["+regGl+", #"+offset+"]\n")
                    registerStatus[regR] = "av"
                    registerStatus[regGl] = "av"
                    registerDict[regR] = left.replace(" ","")
                removeTemp()
        elif ("t" in left):
            registerDict[regR] = left.replace(" ","")
            registerStatus[regR] = "un"
            if ("#" not in opLeft):
                if (registerDict[regR] == "t0" and registerDict[opLeft] == "t1"):
                    registerStatus[opLeft] = "av"
                if (registerDict[regR] == "t1" and registerDict[opLeft] == "t0"):
                    registerStatus[opLeft] = "av"
        

def handleOperator(op):
    t1 = op.replace(" ","")
    print("Buscando "+t1)
    temp = getRegisterWithValue(t1)
    if (temp != None):
        return temp
    else:
        if ("tv" in t1):
            temp1 = t1.split("[")
            offset = temp1[1][0:-1]
            reg = getAvailableRegister()
            text4.insert(INSERT, "\t ldr  "+reg+", [sp, #"+offset+"]\n")
            registerDict[reg] = t1
            registerStatus[reg] = "un"
            return reg
        else:
            return("#"+t1)

def handleParameter(param):
    global paramCount
    temp = list(registerDict.keys())
    print(param)
    print(registerDict)
    if ("[" in param):
        separation = param.split("[")
        sepL = separation[0]
        sepR = separation[1]
        if ("tv" in sepL):
            temp1 = sepL.replace(" ","")
            temp2 = sepR.replace(" ","")
            offset = temp2[0:-1]
            if ("t" in offset):
                regT = getRegisterWithValue(offset)
                text4.insert(INSERT, "\t ldr  "+temp[paramCount]+", [sp, "+regT+"]\n")
            else:    
                text4.insert(INSERT, "\t ldr  "+temp[paramCount]+", [sp, #"+offset+"]\n")
            registerDict[temp[paramCount]] = param
        if ("gl" in sepL):
            temp1 = sepL.replace(" ","")
            temp2 = sepR.replace(" ","")
            offset = temp2[0:-1]
            regGl = getRegisterWithValue(".globalS")
            if (regGl == None):
                regGl = getAvailableRegister()
                registerDict[regGl] = ".globalS"
                registerStatus[regGl] = "un"
                text4.insert(INSERT, "\t ldr  "+regGl+", .globalS\n")
            if ("t" in offset):
                regT = getRegisterWithValue(offset)
                text4.insert(INSERT, "\t ldr  "+temp[paramCount]+", ["+regGl+", "+regT+"]\n")
                registerStatus[regGl] = "av"
                registerStatus[regT] = "av"
            else:    
                text4.insert(INSERT, "\t ldr  "+temp[paramCount]+", ["+regGl+", #"+offset+"]\n")
                registerStatus[regGl] = "av"
            registerDict[temp[paramCount]] = param
    elif ("t" in param):
        temp1 = getRegisterWithValue(param)
        text4.insert(INSERT, "\t mov "+temp[paramCount]+", "+temp1+"\n")
        registerDict[temp[paramCount]] = param
    else:
        text4.insert(INSERT, "\t mov "+temp[paramCount]+", #"+param+"\n")
        registerDict[temp[paramCount]] = param
    paramCount += 1

def handleIf(comp):
    global instruction, gotoCount
    instDict = {"==":"beq", "<":"ble", ">":"bge", "!=":"bne"}
    logOp = ["==","<",">","!="]
    for i in logOp:
        if (i in comp):
            temp = i
            break
    separate = comp.split(temp)
    compL = separate[0]
    compR = separate[1]
    reg1= handleRightValue(compL)
    reg2 = handleRightValue(compR)
    text4.insert(INSERT, "\t cmp  "+reg1+", "+reg2+"\n")
    registerStatus[reg1] = "av"
    registerStatus[reg2] = "av"
    gotoCount = 1
    instruction = instDict[temp]
    """
    dest1 = table.generated[lineReader+1]
    dest1 = dest1.split(" ")[1]
    dest2 = table.generated[lineReader+2]
    dest2 = dest2.split(" ")[1]
    instruction = instDict[temp]
    text4.insert(INSERT, "\t "+instruction+"  ."+dest1+"\n")
    text4.insert(INSERT, "\t b    ."+dest2+"\n").
    """

    

def handleRightValue(right):
    if (right == "R"):
        return "R0"
    if ("[" in right):
        separation = right.split("[")
        sepL = separation[0]
        sepR = separation[1]
        if ("tv" in sepL):
            temp1 = sepL.replace(" ","")
            temp2 = sepR.replace(" ","")
            offset = temp2[0:-1]
            regR = getAvailableRegister()
            if ("t" in offset):
                regT = getRegisterWithValue(offset)
                text4.insert(INSERT, "\t ldr  "+regR+", [sp, "+regT+"]\n")
                registerStatus[regR] = "un"
                registerStatus[regT] = "av"
            else:    
                text4.insert(INSERT, "\t ldr  "+regR+", [sp, #"+offset+"]\n")
                registerStatus[regR] = "un"
            regR2 = getAvailableRegister()
            text4.insert(INSERT, "\t ldr  "+regR2+", [sp, "+regR+"]\n")
            registerStatus[regR] = "av"
            registerStatus[regR2] = "un"
            registerDict[regR2] = right
            return regR2
        if ("gl" in sepL):
            temp1 = sepL.replace(" ","")
            temp2 = sepR.replace(" ","")
            offset = temp2[0:-1]
            regGl = getRegisterWithValue(".globalS")
            if (regGl == None):
                regGl = getAvailableRegister()
                registerDict[regGl] = ".globalS"
                registerStatus[regGl] = "un"
                text4.insert(INSERT, "\t ldr  "+regGl+", .globalS\n")
            regR = getAvailableRegister()
            if ("t" in offset):
                regT = getRegisterWithValue(offset)
                text4.insert(INSERT, "\t ldr  "+regR+", ["+regGl+", "+regT+"]\n")
                registerStatus[regR] = "un"
                registerStatus[regGl] = "av"
            else:    
                text4.insert(INSERT, "\t ldr  "+regR+", ["+regGl+", #"+offset+"]\n")
                registerStatus[regR] = "un"
                registerStatus[regGl] = "av"
            registerDict[regR] = right
            return regR
    else:
        regR = getAvailableRegister()
        text4.insert(INSERT, "\t mov  "+regR+", #"+right+"\n")
        registerStatus[regR] = "un"
        registerDict[regR] = right
        return regR

def removeTemp():
    c = 0
    temp = list(registerDict.keys())
    for i in temp:
        if ("tv" in registerDict[i]):
            c = 0
        elif ("t" in registerDict[i]):
            registerDict[i] = ""
            registerStatus[i] = "av"

def handleReturn(value):
    aritOperators = ["+","-","*","/"]
    temp = ""
    for i in aritOperators:
            if (i in value):
                temp = i
                break
    if temp != "":
        op = value.split(temp)
        opLeft = handleOperator(op[0])
        opRight = handleOperator(op[1])

        regR = getAvailableRegister()
        if (temp == "+"):
            if ("#" in opLeft and "#" in opRight):
                r = int(opLeft.replace("#","")) + int(opRight.replace("#",""))
                text4.insert(INSERT, "\t mov "+regR+", #"+str(r)+"\n")
                registerStatus[regR] = "un"
            else:
                text4.insert(INSERT, "\t add  "+regR+", "+opLeft+", "+opRight+"\n")
                registerStatus[opLeft] = "av"
        elif (temp == "-"):
            if ("#" in opLeft and "#" in opRight):
                r = int(opLeft.replace("#","")) - int(opRight.replace("#",""))
                text4.insert(INSERT, "\t mov "+regR+", #"+str(r)+"\n")
                registerStatus[regR] = "un"
            else:
                text4.insert(INSERT, "\t sub  "+regR+", "+opLeft+", "+opRight+"\n")
                registerStatus[opLeft] = "av"
        elif (temp == "*"):
            if ("#" in opLeft and "#" in opRight):
                r = int(opLeft.replace("#","")) * int(opRight.replace("#",""))
                text4.insert(INSERT, "\t mov "+regR+", #"+str(r)+"\n")
                registerStatus[regR] = "un"
            else:
                if ("#" in opRight):
                    mulTemp = getAvailableRegister()
                    text4.insert(INSERT, "\t mov "+mulTemp+", "+str(opRight)+"\n")
                    opRight = mulTemp
                text4.insert(INSERT, "\t mul  "+regR+", "+opLeft+", "+opRight+"\n")
                registerStatus[opLeft] = "av"
        text4.insert(INSERT, "\t mov  R0, "+str(regR)+"\n")
    elif ("[" in value):
        separation = value.split("[")
        sepL = separation[0]
        sepR = separation[1]
        if ("tv" in sepL):
            temp1 = sepL.replace(" ","")
            temp2 = sepR.replace(" ","")
            offset = temp2[0:-1]
            regR = getAvailableRegister()
            if ("t" in offset):
                regT = getRegisterWithValue(offset)
                text4.insert(INSERT, "\t ldr  "+regR+", [sp, "+regT+"]\n")
                registerStatus[regR] = "un"
                registerStatus[regT] = "av"
            else:    
                text4.insert(INSERT, "\t ldr  "+regR+", [sp, #"+offset+"]\n")
                registerStatus[regR] = "un"
        if ("gl" in sepL):
            temp1 = sepL.replace(" ","")
            temp2 = sepR.replace(" ","")
            offset = temp2[0:-1]
            regGl = getRegisterWithValue(".globalS")
            if (regGl == None):
                regGl = getAvailableRegister()
                registerDict[regGl] = ".globalS"
                registerStatus[regGl] = "un"
                text4.insert(INSERT, "\t ldr  "+regGl+", .globalS\n")
            regR = getAvailableRegister()
            if ("t" in offset):
                regT = getRegisterWithValue(offset)
                text4.insert(INSERT, "\t ldr  "+regR+", ["+regGl+", "+regT+"]\n")
                registerStatus[regR] = "un"
                registerStatus[regGl] = "av"
            else:    
                text4.insert(INSERT, "\t ldr  "+regR+", ["+regGl+", #"+offset+"]\n")
                registerStatus[regR] = "un"
                registerStatus[regGl] = "av"
    else:
        regR = getAvailableRegister()
        text4.insert(INSERT, "\t mov  "+regR+", #"+value+"\n")
        registerStatus[regR] = "un"
        registerDict[regR] = value
    print(registerStatus)

def addGlobalVariables():
    gl = table.getScopeVariables(0)
    acc = 0
    for i in gl:
        acc += i["size"]

    text4.insert(INSERT,"\n.globalS:   .long   globalV\n")
    text4.insert(INSERT,"globalV:   .zero   "+str(acc)+"\n")

def getAvailableRegister():
    for i in registerDict.keys():
        if (registerDict[i] == "" or registerStatus[i] == "av"):
            return i


def getRegisterWithValue(value):
    print(registerDict)
    for i in registerDict.keys():
        if (value == registerDict[i]):
            return i
    return None

def resetRegisters():
    for i in list(registerDict.keys()):
        if (i != "R11"):
            registerDict[i] = ""
            registerStatus[i] = "av"

def verifyLeaf(currentLine):
    flag = False
    temp = currentLine
    while (not flag):
        temp += 1
        if "Call" in table.generated[temp]:
            return False
        if ("End" in table.generated[temp]):
            flag = True
    return True

def verifyReturn(currentLine):
    flag = False
    temp = currentLine
    while (not flag):
        temp += 1
        if "Return" in table.generated[temp]:
            return True
        if ("End" in table.generated[temp]):
            flag = True
    return False

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