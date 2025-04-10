import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem
from Controlador.arregloAlumnos import ArregloAlumnos
from Controlador.arregloAsistencias import ArregloAsistencias
from datetime import datetime

class VentanaAsistencias(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(VentanaAsistencias, self).__init__(parent)
        uic.loadUi('UI/ventanaAsistencias.ui', self)
        
        # Inicializar arreglos
        self.arregloAlumnos = ArregloAlumnos()
        self.arregloAsistencias = ArregloAsistencias()

        # Configurar la tabla de DNIs
        self.tblDNIs.verticalHeader().setVisible(False)
        
        # Conectar botones con funciones
        self.btnRegistrar.clicked.connect(self.registrarAsistencia)
        self.btnConsultar.clicked.connect(self.buscarAlumno)
        self.btnListar.clicked.connect(self.listarAsistencias)
        self.btnModificar.clicked.connect(self.actualizarAsistencia)
        self.btnEliminar.clicked.connect(self.eliminarAsistencia)
        self.btnSalir.clicked.connect(self.close)
        
        # Configurar fecha actual
        self.dateFecha.setDate(datetime.now())
        
        # Llenar tabla inicial
        self.listarAsistencias()
    
    def registrarAsistencia(self):
        codigo = self.txtCodigo.text()
        dni = self.txtDni.text()
        fecha = self.dateFecha.date().toString("yyyy-MM-dd")
        estado = self.cboEstado.currentText()
        
        # Verificar que se haya ingresado un código o DNI
        if not codigo and not dni:
            QMessageBox.warning(self, "Error", "Debe ingresar el código o DNI del alumno")
            return
        
        # Buscar alumno
        index = -1
        if codigo:
            index = self.arregloAlumnos.buscarAlumnoPorCodigo(codigo)
        elif dni:
            index = self.arregloAlumnos.buscarAlumno(dni)
        
        if index == -1:
            QMessageBox.warning(self, "Error", "Alumno no encontrado")
            return
        
        # Obtener alumno
        alumno = self.arregloAlumnos.devolverAlumno(index)
        codigo = alumno.getCodigoAlumno()
        
        # Registrar asistencia
        self.arregloAsistencias.registrarAsistencia(codigo, fecha, estado)
        self.arregloAsistencias.grabar()
        
        QMessageBox.information(self, "Éxito", "Asistencia registrada correctamente")
        self.listarAsistencias()
        self.limpiarCampos()
    
    def buscarAlumno(self):
        codigo = self.txtCodigo.text()
        dni = self.txtDni.text()
        
        # Verificar que se haya ingresado un código o DNI
        if not codigo and not dni:
            QMessageBox.warning(self, "Error", "Debe ingresar el código o DNI del alumno")
            return
        
        # Buscar alumno
        index = -1
        if codigo:
            index = self.arregloAlumnos.buscarAlumnoPorCodigo(codigo)
        elif dni:
            index = self.arregloAlumnos.buscarAlumno(dni)
        
        if index == -1:
            QMessageBox.warning(self, "Error", "Alumno no encontrado")
            return
        
        # Obtener alumno
        alumno = self.arregloAlumnos.devolverAlumno(index)
        
        # Mostrar información del alumno
        self.txtCodigo.setText(alumno.getCodigoAlumno())
        self.txtDni.setText(alumno.getDniAlumno())
        self.txtApNom.setText(alumno.getApNomAlumno())
        
        # Establecer curso en el combo box
        index_curso = self.cboCurso.findText(alumno.getCursoAlumno())
        if index_curso != -1:
            self.cboCurso.setCurrentIndex(index_curso)
        
        # Listar asistencias del alumno
        self.listarAsistenciasAlumno(alumno.getCodigoAlumno())
    
    def listarAsistencias(self):
        # Limpiar tabla
        self.tblAsistencias.setRowCount(0)
        
        # Generar reporte combinando datos de alumnos y asistencias
        reporte = self.arregloAsistencias.generarReporteAsistencias()
        
        # Llenar tabla
        for asistencia in reporte:
            rowPosition = self.tblAsistencias.rowCount()
            self.tblAsistencias.insertRow(rowPosition)
            
            self.tblAsistencias.setItem(rowPosition, 0, QTableWidgetItem(asistencia["codigo"]))
            self.tblAsistencias.setItem(rowPosition, 1, QTableWidgetItem(asistencia["dni"]))
            self.tblAsistencias.setItem(rowPosition, 2, QTableWidgetItem(asistencia["nombre"]))
            self.tblAsistencias.setItem(rowPosition, 3, QTableWidgetItem(asistencia["curso"]))
            self.tblAsistencias.setItem(rowPosition, 4, QTableWidgetItem(asistencia["fecha"]))
            self.tblAsistencias.setItem(rowPosition, 5, QTableWidgetItem(asistencia["estado"]))
    
    def listarAsistenciasAlumno(self, codigo):
        # Limpiar tabla
        self.tblAsistencias.setRowCount(0)
        
        # Generar reporte para el alumno específico
        reporte = self.arregloAsistencias.generarReporteAsistencias(codigo=codigo)
        
        # Llenar tabla
        for asistencia in reporte:
            rowPosition = self.tblAsistencias.rowCount()
            self.tblAsistencias.insertRow(rowPosition)
            
            self.tblAsistencias.setItem(rowPosition, 0, QTableWidgetItem(asistencia["codigo"]))
            self.tblAsistencias.setItem(rowPosition, 1, QTableWidgetItem(asistencia["dni"]))
            self.tblAsistencias.setItem(rowPosition, 2, QTableWidgetItem(asistencia["nombre"]))
            self.tblAsistencias.setItem(rowPosition, 3, QTableWidgetItem(asistencia["curso"]))
            self.tblAsistencias.setItem(rowPosition, 4, QTableWidgetItem(asistencia["fecha"]))
            self.tblAsistencias.setItem(rowPosition, 5, QTableWidgetItem(asistencia["estado"]))
    
    def actualizarAsistencia(self):
        # Obtener fila seleccionada
        fila_seleccionada = self.tblAsistencias.currentRow()
        if fila_seleccionada == -1:
            QMessageBox.warning(self, "Error", "Debe seleccionar una asistencia para actualizar")
            return
        
        # Obtener datos de la fila seleccionada
        codigo = self.tblAsistencias.item(fila_seleccionada, 0).text()
        fecha = self.tblAsistencias.item(fila_seleccionada, 4).text()
        
        # Obtener nuevo estado
        estado = self.cboEstado.currentText()
        
        # Actualizar asistencia
        self.arregloAsistencias.registrarAsistencia(codigo, fecha, estado)
        self.arregloAsistencias.grabar()
        
        QMessageBox.information(self, "Éxito", "Asistencia actualizada correctamente")
        self.listarAsistencias()
    
    def eliminarAsistencia(self):
        # Obtener fila seleccionada
        fila_seleccionada = self.tblAsistencias.currentRow()
        if fila_seleccionada == -1:
            QMessageBox.warning(self, "Error", "Debe seleccionar una asistencia para eliminar")
            return
        
        # Confirmar eliminación
        confirmacion = QMessageBox.question(self, "Confirmar eliminación", 
                                           "¿Está seguro de eliminar esta asistencia?", 
                                           QMessageBox.Yes | QMessageBox.No)
        if confirmacion == QMessageBox.No:
            return
        
        # Obtener datos de la fila seleccionada
        codigo = self.tblAsistencias.item(fila_seleccionada, 0).text()
        fecha = self.tblAsistencias.item(fila_seleccionada, 4).text()
        
        # Eliminar asistencia
        if self.arregloAsistencias.eliminarAsistencia(codigo, fecha):
            self.arregloAsistencias.grabar()
            QMessageBox.information(self, "Éxito", "Asistencia eliminada correctamente")
            self.listarAsistencias()
        else:
            QMessageBox.warning(self, "Error", "No se pudo eliminar la asistencia")
    
    def limpiarCampos(self):
        self.txtCodigo.clear()
        self.txtDni.clear()
        self.txtApNom.clear()
        self.cboCurso.setCurrentIndex(0)
        self.dateFecha.setDate(datetime.now())
        self.cboEstado.setCurrentIndex(0)