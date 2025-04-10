from Controlador.alumnos import Alumno

class Asistencia():

    #ATRIBUTOS(ENCAPSULADOS)
    __dniEmpleado =""; __nombresEmpleado= ""
    __apellidoPaternoEmpleado =""; apellidoMaternoEmpleado= ""
    __direccionEmpleado= ""; __alumno=Alumno("0")
    

    #CONSTRUCTORES
    def __init__(self, fecha, alumno: Alumno):
        self.__fechaAsistencia = fecha
        self.__alumno = alumno

        

    def getDniEmpleado(self):
        return self.__dniEmpleado
    def setDniEmpleado(self, dniempleado):
        self.__dniEmpleado=dniempleado

    def getNombresEmpleado(self):
        return self.__nombresEmpleado
    def setNombresEmpleado(self, nombresempleado):
        self.__nombresEmpleado=nombresempleado
