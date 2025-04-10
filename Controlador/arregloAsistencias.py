from Controlador.alumnos import Alumno
from datetime import date

class ArregloAsistencias:
    """
    Clase para gestionar las asistencias de los alumnos.
    Aunque usamos el modelo de Alumno para almacenar las asistencias,
    esta clase proporciona métodos específicos para manejar asistencias.
    """
    
    def __init__(self, arregloAlumnos):
        """
        Inicializa con una referencia al arreglo de alumnos
        """
        self.arregloAlumnos = arregloAlumnos
    
    def registrarAsistencia(self, dni, fecha, asistio=True):
        """
        Registra la asistencia de un alumno en una fecha específica
        """
        index = self.arregloAlumnos.buscarAlumno(dni)
        if index == -1:
            return False
        
        alumno = self.arregloAlumnos.devolverAlumno(index)
        
        # Formar la fecha en formato string YYYY-MM-DD
        if isinstance(fecha, date):
            fecha_str = fecha.strftime("%Y-%m-%d")
        else:
            fecha_str = fecha
            
        # Obtener diccionario de asistencias actual
        try:
            dictAsistencia = eval(alumno.getFechasAsistenciaAlumno() or "{}")
        except:
            dictAsistencia = {}
        
        # Registrar asistencia
        dictAsistencia[fecha_str] = "A" if asistio else "F"
        
        # Actualizar alumno
        alumno.setFechasAsistenciaAlumno(str(dictAsistencia))
        self.arregloAlumnos.modificarAlumno(alumno, index)
        self.arregloAlumnos.grabar()
        
        return True
    
    def consultarAsistencia(self, dni, fecha=None):
        """
        Consulta la asistencia de un alumno
        Si se proporciona fecha, devuelve la asistencia para esa fecha
        Si no, devuelve todo el historial de asistencias
        """
        index = self.arregloAlumnos.buscarAlumno(dni)
        if index == -1:
            return None
            
        alumno = self.arregloAlumnos.devolverAlumno(index)
        
        # Formar la fecha en formato string YYYY-MM-DD si es un objeto date
        if isinstance(fecha, date):
            fecha_str = fecha.strftime("%Y-%m-%d")
        else:
            fecha_str = fecha
            
        # Obtener diccionario de asistencias
        try:
            dictAsistencia = eval(alumno.getFechasAsistenciaAlumno() or "{}")
        except:
            dictAsistencia = {}
            
        # Si se proporciona fecha, devolver solo esa asistencia
        if fecha_str:
            return dictAsistencia.get(fecha_str, None)
        
        # De lo contrario, devolver todo el diccionario
        return dictAsistencia
    
    def generarReporteAsistencias(self, fecha=None, curso=None):
        """
        Genera un reporte de asistencias, filtrado por fecha y/o curso
        Retorna una lista de diccionarios con la información
        """
        # Formar la fecha en formato string YYYY-MM-DD si es un objeto date
        if isinstance(fecha, date):
            fecha_str = fecha.strftime("%Y-%m-%d")
        else:
            fecha_str = fecha
            
        reporte = []
        
        for i in range(self.arregloAlumnos.tamañoArregloAlumnos()):
            alumno = self.arregloAlumnos.devolverAlumno(i)
            
            # Aplicar filtro de curso si se proporciona
            if curso and alumno.getCursoAlumno() != curso:
                continue
                
            # Obtener diccionario de asistencias
            try:
                dictAsistencia = eval(alumno.getFechasAsistenciaAlumno() or "{}")
            except:
                dictAsistencia = {}
                
            # Si se proporciona fecha, verificar solo esa fecha
            if fecha_str:
                asistencia = dictAsistencia.get(fecha_str, None)
                if asistencia:
                    reporte.append({
                        "codigo": alumno.getCodigoAlumno(),
                        "dni": alumno.getDniAlumno(),
                        "nombre": alumno.getApNomAlumno(),
                        "curso": alumno.getCursoAlumno(),
                        "fecha": fecha_str,
                        "asistio": asistencia == "A"
                    })
            else:
                # Si no se proporciona fecha, incluir todo el historial
                for fecha, asistencia in dictAsistencia.items():
                    reporte.append({
                        "codigo": alumno.getCodigoAlumno(),
                        "dni": alumno.getDniAlumno(),
                        "nombre": alumno.getApNomAlumno(),
                        "curso": alumno.getCursoAlumno(),
                        "fecha": fecha,
                        "asistio": asistencia == "A"
                    })
                    
        return reporte
    
    def calcularPorcentajeAsistencia(self, dni):
        """
        Calcula el porcentaje de asistencia de un alumno
        """
        index = self.arregloAlumnos.buscarAlumno(dni)
        if index == -1:
            return 0
            
        alumno = self.arregloAlumnos.devolverAlumno(index)
        
        # Obtener diccionario de asistencias
        try:
            dictAsistencia = eval(alumno.getFechasAsistenciaAlumno() or "{}")
        except:
            dictAsistencia = {}
            
        if not dictAsistencia:
            return 0
            
        # Contar asistencias
        total = len(dictAsistencia)
        asistencias = sum(1 for asistencia in dictAsistencia.values() if asistencia == "A")
        
        if total == 0:
            return 0
            
        return (asistencias / total) * 100