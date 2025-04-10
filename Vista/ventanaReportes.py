from PyQt5 import QtWidgets, uic
from Controlador.arregloProductos import ArregloProductos
from Controlador.productos import producto

#CREAR OBJETO APRO
aPro = ArregloProductos()

class VentanaProductos(QtWidgets.QMainWindow):
    def __init__(self, parent = None):
        super(VentanaProductos,self).__init__(parent)
        uic.loadUi("UI/ventanaProductos.ui", self)
        #self.show()
    
        #Eventos
        #self.Carga_Productoss()
        self.btnRegistrar.clicked.connect(self.registrar)
        self.btnConsultar.clicked.connect(self.consultar)
        self.btnEliminar.clicked.connect(self.eliminar)
        self.btnListar.clicked.connect(self.listar)
        self.btnModificar.clicked.connect(self.modificar)
        self.btnQuitar.clicked.connect(self.quitar)
        
#es necesario tener algunos métodos a partir de aqui
    def Carga_Productos(self):
        if aPro.tamañoArregloProducto()==0:
            objCli= producto("")
            aPro.adicionaProductos(objCli)
            self.listar()
        else:
            self.listar()

    def obtenerCodigo(self):
        return self.txtCodigo.text()
    
    def obtenerNombres(self):
        return self.txtNombre.text()

    def obtenerDescripcion(self):
        return self.txtDescripcion.text()

    def obtenerStockMinimo(self):
        return self.txtStockMinimo.text()

    def obtenerStockActual(self):
        return self.txtStockActual.text()

    def obtenerPrecioCosto(self):
        return self.txtPrecioCosto.text()
    
    def obtenerPrecioVenta(self):
        return self.txtPrecioVenta.text()
    
    def obtenerProveedor(self):
        return self.cboProveedor.currentText()
    
    def obtenerAlmacen(self):
        return self.cboAlmacen.currentText()

    def limpiarTabla(self):
        self.tblProductos.clearContents()
        self.tblProductos.setRowCount(0)

    def valida(self):
        if self.txtCodigo.text() =="":
            self.txtCodigo.setfocus()
            return "Codigo del Productos...!!!"
        elif self.txtNombre.text()=="":
            self.txtNombre.setfocus()
            return "Nombre del Producto...!!!"
        elif self.txtDescripcion.text()=="":
            self.txtDescripcion.setfocus()
            return "Descripcion del Producto...!!!"
        elif self.txtStockMinimo.text()=="":
            self.txtStockMinimo.setfocus()
            return "Stock Minimo del Producto...!!!"
        elif self.txtStockActual.text()=="":
            self.txtStockActual.setfocus()
            return "Stock Actual del Producto...!!!"
        elif self.txtPrecioCosto.text()=="":
            self.txtPrecioCosto.setfocus()
            return "Precio Costo del Producto...!!!"
        elif self.txtPrecioVenta.text()=="":
            self.txtPrecioVenta.setfocus()
            return "Precio Venta del Producto...!!!"
        elif self.cboProveedor.currentText()=="":
            self.cboProveedor.setfocus()
            return "Proveedor del producto...!!!"
        elif self.cboAlmacen.currentText()=="":
            self.cboAlmacen.setfocus()
            return "Proveedor del producto...!!!"
        else:
            return ""

    def listar(self):
        self.tblProductos.setRowCount(aPro.tamañoArregloProducto())
        self.tblProductos.setColumnCount(9)
        #Cabecera
        self.tblProductos.verticalHeader().setVisible(False)
        for i in range (0, aPro.tamañoArregloProducto()):
            self.tblProductos.setItem(i, 0, QtWidgets.QTableWidgetItem(aPro.devolverProducto(i).getCodProducto()))
            self.tblProductos.setItem(i, 1, QtWidgets.QTableWidgetItem(aPro.devolverProducto(i).getNombreProducto()))
            self.tblProductos.setItem(i, 2, QtWidgets.QTableWidgetItem(aPro.devolverProducto(i).getDescripcionProducto()))
            self.tblProductos.setItem(i, 3, QtWidgets.QTableWidgetItem(aPro.devolverProducto(i).getStockMinimo()))
            self.tblProductos.setItem(i, 4, QtWidgets.QTableWidgetItem(aPro.devolverProducto(i).getStockActual()))
            self.tblProductos.setItem(i, 5, QtWidgets.QTableWidgetItem(aPro.devolverProducto(i).getPrecioCosto()))
            self.tblProductos.setItem(i, 6, QtWidgets.QTableWidgetItem(aPro.devolverProducto(i).getPrecioVenta()))
            self.tblProductos.setItem(i, 7, QtWidgets.QTableWidgetItem(aPro.devolverProducto(i).getProveedor()))
            self.tblProductos.setItem(i, 8, QtWidgets.QTableWidgetItem(aPro.devolverProducto(i).getAlmacen()))

    def limpiarControles(self):
        self.txtCodigo.clear()
        self.txtNombre.clear()
        self.txtDescripcion.clear()
        self.txtStockMinimo.clear()
        self.txtStockActual.clear()
        self.txtPrecioCosto.clear()
        self.txtPrecioVenta.clear()
        self.cboProveedor.setCurrentIndex(0)
        self.cboAlmacen.setCurrentIndex(0)
        #Mantenimiento (Grabar, Registrar, Consultar, Modificar, Listar y Quitar)
    
#Grabar datos
    def registrar(self):
            if self.valida() == "":
                objCli= producto(self.obtenerCodigo(), self.obtenerNombres(),
                                self.obtenerDescripcion(), self.obtenerStockMinimo(),
                                self.obtenerStockActual(), self.obtenerPrecioCosto(),
                                self.obtenerPrecioVenta(), self.obtenerProveedor(),
                                self.obtenerAlmacen())
                codigo=self.obtenerCodigo()
                if aPro.buscarProducto(codigo) == -1:
                    aPro.adicionaProductos(objCli)
                    aPro.grabar() #--> los datos ya se están grabando en los archivos
                    self.limpiarControles()
                    self.listar()
                else:
                    QtWidgets.QMessageBox.information(self, "Registrar Productos",
                                                    "El codigo ingresado ya existe... !!!",
                                                    QtWidgets.QMessageBox.Ok)
            else:
                QtWidgets.QMessageBox.information(self, "Registrar Productos",
                                                    "Error en " + self.valida(), QtWidgets.QMessageBox.Ok)
    
    def consultar(self):
        #self.limpiarTabla()
        if aPro.tamañoArregloProducto() == 0:
                QtWidgets.QMessageBox.information(self, "Consultar Productos",
                                                  "No existe Productoss a consultar... !!!",
                                                  QtWidgets.QMessageBox.Ok)
        else:
            codigo, _ = QtWidgets.QInputDialog.getText(self, "Consultar Productos",
                                                  "Ingrese el codigo a consultar")
            pos = aPro.buscarProducto(codigo)
            if pos == -1:
                QtWidgets.QMessageBox.information(self, "Consultar Productos",
                                                  "El codigo ingresado no existe... !!!",
                                                  QtWidgets.QMessageBox.Ok)
            else:
                self.txtCodigo.setText(aPro.devolverProducto(pos).getCodProducto())
                self.txtNombre.setText(aPro.devolverProducto(pos).getNombreProducto())
                self.txtDescripcion.setText(aPro.devolverProducto(pos).getDescripcionProducto())
                self.txtStockMinimo.setText(aPro.devolverProducto(pos).getStockMinimo())
                self.txtStockActual.setText(aPro.devolverProducto(pos).getStockActual())
                self.txtPrecioCosto.setText(aPro.devolverProducto(pos).getPrecioCosto())
                self.txtPrecioVenta.setText(aPro.devolverProducto(pos).getPrecioVenta())
                self.cboProveedor.setCurrentText(aPro.devolverProducto(pos).getProveedor())
                self.cboAlmacen.setCurrentText(aPro.devolverProducto(pos).getAlmacen())
                
               #self.tblProductos.setRowCount(1)
               #self.tblProductos.setItem(0,0, QtWidgets.QTableWidgetItem(aPro.devolverProducto(pos).getCodProducto()))
               #self.tblProductos.setItem(0,1, QtWidgets.QTableWidgetItem(aPro.devolverProducto(pos).getNombreProducto()))
               #self.tblProductos.setItem(0,2, QtWidgets.QTableWidgetItem(aPro.devolverProducto(pos).getDescripcionProducto()))
               #self.tblProductos.setItem(0,3, QtWidgets.QTableWidgetItem(aPro.devolverProducto(pos).getStockMinimo()))
               #self.tblProductos.setItem(0,4, QtWidgets.QTableWidgetItem(aPro.devolverProducto(pos).getStockActual()))
               #self.tblProductos.setItem(0,5, QtWidgets.QTableWidgetItem(aPro.devolverProducto(pos).getPrecioCosto()))

#Eliminar datos
    def eliminar(self):
        if self.obtenerCodigo() == "":
            QtWidgets.QMessageBox.information(self, "Consultar Productos",
                                              "Por favor Consultar el Productos...!!!",
                                               QtWidgets.QMessageBox.Ok)
        else:
            codigo = self.txtCodigo.text()
            pos = aPro.buscarProducto(codigo)
            aPro.eliminarProducto(pos)
            aPro.grabar() #--> los datos ya se están grabando en el archivo
            self.limpiarControles()
            self.listar()

#Quitar datos
    def quitar(self):
        if aPro.tamañoArregloProducto() ==0:
            QtWidgets.QMessageBox.information(self, "Eliminar Productos",
                                              "No existe Productoss a eliminar... !!!",
                                              QtWidgets.QMessageBox.Ok)
        else:
            fila=self.tblProductos.selectedItems()
            if fila:
                indiceFila=fila[0].row()
                codigo=self.tblProductos.item(indiceFila, 0).text()
                pos =aPro.buscarProducto(codigo)
                aPro.eliminarProducto(pos)
                aPro.grabar() #--> los datos ya se están grabando en el archivo
                self.limpiarTabla()
                self.listar()
            else:
                QtWidgets.QMessageBox.information(self, "Eliminar Productos",
                                                  "Debe seleccionar una fila... !!!",
                                                  QtWidgets.QMessageBox.Ok)

#Modificar datos         
    def modificar(self):
        if aPro.tamañoArregloProducto() == 0:
            QtWidgets.QMessageBox.information(self, "Modificar Productos",
                                                  "No existen Productoss a Modificar... !!!",
						                           QtWidgets.QMessageBox.Ok)
        else:
            codigo= self.obtenerCodigo()
            pos = aPro.buscarProducto(codigo)
            if pos != -1:
                objCli= producto(self.obtenerCodigo(), self.obtenerNombres(),
                                 self.obtenerDescripcion(),
                                 self.obtenerStockMinimo(),
                                 self.obtenerStockActual(),
                                 self.obtenerPrecioCosto(), self.obtenerPrecioVenta())
                aPro.modificarProducto(objCli, pos)
                aPro.grabar() #--> los datos ya se están grabando en el archivo
                self.limpiarControles()
                self.listar()