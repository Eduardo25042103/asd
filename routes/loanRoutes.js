const express = require('express');
const router = express.Router();
const loanController = require('../controllers/loanController');

// Middleware para verificar autenticación
const isAuthenticated = (req, res, next) => {
  if (req.session.user) {
    return next();
  }
  res.redirect('/login');
};

// Middleware para verificar si es administrador
const isAdmin = (req, res, next) => {
  if (req.session.user && req.session.user.role === 'admin') {
    return next();
  }
  res.status(403).send('Acceso denegado: se requiere rol de administrador');
};

// Rutas para préstamos
router.get('/', isAuthenticated, loanController.getAllLoans);
router.get('/nuevo', isAdmin, loanController.getNewLoanForm);
router.post('/nuevo', isAdmin, loanController.createLoan);
router.get('/editar/:id', isAdmin, loanController.getEditLoanForm);
router.post('/editar/:id', isAdmin, loanController.updateLoan);
router.get('/devolver/:id', isAuthenticated, loanController.returnBook);
router.get('/eliminar/:id', isAdmin, loanController.deleteLoan);

module.exports = router;