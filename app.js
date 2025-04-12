const express = require('express');
const path = require('path');
const session = require('express-session');

const authRoutes = require('./routes/authRoutes');
const libroRoutes = require('./routes/libroRoutes');
const loanRoutes = require('./routes/loanRoutes'); // Añadimos las rutas de préstamos

const app = express();

app.use(express.urlencoded({ extended: true }));
app.use(express.json());

app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

app.use(express.static(path.join(__dirname, 'public')));

app.use(session({
  secret: 'clave-secreta',
  resave: false,
  saveUninitialized: false
}));

app.use((req, res, next) => {
  res.locals.user = req.session.user || null;
  next();
});

// Middleware para proteger rutas
const isAuthenticated = (req, res, next) => {
  if (req.session.user) {
    return next();
  }
  res.redirect('/login');
};

app.use(authRoutes);
app.use('/books', isAuthenticated, libroRoutes);
app.use('/loans', isAuthenticated, loanRoutes);

// Eliminamos la ruta /books/index que ya no se utiliza

app.get('/', (req, res) => {
  if (req.session.user) {
    if (req.session.user.role === 'admin') {
      return res.redirect('/books');
    } else {
      return res.redirect('/loans');
    }
  }
  res.redirect('/login');
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Servidor corriendo en http://localhost:${PORT}`));