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

// Middleware para verificar si es un usuario normal (no admin)
const isUser = (req, res, next) => {
  if (req.session.user && req.session.user.role === 'user') {
    return next();
  }
  res.status(403).send('Acceso denegado: se requiere rol de usuario');
};

// Ruta principal de préstamos
router.get('/', isAuthenticated, loanController.getAllLoans);

// Aquí puedes añadir más rutas como crear préstamo, devolver libro, etc.

module.exports = router;