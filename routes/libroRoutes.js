const express = require('express');
const router = express.Router();
const libroController = require('../controllers/libroController');


router.get('/', libroController.getAllBooks);

router.get('/nuevo', libroController.getNewBookForm);

router.post('/nuevo', libroController.createBook);

router.get('/editar/:id', libroController.getEditBookForm);

router.post('/editar/:id', libroController.updateBook);

router.get('/eliminar/:id', libroController.deleteBook);

module.exports = router;
