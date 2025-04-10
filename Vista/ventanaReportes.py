from PyQt5 import QtWidgets, uic
from Controlador.arregloAlumnos import ArregloAlumnos
from Controlador.arregloNotas import ArregloNotas
from Controlador.alumnos import Alumno
import os
from datetime import datetime

# Crear objetos de arreglos
aAlum = ArregloAlumnos()
aNotas = ArregloNotas()

class VentanaReportes(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(VentanaReportes, self).__init__(parent)
        uic.loadUi("UI/ventanaReportes.ui", self)
        
        # Configurar el combobox de cursos igual que en ventanaNotas
        self.cboCurso.clear()
        self.cboCurso.addItem("[Seleccionar]")
        self.cboCurso.addItems(["Matemáticas", "Física", "Química", "Programación", "Base de Datos", "Inglés"])
        
        # Eventos de botones
        self.btnSalir.clicked.connect(self.close)
        self.btnBuscarDNI.clicked.connect(self.buscarPorDNI)
        self.btnBuscarCurso.clicked.connect(self.buscarPorCurso)
        self.btnBuscarCodigo.clicked.connect(self.buscarPorCodigo)
        self.btnListarTodos.clicked.connect(self.listarTodos)
        # Simplificación: remover estadísticas avanzadas
        self.btnEstadisticas.clicked.connect(self.mostrarEstadisticasSimples)
        self.btnExportar.clicked.connect(self.exportarReporte)
        self.btnLimpiar.clicked.connect(self.limpiarFiltros)
        
        # Conectar acciones del menú
        self.actionSalir.triggered.connect(self.close)
        self.actionListado_General.triggered.connect(self.listarTodos)
        self.actionPor_Curso.triggered.connect(self.buscarPorCurso)
        self.actionPor_Estado.triggered.connect(self.filtrarPorEstado)
        self.actionEstadisticas.triggered.connect(self.mostrarEstadisticasSimples)
        
        # Mantener solo la exportación a TXT
        if hasattr(self, 'actionExportar_a_PDF'):
            self.actionExportar_a_PDF.setText("Exportar a TXT")
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
    
    def obtenerPromedioActualizado(self, alumno):
        """Método para obtener el promedio actualizado del alumno"""
        codigo = alumno.getCodigoAlumno()
        index_nota = aNotas.buscarNotaPorCodigo(codigo)
        
        if index_nota != -1:
            # Si hay notas registradas, calcular el promedio con los datos actualizados
            nota_data = aNotas.dataNotas[index_nota]
            notas = [
                float(nota_data.get("nota1", 0)),
                float(nota_data.get("nota2", 0)),
                float(nota_data.get("nota3", 0)),
                float(nota_data.get("nota4", 0))
            ]
            # Filtrar notas que son cero (no registradas)
            notas_validas = [n for n in notas if n > 0]
            if notas_validas:
                return sum(notas_validas) / len(notas_validas)
            else:
                return "Sin notas"
        else:
            # Si no hay notas registradas, usar el método del alumno
            promedio = alumno.Promedio()
            return promedio
    
    def obtenerEstadoActualizado(self, promedio):
        """Método para obtener el estado basado en el promedio actualizado"""
        if isinstance(promedio, str):
            return "Pendiente"
        
        return "Aprobado" if promedio >= 11 else "Desaprobado"
    
    def listarTodos(self):
        self.limpiarTabla()
        self.tblReportes.setRowCount(aAlum.tamañoArregloAlumnos())
        
        row_index = 0
        for i in range(aAlum.tamañoArregloAlumnos()):
            alumno = aAlum.devolverAlumno(i)
            codigo = alumno.getCodigoAlumno()
            
            # Obtener promedio actualizado
            promedio = self.obtenerPromedioActualizado(alumno)
            estado = self.obtenerEstadoActualizado(promedio)
            
            # Verificar si el alumno cumple con los filtros de estado
            if self.rbAprobados.isChecked() and estado != "Aprobado":
                continue
            if self.rbDesaprobados.isChecked() and estado != "Desaprobado":
                continue
            
            # Obtener curso desde notas si existe, sino del alumno
            index_nota = aNotas.buscarNotaPorCodigo(codigo)
            if index_nota != -1:
                curso = aNotas.dataNotas[index_nota].get("curso", alumno.getCursoAlumno())
            else:
                curso = alumno.getCursoAlumno()
            
            self.tblReportes.setItem(row_index, 0, QtWidgets.QTableWidgetItem(codigo))
            self.tblReportes.setItem(row_index, 1, QtWidgets.QTableWidgetItem(alumno.getDniAlumno()))
            self.tblReportes.setItem(row_index, 2, QtWidgets.QTableWidgetItem(alumno.getApNomAlumno()))
            self.tblReportes.setItem(row_index, 3, QtWidgets.QTableWidgetItem(curso))
            
            # Mostrar promedio actualizado
            if isinstance(promedio, float):
                self.tblReportes.setItem(row_index, 4, QtWidgets.QTableWidgetItem(f"{promedio:.2f}"))
            else:
                self.tblReportes.setItem(row_index, 4, QtWidgets.QTableWidgetItem(str(promedio)))
            
            # Mostrar estado actualizado
            self.tblReportes.setItem(row_index, 5, QtWidgets.QTableWidgetItem(estado))
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
        codigo = alumno.getCodigoAlumno()
        self.tblReportes.setRowCount(1)
        
        # Obtener curso desde notas si existe, sino del alumno
        index_nota = aNotas.buscarNotaPorCodigo(codigo)
        if index_nota != -1:
            curso = aNotas.dataNotas[index_nota].get("curso", alumno.getCursoAlumno())
        else:
            curso = alumno.getCursoAlumno()
        
        # Obtener promedio actualizado
        promedio = self.obtenerPromedioActualizado(alumno)
        estado = self.obtenerEstadoActualizado(promedio)
        
        self.tblReportes.setItem(0, 0, QtWidgets.QTableWidgetItem(codigo))
        self.tblReportes.setItem(0, 1, QtWidgets.QTableWidgetItem(alumno.getDniAlumno()))
        self.tblReportes.setItem(0, 2, QtWidgets.QTableWidgetItem(alumno.getApNomAlumno()))
        self.tblReportes.setItem(0, 3, QtWidgets.QTableWidgetItem(curso))
        
        # Mostrar promedio actualizado
        if isinstance(promedio, float):
            self.tblReportes.setItem(0, 4, QtWidgets.QTableWidgetItem(f"{promedio:.2f}"))
        else:
            self.tblReportes.setItem(0, 4, QtWidgets.QTableWidgetItem(str(promedio)))
        
        # Mostrar estado actualizado
        self.tblReportes.setItem(0, 5, QtWidgets.QTableWidgetItem(estado))
        
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
        
        # Obtener curso desde notas si existe, sino del alumno
        index_nota = aNotas.buscarNotaPorCodigo(codigo)
        if index_nota != -1:
            curso = aNotas.dataNotas[index_nota].get("curso", alumno.getCursoAlumno())
        else:
            curso = alumno.getCursoAlumno()
        
        # Obtener promedio actualizado
        promedio = self.obtenerPromedioActualizado(alumno)
        estado = self.obtenerEstadoActualizado(promedio)
        
        self.tblReportes.setItem(0, 0, QtWidgets.QTableWidgetItem(codigo))
        self.tblReportes.setItem(0, 1, QtWidgets.QTableWidgetItem(alumno.getDniAlumno()))
        self.tblReportes.setItem(0, 2, QtWidgets.QTableWidgetItem(alumno.getApNomAlumno()))
        self.tblReportes.setItem(0, 3, QtWidgets.QTableWidgetItem(curso))
        
        # Mostrar promedio actualizado
        if isinstance(promedio, float):
            self.tblReportes.setItem(0, 4, QtWidgets.QTableWidgetItem(f"{promedio:.2f}"))
        else:
            self.tblReportes.setItem(0, 4, QtWidgets.QTableWidgetItem(str(promedio)))
        
        # Mostrar estado actualizado
        self.tblReportes.setItem(0, 5, QtWidgets.QTableWidgetItem(estado))
        
        # Ajustar tamaño de las columnas
        self.tblReportes.resizeColumnsToContents()
    
    def buscarPorCurso(self):
        self.limpiarTabla()
        curso_seleccionado = self.obtenerCurso()
        
        if curso_seleccionado == "[Seleccionar]":
            QtWidgets.QMessageBox.warning(self, "Buscar Alumnos", 
                                         "Por favor seleccione un curso", 
                                         QtWidgets.QMessageBox.Ok)
            return
        
        # Buscar primero en notas (como en ventanaNotas)
        alumnos_por_curso = []
        codigos_encontrados = set()
        
        # Buscar en notas para encontrar alumnos por curso
        for nota in aNotas.dataNotas:
            if nota.get("curso") == curso_seleccionado:
                codigo = nota["codigo"]
                index_alumno = aAlum.buscarAlumnoPorCodigo(codigo)
                if index_alumno != -1 and codigo not in codigos_encontrados:
                    alumnos_por_curso.append(index_alumno)
                    codigos_encontrados.add(codigo)
        
        # Buscar en alumnos para asegurar completitud (para retrocompatibilidad)
        posiciones_adicionales = aAlum.buscarCurso(curso_seleccionado)
        for pos in posiciones_adicionales:
            alumno = aAlum.devolverAlumno(pos)
            if alumno.getCodigoAlumno() not in codigos_encontrados:
                alumnos_por_curso.append(pos)
                codigos_encontrados.add(alumno.getCodigoAlumno())
        
        if not alumnos_por_curso:
            QtWidgets.QMessageBox.information(self, "Buscar Alumnos", 
                                             "No se encontraron alumnos en el curso: " + curso_seleccionado, 
                                             QtWidgets.QMessageBox.Ok)
            return
        
        self.tblReportes.setRowCount(len(alumnos_por_curso))
        
        row_index = 0
        for pos in alumnos_por_curso:
            alumno = aAlum.devolverAlumno(pos)
            codigo = alumno.getCodigoAlumno()
            
            # Obtener promedio actualizado
            promedio = self.obtenerPromedioActualizado(alumno)
            estado = self.obtenerEstadoActualizado(promedio)
            
            # Verificar si el alumno cumple con los filtros de estado
            if self.rbAprobados.isChecked() and estado != "Aprobado":
                continue
            if self.rbDesaprobados.isChecked() and estado != "Desaprobado":
                continue
            
            self.tblReportes.setItem(row_index, 0, QtWidgets.QTableWidgetItem(codigo))
            self.tblReportes.setItem(row_index, 1, QtWidgets.QTableWidgetItem(alumno.getDniAlumno()))
            self.tblReportes.setItem(row_index, 2, QtWidgets.QTableWidgetItem(alumno.getApNomAlumno()))
            self.tblReportes.setItem(row_index, 3, QtWidgets.QTableWidgetItem(curso_seleccionado))
            
            # Mostrar promedio actualizado
            if isinstance(promedio, float):
                self.tblReportes.setItem(row_index, 4, QtWidgets.QTableWidgetItem(f"{promedio:.2f}"))
            else:
                self.tblReportes.setItem(row_index, 4, QtWidgets.QTableWidgetItem(str(promedio)))
            
            # Mostrar estado actualizado
            self.tblReportes.setItem(row_index, 5, QtWidgets.QTableWidgetItem(estado))
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
    
    def mostrarEstadisticasSimples(self):
        """Versión simplificada de estadísticas"""
        total_alumnos = self.tblReportes.rowCount()
        aprobados = 0
        
        for fila in range(total_alumnos):
            estado = self.tblReportes.item(fila, 5).text() if self.tblReportes.item(fila, 5) else ""
            if estado == "Aprobado":
                aprobados += 1
        
        # Mensaje simple con solo lo básico
        mensaje = f"Resumen de alumnos:\n\n"
        mensaje += f"Total de alumnos: {total_alumnos}\n"
        mensaje += f"Alumnos aprobados: {aprobados}\n"
        mensaje += f"Alumnos desaprobados: {total_alumnos - aprobados}\n"
        
        # Mostrar estadísticas en un diálogo
        QtWidgets.QMessageBox.information(self, "Estadísticas Básicas", mensaje, QtWidgets.QMessageBox.Ok)
    
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
                
                # Agregar resumen básico al final
                archivo.write("\n\nRESUMEN\n")
                archivo.write("=======\n\n")
                
                total_alumnos = self.tblReportes.rowCount()
                aprobados = 0
                for fila in range(total_alumnos):
                    estado = self.tblReportes.item(fila, 5).text() if self.tblReportes.item(fila, 5) else ""
                    if estado == "Aprobado":
                        aprobados += 1
                
                archivo.write(f"Total de alumnos: {total_alumnos}\n")
                archivo.write(f"Alumnos aprobados: {aprobados}\n")
                archivo.write(f"Alumnos desaprobados: {total_alumnos - aprobados}\n")
                
            QtWidgets.QMessageBox.information(self, "Exportar Reporte", 
                                            f"Reporte exportado exitosamente a:\n{filename}", 
                                            QtWidgets.QMessageBox.Ok)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error al Exportar", 
                                         f"No se pudo exportar el reporte: {str(e)}", 
                                         QtWidgets.QMessageBox.Ok)