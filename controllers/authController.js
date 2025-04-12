// controllers/authController.js
const db = require('../database/db');
const bcrypt = require('bcryptjs');

exports.showLogin = (req, res) => {
  res.render('login');
};

exports.login = (req, res) => {
  const { email, password } = req.body;

  db.query('SELECT * FROM users WHERE email = ?', [email], async (err, results) => {
    if (err) return res.send('Error en la base de datos');
    if (results.length === 0) return res.send('Usuario no encontrado');

    const user = results[0];
    const match = await bcrypt.compare(password, user.password);
    if (!match) return res.send('Contraseña incorrecta');

    const emailLower = email.toLowerCase();
    if (user.role === 'admin' && !emailLower.endsWith('@admin.com')) {
      return res.send('El email no es válido para un administrador');
    }
    if (user.role === 'user' && emailLower.endsWith('@admin.com')) {
      return res.send('El email no es válido para un usuario');
    }

    req.session.user = {
      id: user.id,
      username: user.username,
      full_name: user.full_name,
      email: user.email,
      role: user.role
    };
    res.redirect('/books');
  });
};

exports.logout = (req, res) => {
  req.session.destroy(() => {
    res.redirect('/login');
  });
};
