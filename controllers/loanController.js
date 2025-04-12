const db = require('../database/db');

// Obtener todos los préstamos
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
    res.render('loans/index', { 
      loans: results,
      user: req.session.user
    });
  });
};

// Mostrar formulario para crear nuevo préstamo
exports.getNewLoanForm = (req, res) => {
  if (!req.session.user || req.session.user.role !== 'admin') {
    return res.status(403).send('Acceso denegado: se requiere rol de administrador');
  }

  // Obtener libros disponibles
  db.query('SELECT id, title FROM books WHERE available_copies > 0', (err, books) => {
    if (err) {
      console.error("Error al obtener libros:", err);
      return res.status(500).send('Error en el servidor');
    }

    // Obtener usuarios
    db.query('SELECT id, username, full_name FROM users', (err, users) => {
      if (err) {
        console.error("Error al obtener usuarios:", err);
        return res.status(500).send('Error en el servidor');
      }

      res.render('loans/new', { 
        books, 
        users, 
        error: null,
        user: req.session.user
      });
    });
  });
};

// Crear nuevo préstamo
exports.createLoan = (req, res) => {
  if (!req.session.user || req.session.user.role !== 'admin') {
    return res.status(403).send('Acceso denegado: se requiere rol de administrador');
  }

  const { book_id, user_id, loan_date, status } = req.body;

  // Validar datos
  if (!book_id || !user_id || !loan_date) {
    return db.query('SELECT id, title FROM books WHERE available_copies > 0', (err, books) => {
      db.query('SELECT id, username, full_name FROM users', (err, users) => {
        res.render('loans/new', { 
          books, 
          users, 
          error: 'Por favor complete todos los campos requeridos',
          user: req.session.user
        });
      });
    });
  }

  // Calcular la fecha de vencimiento (15 días después del préstamo por defecto)
  const loanDateObj = new Date(loan_date);
  const dueDate = new Date(loanDateObj);
  dueDate.setDate(dueDate.getDate() + 15);

  // Crear el préstamo
  const query = `
    INSERT INTO loans (book_id, user_id, loan_date, due_date, status)
    VALUES (?, ?, ?, ?, ?)
  `;

  db.query(query, [book_id, user_id, loan_date, dueDate, status || 'active'], (err, result) => {
    if (err) {
      console.error("Error al crear préstamo:", err);
      return res.status(500).send('Error en el servidor');
    }

    // Actualizar la cantidad de copias disponibles del libro
    db.query(
      'UPDATE books SET available_copies = available_copies - 1 WHERE id = ?',
      [book_id],
      (err) => {
        if (err) {
          console.error("Error al actualizar copias disponibles:", err);
        }
        res.redirect('/loans');
      }
    );
  });
};

// Mostrar formulario para editar préstamo
exports.getEditLoanForm = (req, res) => {
  if (!req.session.user || req.session.user.role !== 'admin') {
    return res.status(403).send('Acceso denegado: se requiere rol de administrador');
  }

  const loanId = req.params.id;

  // Obtener préstamo actual
  db.query(
    `SELECT * FROM loans WHERE id = ?`,
    [loanId],
    (err, loans) => {
      if (err || !loans.length) {
        console.error("Error al obtener préstamo:", err);
        return res.status(404).send('Préstamo no encontrado');
      }

      const loan = loans[0];

      // Obtener libros y usuarios
      db.query('SELECT id, title FROM books', (err, books) => {
        if (err) {
          console.error("Error al obtener libros:", err);
          return res.status(500).send('Error en el servidor');
        }

        db.query('SELECT id, username, full_name FROM users', (err, users) => {
          if (err) {
            console.error("Error al obtener usuarios:", err);
            return res.status(500).send('Error en el servidor');
          }

          res.render('loans/edit', { 
            loan, 
            books, 
            users,
            user: req.session.user
          });
        });
      });
    }
  );
};

// Actualizar préstamo
exports.updateLoan = (req, res) => {
  if (!req.session.user || req.session.user.role !== 'admin') {
    return res.status(403).send('Acceso denegado: se requiere rol de administrador');
  }

  const loanId = req.params.id;
  const { book_id, user_id, loan_date, status } = req.body;

  // Validar datos
  if (!book_id || !user_id || !loan_date || !status) {
    return res.status(400).send('Por favor complete todos los campos requeridos');
  }

  // Obtener información del préstamo actual para verificar cambios en el libro
  db.query('SELECT * FROM loans WHERE id = ?', [loanId], (err, loans) => {
    if (err || !loans.length) {
      console.error("Error al obtener préstamo:", err);
      return res.status(404).send('Préstamo no encontrado');
    }

    const currentLoan = loans[0];
    const prevBookId = currentLoan.book_id;
    const prevStatus = currentLoan.status;

    // Calcular nueva fecha de vencimiento si se cambió la fecha de préstamo
    const loanDateObj = new Date(loan_date);
    const dueDate = new Date(loanDateObj);
    dueDate.setDate(dueDate.getDate() + 15);

    // Actualizar préstamo
    const query = `
      UPDATE loans 
      SET book_id = ?, user_id = ?, loan_date = ?, due_date = ?, status = ?
      WHERE id = ?
    `;

    db.query(query, [book_id, user_id, loan_date, dueDate, status, loanId], (err, result) => {
      if (err) {
        console.error("Error al actualizar préstamo:", err);
        return res.status(500).send('Error en el servidor');
      }

      // Manejar cambios en libros (actualizar copias disponibles)
      const handleBookChanges = () => {
        // Si se cambió el libro o el estado cambió a/desde 'returned'
        if (prevBookId != book_id || prevStatus !== status) {
          // Ajustar copias disponibles de libros afectados
          if (prevBookId != book_id) {
            // Incrementar copias disponibles del libro anterior
            db.query(
              'UPDATE books SET available_copies = available_copies + 1 WHERE id = ?',
              [prevBookId],
              (err) => {
                if (err) {
                  console.error("Error al actualizar copias disponibles del libro anterior:", err);
                }

                // Decrementar copias disponibles del nuevo libro
                db.query(
                  'UPDATE books SET available_copies = available_copies - 1 WHERE id = ?',
                  [book_id],
                  (err) => {
                    if (err) {
                      console.error("Error al actualizar copias disponibles del nuevo libro:", err);
                    }
                    res.redirect('/loans');
                  }
                );
              }
            );
          } else if (prevStatus !== status) {
            // Ajustar copias disponibles según cambio de estado
            if (status === 'returned' && prevStatus !== 'returned') {
              // Incrementar copias disponibles si se devuelve
              db.query(
                'UPDATE books SET available_copies = available_copies + 1 WHERE id = ?',
                [book_id],
                (err) => {
                  if (err) {
                    console.error("Error al actualizar copias disponibles:", err);
                  }
                  res.redirect('/loans');
                }
              );
            } else if (status !== 'returned' && prevStatus === 'returned') {
              // Decrementar copias disponibles si se cambia de devuelto a otro estado
              db.query(
                'UPDATE books SET available_copies = available_copies - 1 WHERE id = ?',
                [book_id],
                (err) => {
                  if (err) {
                    console.error("Error al actualizar copias disponibles:", err);
                  }
                  res.redirect('/loans');
                }
              );
            } else {
              res.redirect('/loans');
            }
          } else {
            res.redirect('/loans');
          }
        } else {
          res.redirect('/loans');
        }
      };

      handleBookChanges();
    });
  });
};

// Devolver libro
exports.returnBook = (req, res) => {
  const loanId = req.params.id;
  const userId = req.session.user.id;
  
  // Verificar que el usuario pueda devolver este libro
  let query = 'SELECT * FROM loans WHERE id = ?';
  const params = [loanId];
  
  // Si no es admin, verificar que el préstamo pertenezca al usuario
  if (req.session.user.role !== 'admin') {
    query += ' AND user_id = ?';
    params.push(userId);
  }
  
  db.query(query, params, (err, loans) => {
    if (err || !loans.length) {
      console.error("Error al obtener préstamo:", err);
      return res.status(404).send('Préstamo no encontrado o no autorizado');
    }
    
    const loan = loans[0];
    
    // Actualizar préstamo a estado "returned" y establecer fecha de devolución
    const returnDate = new Date().toISOString().slice(0, 10);
    db.query(
      'UPDATE loans SET status = ?, return_date = ? WHERE id = ?',
      ['returned', returnDate, loanId],
      (err, result) => {
        if (err) {
          console.error("Error al actualizar préstamo:", err);
          return res.status(500).send('Error en el servidor');
        }
        
        // Incrementar copias disponibles del libro
        db.query(
          'UPDATE books SET available_copies = available_copies + 1 WHERE id = ?',
          [loan.book_id],
          (err) => {
            if (err) {
              console.error("Error al actualizar copias disponibles:", err);
            }
            res.redirect('/loans');
          }
        );
      }
    );
  });
};

// Eliminar préstamo
exports.deleteLoan = (req, res) => {
  if (!req.session.user || req.session.user.role !== 'admin') {
    return res.status(403).send('Acceso denegado: se requiere rol de administrador');
  }

  const loanId = req.params.id;

  // Obtener información del préstamo antes de eliminarlo
  db.query('SELECT * FROM loans WHERE id = ?', [loanId], (err, loans) => {
    if (err || !loans.length) {
      console.error("Error al obtener préstamo:", err);
      return res.status(404).send('Préstamo no encontrado');
    }

    const loan = loans[0];

    // Eliminar préstamo
    db.query('DELETE FROM loans WHERE id = ?', [loanId], (err, result) => {
      if (err) {
        console.error("Error al eliminar préstamo:", err);
        return res.status(500).send('Error en el servidor');
      }

      // Si el préstamo no estaba en estado "returned", incrementar copias disponibles
      if (loan.status !== 'returned') {
        db.query(
          'UPDATE books SET available_copies = available_copies + 1 WHERE id = ?',
          [loan.book_id],
          (err) => {
            if (err) {
              console.error("Error al actualizar copias disponibles:", err);
            }
            res.redirect('/loans');
          }
        );
      } else {
        res.redirect('/loans');
      }
    });
  });
};