from PyQt5 import QtWidgets, uic
from Vista.ventanaPrincipal import VentanaPrincipal

class Login(QtWidgets.QMainWindow):

    contador = 0 
    def __init__(self, parent = None):
        super(Login, self).__init__(parent)
        uic.loadUi("UI/login.ui", self)
        self.show()
    
    #EVENTOS

        self.btnIniciar.clicked.connect(self.iniciarSesion)

    def iniciarSesion(self):
        usuario = self.txtUsuario.text().lower()
        contraseña = self.txtPassword.text()
        if usuario == "1" and contraseña == "2":
            self.close()
            v_principal = VentanaPrincipal(self)
            v_principal.show()
        else:
            self.contador += 1 
            QtWidgets.QMessageBox.information(self, "Error de intento",
                                                f"Intento Nro {str(self.contador)}",
                                                QtWidgets.QMessageBox.Ok)
        
        if self.contador == 3:
            QtWidgets.QMessageBox.information(self, "Salida del sistema", 
                                                "Lo sentimos has agotado tus 3 intentos", 
                                                QtWidgets.QMessageBox.Ok)
            self.close()