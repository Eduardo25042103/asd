from PyQt5 import QtWidgets, uic
from PyQt5 import QtGui
from Vista.ventanaNotas import VentanaNotas
from Vista.ventanaAsistencias import VentanaAsistencias
from Vista.ventanaRegistroAlumnos import VentanaRegistroAlumnos


class VentanaPrincipal(QtWidgets.QMainWindow):
    def __init__(self, parent = None):
        super(VentanaPrincipal,self).__init__(parent)
        uic.loadUi("UI/ventanaPrincipal.ui", self)
        #self.show()

    #EVENTOS     
        self.btnNotas.clicked.connect(self.abrirVentanaNotas)
        self.btnAsistencias.clicked.connect(self.abrirVentanaAsistencias)
        self.btnRegistroAlumnos.clicked.connect(self.abrirVentanaRegistroAlumnos)
        self.btnSalir.clicked.connect(self.cerrar)


    def abrirVentanaNotas(self):
        vnotas = VentanaNotas(self)
        vnotas.show()

    def abrirVentanaAsistencias(self):
        vasistencias = VentanaAsistencias(self)
        vasistencias.show()
    def abrirVentanaRegistroAlumnos(self):
        vregistros = VentanaRegistroAlumnos(self)
        vregistros.show()

    def abrirVentanaReportes(self):
      print()

    def cerrar(self):
        self.close()


