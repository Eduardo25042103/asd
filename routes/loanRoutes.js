const express = require('express');
const router = express.Router();
const loanController = require('../controllers/loanController');

const isAuthenticated = (req, res, next) => {
  if (req.session.user) {
    return next();
  }
  res.redirect('/login');
};

router.get('/', isAuthenticated, loanController.getAllLoans);
router.get('/nuevo', isAuthenticated, loanController.getNewLoanForm);
router.post('/nuevo', isAuthenticated, loanController.createLoan);
router.get('/editar/:id', isAuthenticated, loanController.getEditLoanForm);
router.post('/editar/:id', isAuthenticated, loanController.updateLoan);
router.get('/devolver/:id', isAuthenticated, loanController.returnBook);
router.get('/reactivar/:id', isAuthenticated, loanController.reactivateLoan);
router.get('/eliminar/:id', isAuthenticated, loanController.deleteLoan);

module.exports = router;