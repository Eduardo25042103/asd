class ArregloAsistencias():
    #ATRIBUTOS
    dataAsistencias = [] #ALMACENAR ASISTENCIAS

    #CONSTRUCTORES
    def __init__(self):
        self.cargar()
    
    def registrarAsistencia(self, codigo, fecha, estado):
        # Buscar si ya existe una asistencia para este código y fecha
        for i, asistencia in enumerate(self.dataAsistencias):
            if asistencia["codigo"] == codigo and asistencia["fecha"] == fecha:
                # Actualizar estado
                self.dataAsistencias[i]["estado"] = estado
                return True
        
        # Si no existe, crear nueva asistencia
        asistencia = {
            "codigo": codigo,
            "fecha": fecha,
            "estado": estado
        }
        self.dataAsistencias.append(asistencia)
        return True
    
    def buscarAsistencia(self, codigo, fecha=None):
        resultados = []
        for asistencia in self.dataAsistencias:
            if asistencia["codigo"] == codigo:
                if fecha is None or asistencia["fecha"] == fecha:
                    resultados.append(asistencia)
        return resultados
    
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
                
            # Si se especificó un curso, verificar si el alumno está en ese curso
            if curso:
                index = aAlumnos.buscarAlumnoPorCodigo(asistencia["codigo"])
                if index == -1 or aAlumnos.devolverAlumno(index).getCursoAlumno() != curso:
                    continue
            
            # Buscar datos del alumno
            index = aAlumnos.buscarAlumnoPorCodigo(asistencia["codigo"])
            if index != -1:
                alumno = aAlumnos.devolverAlumno(index)
                resultados.append({
                    "codigo": asistencia["codigo"],
                    "dni": alumno.getDniAlumno(),
                    "nombre": alumno.getApNomAlumno(),
                    "curso": alumno.getCursoAlumno(),
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
            archivo.write(
                asistencia["codigo"] + "," +
                asistencia["fecha"] + "," +
                asistencia["estado"] + "\n"
            )
        archivo.close()
    
    def cargar(self):
        try:
            archivo = open("Modelo/Asistencias.txt", "r", encoding="UTF-8")
            for linea in archivo.readlines():
                columna = str(linea).strip().split(",")
                if len(columna) >= 3:
                    codigo = columna[0]
                    fecha = columna[1]
                    estado = columna[2]
                    
                    self.registrarAsistencia(codigo, fecha, estado)
            archivo.close()
        except FileNotFoundError:
            open("Modelo/Asistencias.txt", "w", encoding="UTF-8").close()