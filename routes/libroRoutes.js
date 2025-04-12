const express = require('express');
const router = express.Router();
const libroController = require('../controllers/libroController');

// Listar libros
router.get('/', libroController.getAllBooks);

// Mostrar formulario para nuevo libro
router.get('/nuevo', libroController.getNewBookForm);

// Crear libro
router.post('/nuevo', libroController.createBook);

// Mostrar formulario para editar libro
router.get('/editar/:id', libroController.getEditBookForm);

// Actualizar libro
router.post('/editar/:id', libroController.updateBook);

// Eliminar libro
router.get('/eliminar/:id', libroController.deleteBook);

module.exports = router;
