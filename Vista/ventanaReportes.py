from PyQt5 import QtWidgets, uic
from Controlador.arregloAlumnos import ArregloAlumnos
from Controlador.alumnos import Alumno
import os
from datetime import datetime

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
        # Eliminar o reemplazar los menús de exportación a PDF y Excel
        if hasattr(self, 'actionExportar_a_PDF'):
            self.actionExportar_a_PDF.triggered.connect(self.exportarReporte)
        if hasattr(self, 'actionExportar_a_Excel'):
            self.actionExportar_a_Excel.setText("Exportar a TXT")
            self.actionExportar_a_Excel.triggered.connect(self.exportarReporte)
        
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
        
        row_index = 0
        for i in range(aAlum.tamañoArregloAlumnos()):
            alumno = aAlum.devolverAlumno(i)
            
            # Verificar si el alumno cumple con los filtros de estado
            if self.rbAprobados.isChecked() and alumno.Estado() != "Aprobado":
                continue
            if self.rbDesaprobados.isChecked() and alumno.Estado() != "Desaprobado":
                continue
            
            cursos = alumno.getCursoAlumno()
            
            self.tblReportes.setItem(row_index, 0, QtWidgets.QTableWidgetItem(alumno.getCodigoAlumno()))
            self.tblReportes.setItem(row_index, 1, QtWidgets.QTableWidgetItem(alumno.getDniAlumno()))
            self.tblReportes.setItem(row_index, 2, QtWidgets.QTableWidgetItem(alumno.getApNomAlumno()))
            self.tblReportes.setItem(row_index, 3, QtWidgets.QTableWidgetItem(cursos))
            
            # Calcular y mostrar promedio
            promedio = alumno.Promedio()
            if isinstance(promedio, float):
                self.tblReportes.setItem(row_index, 4, QtWidgets.QTableWidgetItem(str(promedio)))
            else:
                self.tblReportes.setItem(row_index, 4, QtWidgets.QTableWidgetItem(promedio))
            
            # Mostrar estado
            self.tblReportes.setItem(row_index, 5, QtWidgets.QTableWidgetItem(alumno.Estado()))
            row_index += 1
        
        # Ajustar el número real de filas mostradas
        self.tblReportes.setRowCount(row_index)
        
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
        
        row_index = 0
        for pos in posiciones:
            alumno = aAlum.devolverAlumno(pos)
            
            # Verificar si el alumno cumple con los filtros de estado
            if self.rbAprobados.isChecked() and alumno.Estado() != "Aprobado":
                continue
            if self.rbDesaprobados.isChecked() and alumno.Estado() != "Desaprobado":
                continue
            
            self.tblReportes.setItem(row_index, 0, QtWidgets.QTableWidgetItem(alumno.getCodigoAlumno()))
            self.tblReportes.setItem(row_index, 1, QtWidgets.QTableWidgetItem(alumno.getDniAlumno()))
            self.tblReportes.setItem(row_index, 2, QtWidgets.QTableWidgetItem(alumno.getApNomAlumno()))
            self.tblReportes.setItem(row_index, 3, QtWidgets.QTableWidgetItem(alumno.getCursoAlumno()))
            
            # Calcular y mostrar promedio
            promedio = alumno.Promedio()
            if isinstance(promedio, float):
                self.tblReportes.setItem(row_index, 4, QtWidgets.QTableWidgetItem(str(promedio)))
            else:
                self.tblReportes.setItem(row_index, 4, QtWidgets.QTableWidgetItem(promedio))
            
            # Mostrar estado
            self.tblReportes.setItem(row_index, 5, QtWidgets.QTableWidgetItem(alumno.Estado()))
            row_index += 1
        
        # Ajustar el número real de filas mostradas
        self.tblReportes.setRowCount(row_index)
        
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
        cursos = {}
        
        for i in range(total_alumnos):
            alumno = aAlum.devolverAlumno(i)
            if alumno.Estado() == "Aprobado":
                aprobados += 1
            else:
                desaprobados += 1
            
            promedio = alumno.Promedio()
            if isinstance(promedio, float):
                promedios.append(promedio)
            
            # Contar alumnos por curso
            curso = alumno.getCursoAlumno()
            if curso in cursos:
                cursos[curso] += 1
            else:
                cursos[curso] = 1
        
        # Calcular estadísticas
        promedio_general = sum(promedios) / len(promedios) if promedios else 0
        porcentaje_aprobados = (aprobados / total_alumnos) * 100 if total_alumnos > 0 else 0
        porcentaje_desaprobados = (desaprobados / total_alumnos) * 100 if total_alumnos > 0 else 0
        
        # Crear mensaje con las estadísticas
        mensaje = f"Estadísticas del reporte:\n\n"
        mensaje += f"Total de alumnos: {total_alumnos}\n"
        mensaje += f"Alumnos aprobados: {aprobados} ({porcentaje_aprobados:.2f}%)\n"
        mensaje += f"Alumnos desaprobados: {desaprobados} ({porcentaje_desaprobados:.2f}%)\n"
        mensaje += f"Promedio general: {promedio_general:.2f}\n\n"
        
        mensaje += "Distribución por curso:\n"
        for curso, cantidad in cursos.items():
            mensaje += f"- {curso}: {cantidad} alumnos\n"
        
        # Mostrar estadísticas en un diálogo
        QtWidgets.QMessageBox.information(self, "Estadísticas", mensaje, QtWidgets.QMessageBox.Ok)
    
    def exportarReporte(self):
        # Verificar si hay datos para exportar
        if self.tblReportes.rowCount() == 0:
            QtWidgets.QMessageBox.warning(self, "Exportar Reporte", 
                                         "No hay datos para exportar.", 
                                         QtWidgets.QMessageBox.Ok)
            return
        
        # Generar nombre de archivo con fecha y hora
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        directorio = "Reportes"
        
        # Crear directorio si no existe
        if not os.path.exists(directorio):
            os.makedirs(directorio)
        
        # Exportar a archivo TXT
        filename = os.path.join(directorio, f"reporte_alumnos_{timestamp}.txt")
        
        try:
            with open(filename, 'w', encoding='utf-8') as archivo:
                # Escribir encabezado
                archivo.write("REPORTE DE ALUMNOS\n")
                archivo.write("=================\n\n")
                archivo.write(f"Fecha y hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
                
                # Obtener encabezados de la tabla
                headers = []
                for columna in range(self.tblReportes.columnCount()):
                    headers.append(self.tblReportes.horizontalHeaderItem(columna).text())
                
                # Escribir encabezados
                archivo.write(f"{headers[0]:<15} {headers[1]:<12} {headers[2]:<30} {headers[3]:<20} {headers[4]:<10} {headers[5]:<15}\n")
                archivo.write("-" * 100 + "\n")
                
                # Escribir datos
                for fila in range(self.tblReportes.rowCount()):
                    linea = ""
                    for columna in range(self.tblReportes.columnCount()):
                        item = self.tblReportes.item(fila, columna)
                        texto = item.text() if item else ""
                        
                        # Formatear cada columna según su tipo
                        if columna == 0:  # Código
                            linea += f"{texto:<15} "
                        elif columna == 1:  # DNI
                            linea += f"{texto:<12} "
                        elif columna == 2:  # Nombre
                            linea += f"{texto:<30} "
                        elif columna == 3:  # Curso
                            linea += f"{texto:<20} "
                        elif columna == 4:  # Promedio
                            linea += f"{texto:<10} "
                        elif columna == 5:  # Estado
                            linea += f"{texto:<15} "
                    
                    archivo.write(linea + "\n")
                
                # Agregar resumen al final
                archivo.write("\n\nRESUMEN DE DATOS\n")
                archivo.write("==============\n\n")
                
                # Calcular estadísticas
                total_alumnos = self.tblReportes.rowCount()
                aprobados = 0
                promedios = []
                
                for fila in range(total_alumnos):
                    estado = self.tblReportes.item(fila, 5).text() if self.tblReportes.item(fila, 5) else ""
                    if estado == "Aprobado":
                        aprobados += 1
                    
                    promedio_texto = self.tblReportes.item(fila, 4).text() if self.tblReportes.item(fila, 4) else ""
                    try:
                        promedio = float(promedio_texto)
                        promedios.append(promedio)
                    except ValueError:
                        pass
                
                promedio_general = sum(promedios) / len(promedios) if promedios else 0
                
                archivo.write(f"Total de alumnos en el reporte: {total_alumnos}\n")
                archivo.write(f"Alumnos aprobados: {aprobados}\n")
                archivo.write(f"Alumnos desaprobados: {total_alumnos - aprobados}\n")
                archivo.write(f"Promedio general: {promedio_general:.2f}\n")
                
            QtWidgets.QMessageBox.information(self, "Exportar Reporte", 
                                            f"Reporte exportado exitosamente a:\n{filename}", 
                                            QtWidgets.QMessageBox.Ok)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error al Exportar", 
                                         f"No se pudo exportar el reporte: {str(e)}", 
                                         QtWidgets.QMessageBox.Ok)