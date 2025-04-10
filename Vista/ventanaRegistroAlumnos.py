from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem
from Controlador.arregloAlumnos import ArregloAlumnos
from Controlador.alumnos import Alumno

class VentanaRegistroAlumnos(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(VentanaRegistroAlumnos, self).__init__(parent)
        uic.loadUi('UI/ventanaRegistroAlumnos.ui', self)
        
        self.arregloAlumnos = ArregloAlumnos()

        self.cboCurso = QtWidgets.QComboBox(self)
        self.cboCurso.addItems(["Matemáticas", "Física", "Química", "Programación", "Base de Datos", "Inglés"])
        self.cboCurso.setGeometry(30, 250, 161, 20)  # Posicionarlo debajo del campo txtApNom
        
        # Añadir etiqueta para el combobox
        self.lblCurso = QtWidgets.QLabel(self)
        self.lblCurso.setText("Curso:")
        self.lblCurso.setGeometry(30, 230, 181, 20)
        
        self.btnRegistrar.clicked.connect(self.registrarAlumno)
        self.btnBuscar.clicked.connect(self.buscarAlumno)
        self.btnEliminar.clicked.connect(self.eliminarAlumno)
        self.btnLimpiar.clicked.connect(self.limpiarCampos)
        self.btnSalir.clicked.connect(self.close)
        
        # Configurar la tabla de DNIs
        self.tblDNIs.verticalHeader().setVisible(False)
        
        # Cargar los DNIs existentes al iniciar
        self.cargarTablaDNIs()
    
    def cargarTablaDNIs(self):
        """Carga todos los DNIs de alumnos en la tabla"""
        # Limpiar tabla
        self.tblDNIs.setRowCount(0)
        
        # Recorrer todos los alumnos
        for i in range(self.arregloAlumnos.tamañoArregloAlumnos()):
            alumno = self.arregloAlumnos.devolverAlumno(i)
            
            # Añadir fila
            rowPosition = self.tblDNIs.rowCount()
            self.tblDNIs.insertRow(rowPosition)
            
            # Insertar DNI y código
            self.tblDNIs.setItem(rowPosition, 0, QTableWidgetItem(alumno.getDniAlumno()))
            self.tblDNIs.setItem(rowPosition, 1, QTableWidgetItem(alumno.getCodigoAlumno()))
            self.tblDNIs.setItem(rowPosition, 2, QTableWidgetItem(alumno.getCursoAlumno()))
    def registrarAlumno(self):
        codigo = self.txtCodigo.text()
        dni = self.txtDni.text()
        apnom = self.txtApNom.text()
        curso = self.cboCurso.currentText()
        
        if not codigo or not dni or not apnom:
            QMessageBox.warning(self, "Error", "Debe completar todos los campos obligatorios")
            return
        
        if self.arregloAlumnos.buscarAlumnoPorCodigo(codigo) != -1:
            QMessageBox.warning(self, "Error", "Ya existe un alumno con el mismo código")
            return
            
        if self.arregloAlumnos.buscarAlumno(dni) != -1:
            QMessageBox.warning(self, "Error", "Ya existe un alumno con el mismo DNI")
            return
        
        objAlumno = Alumno(codigo, dni, apnom, curso, "", "", "", "")
        
        self.arregloAlumnos.adicionaAlumnos(objAlumno)
        self.arregloAlumnos.grabar()
        
        QMessageBox.information(self, "Éxito", "Alumno registrado correctamente")
        self.limpiarCampos()
        
        # Actualizar la tabla de DNIs
        self.cargarTablaDNIs()
    
    def buscarAlumno(self):
        codigo = self.txtCodigo.text()
        dni = self.txtDni.text()
        curso = self.cboCurso.currentText()
        
        if not codigo and not dni:
            QMessageBox.warning(self, "Error", "Debe ingresar el código o DNI del alumno")
            return
        
        index = -1
        if codigo:
            index = self.arregloAlumnos.buscarAlumnoPorCodigo(codigo)
        elif dni:
            index = self.arregloAlumnos.buscarAlumno(dni)
        
        if index == -1:
            QMessageBox.warning(self, "Error", "Alumno no encontrado")
            return
        
        alumno = self.arregloAlumnos.devolverAlumno(index)
        
        self.txtCodigo.setText(alumno.getCodigoAlumno())
        self.txtDni.setText(alumno.getDniAlumno())
        self.txtApNom.setText(alumno.getApNomAlumno())

        index_curso = self.cboCurso.findText(alumno.getCursoAlumno())
        if index_curso != -1:
            self.cboCurso.setCurrentIndex(index_curso)
    
    def eliminarAlumno(self):
        codigo = self.txtCodigo.text()
        
        if not codigo:
            QMessageBox.warning(self, "Error", "Debe ingresar el código del alumno a eliminar")
            return
        
        index = self.arregloAlumnos.buscarAlumnoPorCodigo(codigo)
        
        if index == -1:
            QMessageBox.warning(self, "Error", "Alumno no encontrado")
            return
        
        confirmacion = QMessageBox.question(self, "Confirmar eliminación", 
                                          "¿Está seguro de eliminar este alumno?",
                                          QMessageBox.Yes | QMessageBox.No)
        if confirmacion == QMessageBox.No:
            return
        
        self.arregloAlumnos.eliminarAlumno(index)
        self.arregloAlumnos.grabar()
        
        QMessageBox.information(self, "Éxito", "Alumno eliminado correctamente")
        self.limpiarCampos()
        
        # Actualizar la tabla de DNIs después de eliminar
        self.cargarTablaDNIs()
    
    def limpiarCampos(self):
        self.txtCodigo.clear()
        self.txtDni.clear()
        self.txtApNom.clear()
        self.cboCurso.setCurrentIndex(0)
