from PyQt5 import QtWidgets, uic
from PyQt5 import QtGui
from Controlador.arregloAlumnos import ArregloAlumnos
from Controlador.alumnos import Alumno

aAlum = ArregloAlumnos()

class VentanaNotas(QtWidgets.QMainWindow):
    def __init__(self, parent = None):
        super(VentanaNotas, self).__init__(parent)
        uic.loadUi("UI/ventanaNotas.ui", self)
        #self.show()

        #self.Carga_Clientes()
        self.btnRegistrar.clicked.connect(self.registrar)
        self.btnConsultar.clicked.connect(self.consultar)
        self.btnEliminar.clicked.connect(self.eliminar)
        self.btnListar.clicked.connect(self.listar)
        self.btnModificar.clicked.connect(self.modificar)
        self.btnQuitar.clicked.connect(self.quitar)
        
    def Carga_Alumnos(self):
        if aAlum.tamañoArregloAlumnos()==0:
            objAlumno= Alumno("")
            aAlum.adicionaAlumnos(objAlumno)
            self.listar()
        else:
            self.listar()

    def obtenerCodigo(self):
        return self.txtCodigo.text()
    
    def obtenerDni(self):
        return self.txtDni.text()
    
    def obtenerApNom(self):
        return self.txtApNom.text()
    
    def obtenerCurso(self):
        print(self.cboCurso.currentText())
        return self.cboCurso.currentText()

    def obtenerEC1(self):
        return self.txtEC1.text()

    def obtenerEC2(self):
        return self.txtEC2.text()

    def obtenerEC3(self):
        return self.txtEC3.text()

    def obtenerEF(self):
        return self.txtEF.text()

    def limpiarTabla(self):
        self.tblNotas.clearContents()
        self.tblNotas.setRowCount(0)

    def valida(self):
        if self.txtCodigo.text() =="":
            self.txtCodigo.setFocus()
            return "Codigo del alumno...!!!"
        elif self.txtDni.text() =="":
            self.txtDni.setFocus()
            return "DNI del alumno...!!!"
        elif self.txtApNom.text()=="":
            self.txtApNom.setFocus()
            return "Apellidos y Nombres del alumno...!!!"
        elif self.cboCurso.currentIndex() == 0:
            self.cboCurso.setFocus()
            return "Curso del alumno...!!!"
        elif self.txtEC1.text()=="":
            self.txtEC1.setFocus()
            return "EC1 del alumno...!!!"
        elif self.txtEC2.text()=="":
            self.txtEC2.setFocus()
            return "EC2 del alumno...!!!"
        elif self.txtEC3.text()=="":
            self.txtEC3.setFocus()
            return "EC3 del alumno...!!!"
        elif self.txtEF.text()=="":
            self.txtEF.setFocus()
            return "EF del alumno...!!!"
        else:
            return ""

    def listar(self):
        self.tblNotas.setRowCount(aAlum.tamañoArregloAlumnos())
        self.tblNotas.setColumnCount(10)
        self.tblNotas.verticalHeader().setVisible(False)
        for i in range (0, aAlum.tamañoArregloAlumnos()):
            self.tblNotas.setItem(i, 0, QtWidgets.QTableWidgetItem(aAlum.devolverAlumno(i).getCodigoAlumno()))
            self.tblNotas.setItem(i, 1, QtWidgets.QTableWidgetItem(aAlum.devolverAlumno(i).getDniAlumno()))
            self.tblNotas.setItem(i, 2, QtWidgets.QTableWidgetItem(aAlum.devolverAlumno(i).getApNomAlumno()))
            self.tblNotas.setItem(i, 3, QtWidgets.QTableWidgetItem(aAlum.devolverAlumno(i).getCursoAlumno()))
            self.tblNotas.setItem(i, 4, QtWidgets.QTableWidgetItem(aAlum.devolverAlumno(i).getEC1Alumno()))
            self.tblNotas.setItem(i, 5, QtWidgets.QTableWidgetItem(aAlum.devolverAlumno(i).getEC2Alumno()))
            self.tblNotas.setItem(i, 6, QtWidgets.QTableWidgetItem(aAlum.devolverAlumno(i).getEC3Alumno()))
            self.tblNotas.setItem(i, 7, QtWidgets.QTableWidgetItem(aAlum.devolverAlumno(i).getEXFAlumno()))
            self.tblNotas.setItem(i, 8, QtWidgets.QTableWidgetItem(str(aAlum.devolverAlumno(i).Promedio())))
            self.tblNotas.setItem(i, 9, QtWidgets.QTableWidgetItem(aAlum.devolverAlumno(i).Estado()))

            
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

