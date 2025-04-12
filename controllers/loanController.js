const db = require('../database/db');

exports.getAllLoans = (req, res) => {
  // Verificar que el usuario esté autenticado
  if (!req.session.user) {
    return res.redirect('/login');
  }

  // Consulta para obtener préstamos, posiblemente filtrada por usuario si no es admin
  let query = `
    SELECT loans.id, books.title, users.username, 
           loans.loan_date, loans.due_date, loans.return_date, loans.status
    FROM loans
    INNER JOIN books ON loans.book_id = books.id
    INNER JOIN users ON loans.user_id = users.id
  `;

  // Si es un usuario normal, solo muestra sus préstamos
  const params = [];
  if (req.session.user.role !== 'admin') {
    query += ' WHERE loans.user_id = ?';
    params.push(req.session.user.id);
  }

  db.query(query, params, (err, results) => {
    if (err) {
      console.error("Error al obtener préstamos:", err);
      return res.status(500).send('Error en el servidor');
    }
    res.render('loans/index', { loans: results });
  });
};