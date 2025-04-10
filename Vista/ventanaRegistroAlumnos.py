from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox
from Controlador.arregloAlumnos import ArregloAlumnos
from Controlador.alumnos import Alumno

class VentanaRegistroAlumnos(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(VentanaRegistroAlumnos, self).__init__(parent)
        uic.loadUi('UI/ventanaRegistroAlumnos.ui', self)
        

        self.arregloAlumnos = ArregloAlumnos()
        
        self.btnRegistrar.clicked.connect(self.registrarAlumno)
        self.btnBuscar.clicked.connect(self.buscarAlumno)
        self.btnEliminar.clicked.connect(self.eliminarAlumno)
        self.btnLimpiar.clicked.connect(self.limpiarCampos)
        self.btnSalir.clicked.connect(self.close)
    
    def registrarAlumno(self):
        codigo = self.txtCodigo.text()
        dni = self.txtDni.text()
        apnom = self.txtApNom.text()
        
        if not codigo or not dni or not apnom:
            QMessageBox.warning(self, "Error", "Debe completar todos los campos obligatorios")
            return
        
        if self.arregloAlumnos.buscarAlumnoPorCodigo(codigo) != -1:
            QMessageBox.warning(self, "Error", "Ya existe un alumno con el mismo código")
            return
            
        if self.arregloAlumnos.buscarAlumno(dni) != -1:
            QMessageBox.warning(self, "Error", "Ya existe un alumno con el mismo DNI")
            return
        
        objAlumno = Alumno(codigo, dni, apnom, "", "", "", "", "")
        
        self.arregloAlumnos.adicionaAlumnos(objAlumno)
        self.arregloAlumnos.grabar()
        
        QMessageBox.information(self, "Éxito", "Alumno registrado correctamente")
        self.limpiarCampos()
    
    def buscarAlumno(self):
        codigo = self.txtCodigo.text()
        dni = self.txtDni.text()
        
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
    
    def limpiarCampos(self):
        self.txtCodigo.clear()
        self.txtDni.clear()
        self.txtApNom.clear()
