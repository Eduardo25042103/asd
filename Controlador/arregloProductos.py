from Controlador.productos import producto
#MANTENIMIENTO

class ArregloProductos():

    #ATRIBUTOS
    dataProductos = [] # MOSTRAR BASE DATOS

    #CONSTRUCTOR
    def __init__(self):
        pass

    def adicionaProductos(self,objpro): #GUARDAR DATOS
        self.dataProductos.append(objpro)

    def devolverProducto(self, pos): #RETORNAR DATOS
        return self.dataProductos[pos]

    def tamañoArregloProducto(self): #DEVOLVER TAMAÑO
        return len(self.dataProductos)

    def buscarProducto(self, codproducto): #BUSCAR PRODUCTOS
        for i in range (self.tamañoArregloProducto()):
            if codproducto == self.dataProductos[i].getCodProducto():
                return i #REGRESAR A MISMA POSICIÓN
        return -1 #DATOS INEXISTENTES

    def eliminarProducto(self, pos): #ELIMINAR PRODUCTO
        del(self.dataProductos[pos])

    def modificarProducto(self, objpro, pos): #MODIFICAR DATOS PRODUCTO
        self.dataProductos[pos] = objpro

    def retornarDatos(self):
        return self.dataProductos  

    def grabar(self):
    #GUARDAR DATOS DE LISTA DATAPRODUCTO
        archivo = open("Modelo/Productos.txt", "w+", encoding="UTF-8")
        for i in range(self.tamañoArregloProducto()):
            archivo.write(str(self.devolverProducto(i).getCodProducto()) + ","
            + str(self.devolverProducto(i).getNombreProducto()) + ","
            + str(self.devolverProducto(i).getDescripcionProducto()) + ","
            + str(self.devolverProducto(i).getStockMinimo()) + ","
            + str(self.devolverProducto(i).getStockActual()) + ","
            + str(self.devolverProducto(i).getPrecioCosto()) + ","
            + str(self.devolverProducto(i).getPrecioVenta()) + ","
            + str(self.devolverProducto(i).getProveedor()) + ","
            + str(self.devolverProducto(i).getAlmacen()) + "\n")
        archivo.close()
    
    def cargar(self):
        #Carga los datos del archivo Productos.txt y los pasa a la lista dataProductos[]
        #con la finalidad de imprimir esos datos en la tabla.
        archivo = open("Modelo/Productos.txt", "r", encoding="UTF-8")
        for linea in archivo.readlines():
            columna = str(linea).split(",")
            codproducto = columna[0]
            nombre = columna[1]
            descripcion = columna[2]
            stockminimo = columna[3]
            stockactual = columna[4]
            preciocosto = columna[5]
            precioventa = columna[6]
            proveedor = columna[7]
            almacen = columna[8]
            objEmp = producto(codproducto, nombre, descripcion, 
                              stockminimo, stockactual, preciocosto,
                              precioventa, proveedor, almacen)
            self.adicionaProductos(objEmp)
        archivo.close()