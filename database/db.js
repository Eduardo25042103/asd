const mysql = require('mysql');

// Configuración de la conexión a la base de datos
const connection = mysql.createConnection({
  host: 'localhost',
  user: 'root',         // Ajusta según tu configuración en XAMPP
  password: '',         // Pon tu password aquí si la tienes
  database: 'biblioteca'  // Asegúrate de haber creado esta BD
});

connection.connect((error) => {
  if (error) {
    console.error('Error de conexión a la base de datos:', error);
    process.exit(1);
  }
  console.log('Conexión a la base de datos exitosa.');
});

module.exports = connection;
