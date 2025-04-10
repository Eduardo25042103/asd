from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem
from Controlador.arregloAlumnos import ArregloAlumnos
from Controlador.arregloNotas import ArregloNotas

class VentanaNotas(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(VentanaNotas, self).__init__(parent)
        uic.loadUi("UI/ventanaNotas.ui", self)
        
        # Inicializar arreglos
        self.arregloAlumnos = ArregloAlumnos()
        self.arregloNotas = ArregloNotas()
        
        # Conectar botones
        self.btnRegistrar.clicked.connect(self.registrar)
        self.btnConsultar.clicked.connect(self.consultar)
        self.btnEliminar.clicked.connect(self.eliminar)
        self.btnListar.clicked.connect(self.listar)
        self.btnModificar.clicked.connect(self.modificar)
        self.btnQuitar.clicked.connect(self.quitar)
        self.btnSalir.clicked.connect(self.close)
        
        # Cargar datos iniciales
        self.listar()
    
    def listar(self):
        self.limpiarTabla()
        
        # Mostrar solo alumnos con notas
        for nota in self.arregloNotas.dataNotas:
            codigo = nota["codigo"]
            
            # Buscar alumno por código
            index_alumno = self.arregloAlumnos.buscarAlumnoPorCodigo(codigo)
            
            if index_alumno != -1:  # Si el alumno existe
                alumno = self.arregloAlumnos.devolverAlumno(index_alumno)
                
                # Preparar datos para mostrar
                row = self.tblNotas.rowCount()
                self.tblNotas.insertRow(row)
                
                # Datos básicos del alumno
                self.tblNotas.setItem(row, 0, QTableWidgetItem(codigo))
                self.tblNotas.setItem(row, 1, QTableWidgetItem(alumno.getDniAlumno()))
                self.tblNotas.setItem(row, 2, QTableWidgetItem(alumno.getApNomAlumno()))
                self.tblNotas.setItem(row, 3, QTableWidgetItem(alumno.getCursoAlumno()))
                
                # Notas
                ec1 = nota["ec1"]
                ec2 = nota["ec2"]
                ec3 = nota["ec3"]
                exf = nota["exf"]
                
                promedio = self.arregloNotas.calcularPromedio(ec1, ec2, ec3, exf)
                estado = self.arregloNotas.determinarEstado(promedio)
                
                self.tblNotas.setItem(row, 4, QTableWidgetItem(ec1))
                self.tblNotas.setItem(row, 5, QTableWidgetItem(ec2))
                self.tblNotas.setItem(row, 6, QTableWidgetItem(ec3))
                self.tblNotas.setItem(row, 7, QTableWidgetItem(exf))
                self.tblNotas.setItem(row, 8, QTableWidgetItem(str(promedio)))
                self.tblNotas.setItem(row, 9, QTableWidgetItem(estado))
    
    def limpiarTabla(self):
        self.tblNotas.setRowCount(0)
    
    def limpiarControles(self):
        self.txtCodigo.clear()
        self.txtDni.clear()
        self.txtApNom.clear()
        self.cboCurso.setCurrentIndex(0)
        self.txtEC1.clear()
        self.txtEC2.clear()
        self.txtEC3.clear()
        self.txtEF.clear()

    def obtenerCodigo(self):
        return self.txtCodigo.text()
    
    def obtenerDni(self):
        return self.txtDni.text()
    
    def obtenerApNom(self):
        return self.txtApNom.text()
    
    def obtenerCurso(self):
        return self.cboCurso.currentText()
    
    def obtenerEC1(self):
        return self.txtEC1.text()
    
    def obtenerEC2(self):
        return self.txtEC2.text()
    
    def obtenerEC3(self):
        return self.txtEC3.text()
    
    def obtenerEF(self):
        return self.txtEF.text()
    
    def valida(self):
        if self.obtenerCodigo() == "":
            return "Código"
        if self.obtenerDni() == "":
            return "DNI"
        if self.obtenerApNom() == "":
            return "Apellidos y Nombres"
        if self.obtenerEC1() == "":
            return "EC1"
        if self.obtenerEC2() == "":
            return "EC2"
        if self.obtenerEC3() == "":
            return "EC3"
        if self.obtenerEF() == "":
            return "Examen Final"
        return ""

    def registrar(self):
        if self.valida() == "":
            codigo = self.obtenerCodigo()
            dni = self.obtenerDni()
            apNom = self.obtenerApNom()
            curso = self.obtenerCurso()
            ec1 = self.obtenerEC1()
            ec2 = self.obtenerEC2()
            ec3 = self.obtenerEC3()
            exf = self.obtenerEF()
            
            # Verificar si el alumno existe
            index_alumno = self.arregloAlumnos.buscarAlumnoPorCodigo(codigo)
            if index_alumno == -1:
                # Si no existe, mostramos mensaje
                QMessageBox.warning(self, "Registrar Notas", 
                                "El alumno no existe. Regístrelo primero.", 
                                QMessageBox.Ok)
                return
            
            # Registrar/actualizar notas
            if self.arregloNotas.buscarNotaPorCodigo(codigo) != -1:
                self.arregloNotas.actualizarNota(codigo, ec1, ec2, ec3, exf, curso)
            else:
                self.arregloNotas.adicionaNota(codigo, ec1, ec2, ec3, exf, curso)
            
            self.arregloNotas.grabar()
            QMessageBox.information(self, "Registrar Notas", 
                                "Notas registradas correctamente", 
                                QMessageBox.Ok)
            self.limpiarControles()
            self.listar()
        else:
            QMessageBox.information(self, "Registrar Notas",
                                "Error en " + self.valida(), QMessageBox.Ok)
    
    def consultar(self):
        if self.arregloAlumnos.tamañoArregloAlumnos() == 0:
            QMessageBox.information(self, "Consultar Notas",
                                    "No existen alumnos a consultar", 
                                    QMessageBox.Ok)
        else:
            codigo, ok = QtWidgets.QInputDialog.getText(self, "Consultar Notas",
                                                "Ingrese el código del alumno")
            if ok:
                index_alumno = self.arregloAlumnos.buscarAlumnoPorCodigo(codigo)
                if index_alumno == -1:
                    QMessageBox.information(self, "Consultar Notas",
                                          "El código ingresado no existe", 
                                          QMessageBox.Ok)
                    return
                
                alumno = self.arregloAlumnos.devolverAlumno(index_alumno)
                self.txtCodigo.setText(alumno.getCodigoAlumno())
                self.txtDni.setText(alumno.getDniAlumno())
                self.txtApNom.setText(alumno.getApNomAlumno())
                
                # Seleccionar curso en combobox
                index_curso = self.cboCurso.findText(alumno.getCursoAlumno())
                if index_curso != -1:
                    self.cboCurso.setCurrentIndex(index_curso)
                
                # Mostrar notas si existen
                index_nota = self.arregloNotas.buscarNotaPorCodigo(codigo)
                if index_nota != -1:
                    nota = self.arregloNotas.dataNotas[index_nota]
                    self.txtEC1.setText(nota["ec1"])
                    self.txtEC2.setText(nota["ec2"])
                    self.txtEC3.setText(nota["ec3"])
                    self.txtEF.setText(nota["exf"])
    
    def eliminar(self):
        codigo = self.obtenerCodigo()
        if codigo == "":
            QMessageBox.information(self, "Eliminar Notas",
                                    "Primero debe consultar un alumno", 
                                    QMessageBox.Ok)
            return
        
        index_nota = self.arregloNotas.buscarNotaPorCodigo(codigo)
        if index_nota == -1:
            QMessageBox.information(self, "Eliminar Notas",
                                  "El alumno no tiene notas registradas", 
                                  QMessageBox.Ok)
            return
        
        confirmacion = QMessageBox.question(self, "Eliminar Notas", 
                                           "¿Está seguro de eliminar las notas?", 
                                           QMessageBox.Yes | QMessageBox.No)
        if confirmacion == QMessageBox.Yes:
            self.arregloNotas.eliminarNota(codigo)
            self.arregloNotas.grabar()
            QMessageBox.information(self, "Eliminar Notas",
                                    "Notas eliminadas correctamente", 
                                    QMessageBox.Ok)
            self.limpiarControles()
            self.listar()

    def quitar(self):
        if self.arregloAlumnos.tamañoArregloAlumnos() == 0:
            QMessageBox.information(self, "Eliminar Notas",
                                    "No hay alumnos registrados", 
                                    QMessageBox.Ok)
            return
        
        fila = self.tblNotas.selectedItems()
        if not fila:
            QMessageBox.information(self, "Eliminar Notas",
                                    "Debe seleccionar una fila", 
                                    QMessageBox.Ok)
            return
        
        indiceFila = fila[0].row()
        codigo = self.tblNotas.item(indiceFila, 0).text()
        
        index_nota = self.arregloNotas.buscarNotaPorCodigo(codigo)
        if index_nota == -1:
            QMessageBox.information(self, "Eliminar Notas",
                                  "El alumno no tiene notas registradas", 
                                  QMessageBox.Ok)
            return
        
        confirmacion = QMessageBox.question(self, "Eliminar Notas", 
                                           "¿Está seguro de eliminar las notas?", 
                                           QMessageBox.Yes | QMessageBox.No)
        if confirmacion == QMessageBox.Yes:
            self.arregloNotas.eliminarNota(codigo)
            self.arregloNotas.grabar()
            self.listar()

    def modificar(self):
        if self.valida() == "":
            codigo = self.obtenerCodigo()
            curso = self.obtenerCurso()
            ec1 = self.obtenerEC1()
            ec2 = self.obtenerEC2()
            ec3 = self.obtenerEC3()
            exf = self.obtenerEF()
            
            index_nota = self.arregloNotas.buscarNotaPorCodigo(codigo)
            if index_nota == -1:
                QMessageBox.information(self, "Modificar Notas",
                                      "No existen notas para este alumno. Use Registrar", 
                                      QMessageBox.Ok)
                return
            
            self.arregloNotas.actualizarNota(codigo, ec1, ec2, ec3, exf, curso)
            self.arregloNotas.grabar()
            
            QMessageBox.information(self, "Modificar Notas",
                                    "Notas modificadas correctamente", 
                                    QMessageBox.Ok)
            self.limpiarControles()
            self.listar()
        else:
            QMessageBox.information(self, "Modificar Notas",
                                    "Error en " + self.valida(), QMessageBox.Ok)