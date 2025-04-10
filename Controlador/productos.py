class producto():

    #ATRIBUTOS(ENCAPSULADOS)
    __CodProducto = ""; __NombreProducto = ""
    __DescripcionProducto = ""; __StockMinimo = ""
    __StockActual = ""; __PrecioCosto = ""
    __PrecioVenta = ""; __Proveedor = -1; __Almacen = -1

    #CONSTRUCTORES
    def __init__(self, codproducto, nombreproducto, descripcionproducto,
                 stockminimo, stockactual, preciocosto, precioventa,
                 proveedor, almacen):
        self.__CodProducto = codproducto
        self.__NombreProducto = nombreproducto
        self.__DescripcionProducto = descripcionproducto
        self.__StockMinimo = stockminimo 
        self.__StockActual = stockactual
        self.__PrecioCosto = preciocosto
        self.__PrecioVenta = precioventa
        self.__Proveedor = proveedor
        self.__Almacen = almacen

    #OBTENER Y ESTABLECER VALORES
    def getCodProducto(self):
        return self.__CodProducto
    def setCodProducto(self, codproducto):
        self.__CodProducto = codproducto
    def getNombreProducto(self):
        return self.__NombreProducto
    def setNombreProducto(self, nombreproducto):
        self.__NombreProducto = nombreproducto
    def getDescripcionProducto(self):
        return self.__DescripcionProducto
    def seDescripcionProducto(self, descripcionproducto):
        self.__DescripcionProducto = descripcionproducto
    def getStockMinimo(self):
        return self.__StockMinimo
    def setStockMinimo(self, stockminimo):
        self.__StockMinimo = stockminimo
    def getStockActual(self):
        return self.__StockActual
    def setStockActual(self, stockactual):
        self.__StockActual = stockactual
    def getPrecioCosto(self):
        return self.__PrecioCosto
    def setPrecioCosto(self, preciocosto):
        self.__PrecioCosto = preciocosto
    def getPrecioVenta(self):
        return self.__PrecioVenta
    def setPrecioVenta(self, precioventa):
        self.__PrecioVenta = precioventa
    def getProveedor(self):
        return str(self.__Proveedor)
    def setProveedor(self, proveedor):
        self.__Proveedor = str(proveedor)
    def getAlmacen(self):
        return str(self.__Almacen)
    def setAlmacen(self, almacen):
        self.__Almacen = str(almacen)