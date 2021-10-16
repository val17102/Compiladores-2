
class typeTable():
    def __init__(self):
        self.datatypes = ["int","char","boolean","void","error"]
        self.scopeTable = []
        self.scopeParams = []
        self.structTable = []
        self.errors = []
        self.addressCount = 0
        self.generated = []


    def addVariable(self, type, name, scope, size, array):
        
        for i in self.scopeTable:
            if (i["scopeId"] == scope):
                i["variables"].append({"dataType": type, "dataId": name, "scopeId": scope, "size":size, "array": array, "value": None, "address":self.addressCount})
                break
        if (size != None):
            self.addressCount += int(size)
        

    def addGeneratedCode(self, code):
        self.generated.append(code)

    def addScope(self, scopeNum, type, name):
        self.scopeTable.append({"scopeId": scopeNum, "dataType": type, "scopeName":name, "variables": [], "params": []})
        
    def addStruct(self, id, name, scope):
        self.structTable.append({"structId": id, "dataId": name, "scopeId": scope, "attributes": []})

    def addStructAttribute(self, type, name, size, structId, array):
        for i in self.structTable:
            if (i["structId"] == structId):
                i["attributes"].append({"dataType": type, "dataId": name, "size": size, "array": array})
                break

    def addScopeParams(self, scope, type):
        for i in self.scopeTable:
            if i["scopeId"] == scope:
                i["params"].append(type)
                #print("param "+type+" "+scope)
                break

    def checkAttributeExists(self, name, strucId):
        for i in self.structTable:
            if (i["structId"] == strucId):
                for j in i["attributes"]:
                    if (j["dataId"] == name):
                        return True
                return False

    def getVariableExists(self, name, scope):
        for i in self.scopeTable:
            if (i["scopeId"] == scope):
                for j in i["variables"]:
                    if j["dataId"] == name:
                        return True
                return False

    def getScope(self, name):
        for i in self.scopeTable:
            tempName = i["scopeName"]
            if (name == tempName):
                return True
        return False

    def getScopeId(self, name):
        for i in self.scopeTable:
            tempName = i["scopeName"]
            if (name == tempName):
                return i["scopeId"]
        return None

    def assignVariable(self, id, scope, value):
        for i in self.variableTable:
            tempId = i["dataId"]
            tempScope = i["scopeId"]
            if (id == tempId and scope == tempScope):
                i["value"] = value

    def checkVariableType(self, name, scope):
        for i in self.scopeTable:
            if (i["scopeId"] == scope):
                for j in i["variables"]:
                    if j["dataId"] == name:
                        return j["dataType"]
                return None

    def checkVariableArray(self, name, scope):
        for i in self.scopeTable:
            if (i["scopeId"] == scope):
                for j in i["variables"]:
                    if j["dataId"] == name:
                        return j["array"]
                return None

    def getVariableValue(self,name, scope):
        for i in self.scopeTable:
            if (i["scopeId"] == scope):
                for j in i["variables"]:
                    if j["dataId"] == name:
                        return j["value"]
                return None

    def getVariableAddress(self,name, scope):
        for i in self.scopeTable:
            if (i["scopeId"] == scope):
                for j in i["variables"]:
                    if j["dataId"] == name:
                        return j["address"]
                return None

    def checkMethodReturnTypeById(self, id):
        for i in self.scopeTable:
            tempId = i["scopeId"]
            if (tempId == id):
                return i["dataType"]
        return None

    def checkMethodReturnTypeByName(self, name):
        for i in self.scopeTable:
            tempName = i["scopeName"]
            if (tempName == name):
                return i["dataType"]
        return None

    def checkStructUniqueInScope(self, scope, name):
        for i in self.structTable:
            tempScope = i["scopeId"]
            tempName = i["dataId"]
            if (tempScope == scope and tempName == name):
                return True
        return False

    def checkStructExist(self, name):
        for i in self.structTable:
            tempName = i["dataId"]
            if (tempName == name):
                return True
        return False
    
    def getScopeParams(self, scope):
        temp = []
        for i in self.scopeTable:
            if (i["scopeId"] == scope):
                return(i["params"])

    def getStructInScope(self, scope, name):
        for i in self.structTable:
            tempScope = i["scopeId"]
            tempName = i["dataId"]
            if (tempScope == scope and tempName == name):
                return i
        return None

    def getStructAttribute(self, name, strucId):
        for i in self.structTable:
            if (i["structId"] == strucId):
                for j in i["attributes"]:
                    if (j["dataId"] == name):
                        return j
                return None

    def getMethodData(self, name):
        for i in self.scopeTable:
            tempName = i["scopeName"]
            if (tempName == name):
                return i
        return None

    def getScopeType(self, id):
        for i in self.scopeTable:
            tempId = i["scopeId"]
            if (id == tempId):
                return i["dataType"]
        return None

    def getScopeVariables(self, scope):
        for i in self.scopeTable:
            if (i["scopeId"] == scope):
                return i["variables"]

    def addError(self, error):
        self.errors.append(error)

        
            


