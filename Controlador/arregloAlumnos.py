from Controlador.alumnos import Alumno 
#MANTENIMIENTO

class ArregloAlumnos():

    #ATRIBUTOS
    dataAlumnos = [] #MOSTRAR BASE DE DATOS

    #CONSTRUCTORES
    def __init__(self):
        self.cargar()

    def adicionaAlumnos(self,objAlumno): #REGISTRAR DATOS CLIENTE
        self.dataAlumnos.append(objAlumno)

    def devolverAlumno(self, index): #RETORNAR DATOS
        return self.dataAlumnos[index]

    def tamañoArregloAlumnos(self): #DEVOLVER TAMAÑO
        return len(self.dataAlumnos)

    def buscarAlumno(self, dni): #BUSCAR CLIENTES DNI
        for i in range (self.tamañoArregloAlumnos()):
            if dni == self.dataAlumnos[i].getDniAlumno():
                return i #DEVOLVER POSICIÓN DE ELEMENTO
        return -1 #DATOS INEXISTENTES
    
    def buscarAlumnoPorCodigo(self, codigo): #BUSCAR ALUMNOS POR CÓDIGO
        for i in range (self.tamañoArregloAlumnos()):
            if codigo == self.dataAlumnos[i].getCodigoAlumno():
                return i #DEVOLVER POSICIÓN DE ELEMENTO
        return -1 #DATOS INEXISTENTES
    
    def buscarCurso(self, curso): #BUSCAR ALUMNOS POR CURSO
        resultados = []
        for i in range (self.tamañoArregloAlumnos()):
            if curso == self.dataAlumnos[i].getCursoAlumno():
                resultados.append(i)
        return resultados #DEVOLVER POSICIONES DE ELEMENTOS

    def eliminarAlumno(self, index): #ELIMINAR AL ALUMNO
        del(self.dataAlumnos[index])

    def modificarAlumno(self, objAlumno, index): #MODIFICAR DATO ALUMNO
        self.dataAlumnos[index] = objAlumno

    def retornarDatos(self): #RETORNAR DATOS
        return self.dataAlumnos
    
    # Registro de asistencias
    def registrarAsistencia(self, codigo, fecha, estado):
        """
        Registra la asistencia de un alumno por su código en una fecha específica
        """
        index = self.buscarAlumnoPorCodigo(codigo)
        if index == -1:
            return False
        
        alumno = self.devolverAlumno(index)
        alumno.registrarAsistencia(fecha, estado)
        self.modificarAlumno(alumno, index)
        self.grabar()
        return True
    
    def consultarAsistencia(self, codigo, fecha=None):
        """
        Consulta la asistencia de un alumno por su código
        Si se proporciona fecha, devuelve solo la asistencia para esa fecha
        """
        index = self.buscarAlumnoPorCodigo(codigo)
        if index == -1:
            return None
            
        alumno = self.devolverAlumno(index)
        return alumno.getAsistencia(fecha)
    
    def generarReporteAsistencias(self, fecha=None, curso=None):
        """
        Genera un reporte de asistencias, filtrado por fecha y/o curso
        """
        reporte = []
        
        for i in range(self.tamañoArregloAlumnos()):
            alumno = self.devolverAlumno(i)
            
            # Aplicar filtro de curso si se proporciona
            if curso and alumno.getCursoAlumno() != curso:
                continue
                
            dictAsistencia = alumno.getDictAsistencia()
                
            # Si se proporciona fecha, verificar solo esa fecha
            if fecha:
                estado = alumno.getAsistencia(fecha)
                if estado:  # Solo agregar si hay registro para esa fecha
                    reporte.append({
                        "codigo": alumno.getCodigoAlumno(),
                        "dni": alumno.getDniAlumno(),
                        "nombre": alumno.getApNomAlumno(),
                        "curso": alumno.getCursoAlumno(),
                        "fecha": fecha,
                        "estado": estado
                    })
            else:
                # Si no se proporciona fecha, incluir todo el historial
                for fecha, estado in dictAsistencia.items():
                    reporte.append({
                        "codigo": alumno.getCodigoAlumno(),
                        "dni": alumno.getDniAlumno(),
                        "nombre": alumno.getApNomAlumno(),
                        "curso": alumno.getCursoAlumno(),
                        "fecha": fecha,
                        "estado": estado
                    })
                    
        return reporte
    
    def grabar(self):  #GUARDAR LISTA DATACLIENTE A ALUMNOS.TXT
        archivo = open("Modelo/Alumnos.txt", "w+", encoding="UTF-8")
        for i in range(self.tamañoArregloAlumnos()):
            alumno = self.devolverAlumno(i)
            archivo.write(str(alumno.getCodigoAlumno()) + ","
            + str(alumno.getDniAlumno()) + ","
            + str(alumno.getApNomAlumno()) + ","
            + str(alumno.getCursoAlumno()) + "\n")
        archivo.close()
        
    def cargar(self):
        #CARGAR DATOS ALUMNOS.TXT A LISTA DATAALUMNOS
        self.dataAlumnos = []  
        try:
            archivo = open("Modelo/Alumnos.txt", "r", encoding="UTF-8")
            for linea in archivo.readlines():
                columna = str(linea).split(",")
                codigo = columna[0]
                dni = columna[1]
                apnom = columna[2]
                curso = columna[3].strip()
                
                objAlumno = Alumno(codigo, dni, apnom, curso)
                self.adicionaAlumnos(objAlumno)
            archivo.close()
        except FileNotFoundError:
            open("Modelo/Alumnos.txt", "w", encoding="UTF-8").close()