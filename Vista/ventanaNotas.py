from PyQt5 import QtWidgets, uic
from PyQt5 import QtGui
from Controlador.arregloAlumnos import ArregloAlumnos
from Controlador.arregloNotas import ArregloNotas
from Controlador.alumnos import Alumno

class VentanaNotas(QtWidgets.QMainWindow):
    def __init__(self, parent = None):
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
        
        # Cargar datos iniciales
        self.listar()
    
    # Método para listar que combine datos de alumnos y notas
    def listar(self):
        self.limpiarTabla()
        
        # Iterar por todos los alumnos
        for i in range(self.arregloAlumnos.tamañoArregloAlumnos()):
            alumno = self.arregloAlumnos.devolverAlumno(i)
            codigo = alumno.getCodigoAlumno()
            
            # Buscar notas del alumno
            index_nota = self.arregloNotas.buscarNotaPorCodigo(codigo)
            
            # Preparar datos para mostrar
            row = self.tblNotas.rowCount()
            self.tblNotas.insertRow(row)
            
            # Datos básicos del alumno
            self.tblNotas.setItem(row, 0, QtWidgets.QTableWidgetItem(codigo))
            self.tblNotas.setItem(row, 1, QtWidgets.QTableWidgetItem(alumno.getDniAlumno()))
            self.tblNotas.setItem(row, 2, QtWidgets.QTableWidgetItem(alumno.getApNomAlumno()))
            self.tblNotas.setItem(row, 3, QtWidgets.QTableWidgetItem(alumno.getCursoAlumno()))
            
            # Notas (si existen)
            if index_nota != -1:
                nota = self.arregloNotas.dataNotas[index_nota]
                ec1 = nota["ec1"]
                ec2 = nota["ec2"]
                ec3 = nota["ec3"]
                exf = nota["exf"]
                
                promedio = self.arregloNotas.calcularPromedio(ec1, ec2, ec3, exf)
                estado = self.arregloNotas.determinarEstado(promedio)
                
                self.tblNotas.setItem(row, 4, QtWidgets.QTableWidgetItem(ec1))
                self.tblNotas.setItem(row, 5, QtWidgets.QTableWidgetItem(ec2))
                self.tblNotas.setItem(row, 6, QtWidgets.QTableWidgetItem(ec3))
                self.tblNotas.setItem(row, 7, QtWidgets.QTableWidgetItem(exf))
                self.tblNotas.setItem(row, 8, QtWidgets.QTableWidgetItem(str(promedio)))
                self.tblNotas.setItem(row, 9, QtWidgets.QTableWidgetItem(estado))
            else:
                # No hay notas registradas
                self.tblNotas.setItem(row, 4, QtWidgets.QTableWidgetItem(""))
                self.tblNotas.setItem(row, 5, QtWidgets.QTableWidgetItem(""))
                self.tblNotas.setItem(row, 6, QtWidgets.QTableWidgetItem(""))
                self.tblNotas.setItem(row, 7, QtWidgets.QTableWidgetItem(""))
                self.tblNotas.setItem(row, 8, QtWidgets.QTableWidgetItem("Sin notas"))
                self.tblNotas.setItem(row, 9, QtWidgets.QTableWidgetItem("Sin notas"))
            
    def limpiarControles(self):
        self.txtCodigo.clear()
        self.txtDni.clear()
        self.txtApNom.clear()
        self.cboCurso.setCurrentIndex(0)
        self.txtEC1.clear()
        self.txtEC2.clear()
        self.txtEC3.clear()
        self.txtEF.clear()


    def registrar(self):
            if self.valida() == "":
                objAlumno= Alumno(self.obtenerCodigo(), self.obtenerDni(),
                                self.obtenerApNom(),
                                self.obtenerCurso(),
                                self.obtenerEC1(),
                                self.obtenerEC2(),
                                self.obtenerEC3(),
                                self.obtenerEF())
                dni=self.obtenerDni()
                curso=self.obtenerCurso()
                if aAlum.buscarAlumno(dni) == -1:
                    aAlum.adicionaAlumnos(objAlumno)
                    aAlum.grabar() 
                    self.limpiarControles()
                    self.listar()
                else:
                    if aAlum.buscarCurso(curso) != objAlumno.getCursoAlumno():
                        aAlum.adicionaAlumnos(objAlumno)
                        aAlum.grabar() 
                        self.limpiarControles()
                        self.listar()
                    else:
                        QtWidgets.QMessageBox.information(self, "Registrar Cliente",
                                                    "El DNI ingresado ya existe con el curso... !!!",
                                                    QtWidgets.QMessageBox.Ok)
            else:
                QtWidgets.QMessageBox.information(self, "Registrar Cliente",
                                                    "Error en " + self.valida(), QtWidgets.QMessageBox.Ok)
    
    def consultar(self):
        #self.limpiarTabla()
        if aAlum.tamañoArregloAlumnos() == 0:
                QtWidgets.QMessageBox.information(self, "Consultar Cliente",
                                                  "No existe clientes a consultar... !!!",
                                                  QtWidgets.QMessageBox.Ok)
        else:
            dni, _ = QtWidgets.QInputDialog.getText(self, "Consultar Cliente",
                                                  "Ingrese el DNI a consultar")
            index = aAlum.buscarAlumno(dni)
            if index == -1:
                QtWidgets.QMessageBox.information(self, "Consultar Cliente",
                                                  "El DNI ingresado no existe... !!!",
                                                  QtWidgets.QMessageBox.Ok)
            else:
                self.txtCodigo.setText(aAlum.devolverAlumno(index).getCodigoAlumno())
                self.txtDni.setText(aAlum.devolverAlumno(index).getDniAlumno())
                self.txtApNom.setText(aAlum.devolverAlumno(index).getApNomAlumno())
                word = aAlum.devolverAlumno(index).getCursoAlumno()
                pos = self.cboCurso.findText(word)
                self.cboCurso.setCurrentIndex(pos)
                self.txtEC1.setText(aAlum.devolverAlumno(index).getEC1Alumno())
                self.txtEC2.setText(aAlum.devolverAlumno(index).getEC2Alumno())
                self.txtEC2.setText(aAlum.devolverAlumno(index).getEC3Alumno())
                self.txtEF.setText(aAlum.devolverAlumno(index).getEXFAlumno())

               
    def eliminar(self):
        if self.obtenerDni() == "":
            QtWidgets.QMessageBox.information(self, "Consultar Cliente",
                                              "Por favor Consultar el Cliente...!!!",
                                               QtWidgets.QMessageBox.Ok)
        else:
            dni = self.txtDni.text()
            index = aAlum.buscarAlumno(dni)
            aAlum.eliminarAlumno(index)
            aAlum.grabar() 
            self.limpiarControles()
            self.listar()

    def quitar(self):
        if aAlum.tamañoArregloAlumnos() ==0:
            QtWidgets.QMessageBox.information(self, "Eliminar Cliente",
                                              "No existe clientes a eliminar... !!!",
                                              QtWidgets.QMessageBox.Ok)
        else:
            fila=self.tblNotas.selectedItems()
            if fila:
                indiceFila=fila[0].row()
                dni=self.tblNotas.item(indiceFila, 0).text()
                index =aAlum.buscarAlumno(dni)
                aAlum.eliminarAlumno(index)
                aAlum.grabar() 
                self.limpiarTabla()
                self.listar()
            else:
                QtWidgets.QMessageBox.information(self, "Eliminar Cliente",
                                                  "Debe seleccionar una fila... !!!",
                                                  QtWidgets.QMessageBox.Ok)

    def modificar(self):
        if aAlum.tamañoArregloAlumnos() == 0:
            QtWidgets.QMessageBox.information(self, "Modificar Cliente",
                                                  "No existen clientes a Modificar... !!!",
						                           QtWidgets.QMessageBox.Ok)
        else:
            dni= self.obtenerDni()
            index= aAlum.buscarAlumno(dni)
            if index != -1:
                objAlumno= Alumno(self.obtenerCodigo(), self.obtenerDni(),
                                self.obtenerApNom(),
                                self.obtenerCurso(),
                                self.obtenerEC1(),
                                self.obtenerEC2(),
                                self.obtenerEC3(),
                                self.obtenerEF())   
                aAlum.modificarAlumno(objAlumno, index)
                aAlum.grabar() 
                self.limpiarControles()
                self.listar()

