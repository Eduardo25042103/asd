from PyQt5 import QtWidgets, uic
from Controlador.arregloAlumnos import ArregloAlumnos
from Controlador.alumnos import Alumno
import os

# Crear objeto de arreglo de alumnos
aAlum = ArregloAlumnos()

class VentanaReportes(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(VentanaReportes, self).__init__(parent)
        uic.loadUi("UI/ventanaReportes.ui", self)
        
        # Eventos de botones
        self.btnSalir.clicked.connect(self.close)
        self.btnBuscarDNI.clicked.connect(self.buscarPorDNI)
        self.btnBuscarCurso.clicked.connect(self.buscarPorCurso)
        self.btnBuscarCodigo.clicked.connect(self.buscarPorCodigo)
        self.btnListarTodos.clicked.connect(self.listarTodos)
        self.btnEstadisticas.clicked.connect(self.mostrarEstadisticas)
        self.btnExportar.clicked.connect(self.exportarReporte)
        self.btnLimpiar.clicked.connect(self.limpiarFiltros)
        
        # Conectar acciones del menú
        self.actionSalir.triggered.connect(self.close)
        self.actionListado_General.triggered.connect(self.listarTodos)
        self.actionPor_Curso.triggered.connect(self.buscarPorCurso)
        self.actionPor_Estado.triggered.connect(self.filtrarPorEstado)
        self.actionEstadisticas.triggered.connect(self.mostrarEstadisticas)
        self.actionExportar_a_PDF.triggered.connect(lambda: self.exportarReporte("pdf"))
        self.actionExportar_a_Excel.triggered.connect(lambda: self.exportarReporte("excel"))
        
        # Radio buttons para filtros
        self.rbTodos.toggled.connect(self.aplicarFiltros)
        self.rbAprobados.toggled.connect(self.aplicarFiltros)
        self.rbDesaprobados.toggled.connect(self.aplicarFiltros)
        
        # Cargar datos al iniciar
        self.listarTodos()
    
    def obtenerCodigo(self):
        return self.txtCodigo.text()
    
    def obtenerDNI(self):
        return self.txtDni.text()
    
    def obtenerCurso(self):
        return self.cboCurso.currentText()
    
    def limpiarTabla(self):
        self.tblReportes.clearContents()
        self.tblReportes.setRowCount(0)
    
    def limpiarFiltros(self):
        self.txtCodigo.clear()
        self.txtDni.clear()
        self.cboCurso.setCurrentIndex(0)
        self.rbTodos.setChecked(True)
        self.listarTodos()
    
    def listarTodos(self):
        self.limpiarTabla()
        self.tblReportes.setRowCount(aAlum.tamañoArregloAlumnos())
        
        for i in range(aAlum.tamañoArregloAlumnos()):
            alumno = aAlum.devolverAlumno(i)
            
            # Verificar si el alumno cumple con los filtros de estado
            if self.rbAprobados.isChecked() and alumno.Estado() != "Aprobado":
                continue
            if self.rbDesaprobados.isChecked() and alumno.Estado() != "Desaprobado":
                continue
            
            cursos = alumno.getCursoAlumno()
            
            self.tblReportes.setItem(i, 0, QtWidgets.QTableWidgetItem(alumno.getCodigoAlumno()))
            self.tblReportes.setItem(i, 1, QtWidgets.QTableWidgetItem(alumno.getDniAlumno()))
            self.tblReportes.setItem(i, 2, QtWidgets.QTableWidgetItem(alumno.getApNomAlumno()))
            self.tblReportes.setItem(i, 3, QtWidgets.QTableWidgetItem(cursos))
            
            # Calcular y mostrar promedio
            promedio = alumno.Promedio()
            if isinstance(promedio, float):
                self.tblReportes.setItem(i, 4, QtWidgets.QTableWidgetItem(str(promedio)))
            else:
                self.tblReportes.setItem(i, 4, QtWidgets.QTableWidgetItem(promedio))
            
            # Mostrar estado
            self.tblReportes.setItem(i, 5, QtWidgets.QTableWidgetItem(alumno.Estado()))
        
        # Ajustar tamaño de las columnas
        self.tblReportes.resizeColumnsToContents()
    
    def buscarPorDNI(self):
        self.limpiarTabla()
        dni = self.obtenerDNI()
        
        if dni == "":
            QtWidgets.QMessageBox.warning(self, "Buscar Alumno", 
                                         "Por favor ingrese un DNI para buscar", 
                                         QtWidgets.QMessageBox.Ok)
            return
        
        pos = aAlum.buscarAlumno(dni)
        
        if pos == -1:
            QtWidgets.QMessageBox.information(self, "Buscar Alumno", 
                                             "No se encontró ningún alumno con el DNI: " + dni, 
                                             QtWidgets.QMessageBox.Ok)
            return
        
        alumno = aAlum.devolverAlumno(pos)
        self.tblReportes.setRowCount(1)
        
        self.tblReportes.setItem(0, 0, QtWidgets.QTableWidgetItem(alumno.getCodigoAlumno()))
        self.tblReportes.setItem(0, 1, QtWidgets.QTableWidgetItem(alumno.getDniAlumno()))
        self.tblReportes.setItem(0, 2, QtWidgets.QTableWidgetItem(alumno.getApNomAlumno()))
        self.tblReportes.setItem(0, 3, QtWidgets.QTableWidgetItem(alumno.getCursoAlumno()))
        
        # Calcular y mostrar promedio
        promedio = alumno.Promedio()
        if isinstance(promedio, float):
            self.tblReportes.setItem(0, 4, QtWidgets.QTableWidgetItem(str(promedio)))
        else:
            self.tblReportes.setItem(0, 4, QtWidgets.QTableWidgetItem(promedio))
        
        # Mostrar estado
        self.tblReportes.setItem(0, 5, QtWidgets.QTableWidgetItem(alumno.Estado()))
        
        # Ajustar tamaño de las columnas
        self.tblReportes.resizeColumnsToContents()
    
    def buscarPorCodigo(self):
        self.limpiarTabla()
        codigo = self.obtenerCodigo()
        
        if codigo == "":
            QtWidgets.QMessageBox.warning(self, "Buscar Alumno", 
                                         "Por favor ingrese un código para buscar", 
                                         QtWidgets.QMessageBox.Ok)
            return
        
        pos = aAlum.buscarAlumnoPorCodigo(codigo)
        
        if pos == -1:
            QtWidgets.QMessageBox.information(self, "Buscar Alumno", 
                                             "No se encontró ningún alumno con el código: " + codigo, 
                                             QtWidgets.QMessageBox.Ok)
            return
        
        alumno = aAlum.devolverAlumno(pos)
        self.tblReportes.setRowCount(1)
        
        self.tblReportes.setItem(0, 0, QtWidgets.QTableWidgetItem(alumno.getCodigoAlumno()))
        self.tblReportes.setItem(0, 1, QtWidgets.QTableWidgetItem(alumno.getDniAlumno()))
        self.tblReportes.setItem(0, 2, QtWidgets.QTableWidgetItem(alumno.getApNomAlumno()))
        self.tblReportes.setItem(0, 3, QtWidgets.QTableWidgetItem(alumno.getCursoAlumno()))
        
        # Calcular y mostrar promedio
        promedio = alumno.Promedio()
        if isinstance(promedio, float):
            self.tblReportes.setItem(0, 4, QtWidgets.QTableWidgetItem(str(promedio)))
        else:
            self.tblReportes.setItem(0, 4, QtWidgets.QTableWidgetItem(promedio))
        
        # Mostrar estado
        self.tblReportes.setItem(0, 5, QtWidgets.QTableWidgetItem(alumno.Estado()))
        
        # Ajustar tamaño de las columnas
        self.tblReportes.resizeColumnsToContents()
    
    def buscarPorCurso(self):
        self.limpiarTabla()
        curso = self.obtenerCurso()
        
        if curso == "[Seleccionar]":
            QtWidgets.QMessageBox.warning(self, "Buscar Alumnos", 
                                         "Por favor seleccione un curso", 
                                         QtWidgets.QMessageBox.Ok)
            return
        
        posiciones = aAlum.buscarCurso(curso)
        
        if not posiciones:
            QtWidgets.QMessageBox.information(self, "Buscar Alumnos", 
                                             "No se encontraron alumnos en el curso: " + curso, 
                                             QtWidgets.QMessageBox.Ok)
            return
        
        self.tblReportes.setRowCount(len(posiciones))
        
        for fila, pos in enumerate(posiciones):
            alumno = aAlum.devolverAlumno(pos)
            
            # Verificar si el alumno cumple con los filtros de estado
            if self.rbAprobados.isChecked() and alumno.Estado() != "Aprobado":
                continue
            if self.rbDesaprobados.isChecked() and alumno.Estado() != "Desaprobado":
                continue
            
            self.tblReportes.setItem(fila, 0, QtWidgets.QTableWidgetItem(alumno.getCodigoAlumno()))
            self.tblReportes.setItem(fila, 1, QtWidgets.QTableWidgetItem(alumno.getDniAlumno()))
            self.tblReportes.setItem(fila, 2, QtWidgets.QTableWidgetItem(alumno.getApNomAlumno()))
            self.tblReportes.setItem(fila, 3, QtWidgets.QTableWidgetItem(alumno.getCursoAlumno()))
            
            # Calcular y mostrar promedio
            promedio = alumno.Promedio()
            if isinstance(promedio, float):
                self.tblReportes.setItem(fila, 4, QtWidgets.QTableWidgetItem(str(promedio)))
            else:
                self.tblReportes.setItem(fila, 4, QtWidgets.QTableWidgetItem(promedio))
            
            # Mostrar estado
            self.tblReportes.setItem(fila, 5, QtWidgets.QTableWidgetItem(alumno.Estado()))
        
        # Ajustar tamaño de las columnas
        self.tblReportes.resizeColumnsToContents()
    
    def aplicarFiltros(self):
        # Si hay búsqueda específica por DNI o código, no aplicar filtros
        if self.obtenerDNI() != "" or self.obtenerCodigo() != "":
            return
        
        # Si hay filtro por curso, aplicar sobre esa búsqueda
        if self.obtenerCurso() != "[Seleccionar]":
            self.buscarPorCurso()
        else:
            # Si no hay filtros específicos, aplicar a todos
            self.listarTodos()
    
    def filtrarPorEstado(self):
        estado, ok = QtWidgets.QInputDialog.getItem(self, "Filtrar por Estado",
                                                  "Seleccione el estado:",
                                                  ["Todos", "Aprobados", "Desaprobados"], 0, False)
        if ok:
            if estado == "Aprobados":
                self.rbAprobados.setChecked(True)
            elif estado == "Desaprobados":
                self.rbDesaprobados.setChecked(True)
            else:
                self.rbTodos.setChecked(True)
            
            self.aplicarFiltros()
    
    def mostrarEstadisticas(self):
        total_alumnos = aAlum.tamañoArregloAlumnos()
        aprobados = 0
        desaprobados = 0
        promedios = []
        
        for i in range(total_alumnos):
            alumno = aAlum.devolverAlumno(i)
            if alumno.Estado() == "Aprobado":
                aprobados += 1
            else:
                desaprobados += 1
            
            promedio = alumno.Promedio()
            if isinstance(promedio, float):
                promedios.append(promedio)
        
        #