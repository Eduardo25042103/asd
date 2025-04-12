const express = require('express');
const path = require('path');
const session = require('express-session');

const authRoutes = require('./routes/authRoutes');
const libroRoutes = require('./routes/libroRoutes');

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

app.use(authRoutes);
app.use('/books', libroRoutes);

app.get('/books/index', (req, res) => {
  if (!req.session.user) return res.redirect('/login');
  res.send(`Bienvenido ${req.session.user.username} con rol ${req.session.user.role}`);
});

app.get('/', (req, res) => {
  res.redirect('/books/index');
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Servidor corriendo en http://localhost:${PORT}`));
