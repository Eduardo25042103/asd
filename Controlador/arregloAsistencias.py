from Controlador.arregloAlumnos import ArregloAlumnos


class ArregloAsistencias():
    #ATRIBUTOS
    dataAsistencias = [] #ALMACENAR ASISTENCIAS

    #CONSTRUCTORES
    def __init__(self):
        self.cargar()
    
    def registrarAsistencia(self, codigo, fecha, estado, curso=None):
        # Buscar si ya existe una asistencia para este código y fecha
        for i, asistencia in enumerate(self.dataAsistencias):
            if asistencia["codigo"] == codigo and asistencia["fecha"] == fecha:
                # Actualizar estado y curso
                self.dataAsistencias[i]["estado"] = estado
                if curso:
                    self.dataAsistencias[i]["curso"] = curso
                return True
        
        # Si no existe, crear nueva asistencia
        asistencia = {
            "codigo": codigo,
            "fecha": fecha,
            "estado": estado
        }
        
        # Agregar curso si fue proporcionado
        if curso:
            asistencia["curso"] = curso
            
        self.dataAsistencias.append(asistencia)
        return True
    
    def buscarAsistencia(self, codigo, fecha=None):
        resultados = []
        for asistencia in self.dataAsistencias:
            if asistencia["codigo"] == codigo:
                if fecha is None or asistencia["fecha"] == fecha:
                    resultados.append(asistencia)
        return resultados
    
    def buscarAsistenciasPorCodigo(self, codigo):
        """Devuelve todas las asistencias de un alumno dado su código"""
        return self.buscarAsistencia(codigo)
    
    def eliminarAsistencia(self, codigo, fecha):
        for i, asistencia in enumerate(self.dataAsistencias):
            if asistencia["codigo"] == codigo and asistencia["fecha"] == fecha:
                del self.dataAsistencias[i]
                return True
        return False
    
    def generarReporteAsistencias(self, codigo=None, fecha=None, curso=None):
        # Esta función necesita tener acceso a los datos de los alumnos
        # para poder filtrar por curso
        aAlumnos = ArregloAlumnos()
        
        resultados = []
        for asistencia in self.dataAsistencias:
            # Si se especificó un código y no coincide, saltar
            if codigo and asistencia["codigo"] != codigo:
                continue
                
            # Si se especificó una fecha y no coincide, saltar
            if fecha and asistencia["fecha"] != fecha:
                continue
            
            # Buscar datos del alumno
            index = aAlumnos.buscarAlumnoPorCodigo(asistencia["codigo"])
            if index != -1:
                alumno = aAlumnos.devolverAlumno(index)
                curso_alumno = alumno.getCursoAlumno()
                
                # Si se especificó un curso, verificar si coincide con el curso de la asistencia o del alumno
                if curso:
                    curso_asistencia = asistencia.get("curso", curso_alumno)
                    if curso_asistencia != curso:
                        continue
                
                resultados.append({
                    "codigo": asistencia["codigo"],
                    "dni": alumno.getDniAlumno(),
                    "nombre": alumno.getApNomAlumno(),
                    "curso": asistencia.get("curso", curso_alumno),  # Usar curso de asistencia si existe, sino curso del alumno
                    "curso_alumno": curso_alumno,  # Guardar el curso original del alumno para referencia
                    "fecha": asistencia["fecha"],
                    "estado": asistencia["estado"]
                })
        
        return resultados
    
    def calcularPorcentajeAsistencia(self, codigo):
        asistencias = self.buscarAsistencia(codigo)
        if not asistencias:
            return 0
            
        total = len(asistencias)
        presentes = sum(1 for a in asistencias if a["estado"] == "Presente")
        
        return (presentes / total) * 100 if total > 0 else 0
    
    def grabar(self):
        archivo = open("Modelo/Asistencias.txt", "w+", encoding="UTF-8")
        for asistencia in self.dataAsistencias:
            linea = (asistencia["codigo"] + "," +
                    asistencia["fecha"] + "," +
                    asistencia["estado"])
            
            # Agregar el curso si existe
            if "curso" in asistencia:
                linea += "," + asistencia["curso"]
                
            archivo.write(linea + "\n")
        archivo.close()
    
    def cargar(self):
        self.dataAsistencias = [] 
        try:
            archivo = open("Modelo/Asistencias.txt", "r", encoding="UTF-8")
            for linea in archivo.readlines():
                columna = str(linea).strip().split(",")
                if len(columna) >= 3:
                    codigo = columna[0]
                    fecha = columna[1]
                    estado = columna[2]
                    
                    # Obtener curso si existe
                    curso = None
                    if len(columna) >= 4:
                        curso = columna[3]
                    
                    self.registrarAsistencia(codigo, fecha, estado, curso)
            archivo.close()
        except FileNotFoundError:
            open("Modelo/Asistencias.txt", "w", encoding="UTF-8").close()