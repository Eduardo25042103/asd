class Alumno():
    #ATRIBUTOS (ENCAPSULADOS)
    __dniAlumno=""; __apnomAlumno=""
    __codigoAlumno=""; __cursoAlumno=""
    __ec1Alumno=""; __ec2Alumno=""
    __ec3Alumno="" ; __exfAlumno=""
    
    #CONSTRUCTORES
    def __init__(self, codigoAlumno, dniAlumno="", apnomAlumno="", cursoAlumno="", ec1Alumno="", ec2Alumno="", ec3Alumno="", exfAlumno=""):
        self.__codigoAlumno = codigoAlumno
        self.__dniAlumno = dniAlumno
        self.__apnomAlumno = apnomAlumno
        self.__cursoAlumno = cursoAlumno
        self.__ec1Alumno = ec1Alumno
        self.__ec2Alumno = ec2Alumno
        self.__ec3Alumno = ec3Alumno
        self.__exfAlumno = exfAlumno
    
    def Promedio(self):
        try:
           return round(float(self.__ec1Alumno)*0.16 + float(self.__ec2Alumno)*0.14 + float(self.__ec3Alumno)*0.2 + float(self.__exfAlumno)*0.5,2)
        except ValueError:
            return "Nota inválida"
    
    def Estado(self):
        if isinstance(self.Promedio(), float) and self.Promedio() >= 12.5:
            return "Aprobado"
        else:
            return "Desaprobado"
    
    def getCodigoAlumno(self):
        return self.__codigoAlumno
    def setCodigoAlumno(self, codigoalumno):
        self.__codigoAlumno=codigoalumno

    def getDniAlumno(self):
        return self.__dniAlumno
    def setDniAlumno(self, dnialumno):
        self.__dniAlumno=dnialumno

    def getApNomAlumno(self):
        return self.__apnomAlumno
    def setApNomAlumno(self, apnomalumno):
        self.__apnomAlumno=apnomalumno
    
    def getCursoAlumno(self):
        return self.__cursoAlumno
    def setCursoAlumno(self, cursoalumno):
        self.__cursoAlumno=cursoalumno
    
    def getEC1Alumno(self):
        return self.__ec1Alumno
    def setEC1Alumno(self, ec1alumno):
        self.__ec1Alumno=ec1alumno

    def getEC2Alumno(self):
        return self.__ec2Alumno
    def setEC2Alumno(self, ec2alumno):
        self.__ec2Alumno=ec2alumno
    
    def getEC3Alumno(self):
        return self.__ec3Alumno
    def setEC3Alumno(self, ec3alumno):
        self.__ec3Alumno=ec3alumno

    def getEXFAlumno(self):
        return self.__exfAlumno
    def setEXFAlumno(self, exfalumno):
        self.__exfAlumno=exfalumno
