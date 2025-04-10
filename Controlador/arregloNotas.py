class ArregloNotas():
    #ATRIBUTOS
    dataNotas = [] #ALMACENAR NOTAS

    #CONSTRUCTORES
    def __init__(self):
        self.cargar()
    
    def adicionaNota(self, codigo, ec1, ec2, ec3, exf, curso):
        # Crear un diccionario con las notas
        nota = {
            "codigo": codigo,
            "ec1": ec1,
            "ec2": ec2,
            "ec3": ec3,
            "exf": exf,
            "curso": curso
        }
        self.dataNotas.append(nota)
    
    def calcularPromedio(self, ec1, ec2, ec3, exf):
        try:
            return round(float(ec1)*0.16 + float(ec2)*0.14 + float(ec3)*0.2 + float(exf)*0.5, 2)
        except ValueError:
            return "Nota inválida"
    
    def determinarEstado(self, promedio):
        if isinstance(promedio, float) and promedio >= 12.5:
            return "Aprobado"
        else:
            return "Desaprobado"
    
    def buscarNotaPorCodigo(self, codigo):
        for i, nota in enumerate(self.dataNotas):
            if nota["codigo"] == codigo:
                return i
        return -1
    
    def actualizarNota(self, codigo, ec1, ec2, ec3, exf, curso):
        index = self.buscarNotaPorCodigo(codigo)
        if index != -1:
            self.dataNotas[index] = {
                "codigo": codigo,
                "ec1": ec1,
                "ec2": ec2,
                "ec3": ec3,
                "exf": exf,
                "curso": curso
            }
            return True
        return False
    
    def eliminarNota(self, codigo):
        index = self.buscarNotaPorCodigo(codigo)
        if index != -1:
            del self.dataNotas[index]
            return True
        return False
    
    def grabar(self):
        archivo = open("Modelo/Notas.txt", "w+", encoding="UTF-8")
        for nota in self.dataNotas:
            promedio = self.calcularPromedio(nota["ec1"], nota["ec2"], nota["ec3"], nota["exf"])
            estado = self.determinarEstado(promedio)
            archivo.write(
                nota["codigo"] + "," +
                nota["ec1"] + "," +
                nota["ec2"] + "," +
                nota["ec3"] + "," +
                nota["exf"] + "," +
                nota["curso"] + "," +
                str(promedio) + "," +
                estado + "\n"
            )
        archivo.close()
    
    def cargar(self):
        try:
            archivo = open("Modelo/Notas.txt", "r", encoding="UTF-8")
            for linea in archivo.readlines():
                columna = str(linea).split(",")
                if len(columna) >= 6:  # Ahora tenemos un campo más (curso)
                    codigo = columna[0]
                    ec1 = columna[1]
                    ec2 = columna[2]
                    ec3 = columna[3]
                    exf = columna[4]
                    curso = columna[5]
                    
                    self.adicionaNota(codigo, ec1, ec2, ec3, exf, curso)
            archivo.close()
        except FileNotFoundError:
            open("Modelo/Notas.txt", "w", encoding="UTF-8").close()