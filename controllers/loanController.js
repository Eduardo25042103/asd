const db = require('../database/db');

// Obtener todos los préstamos
// Modificación opcional para garantizar que los estados de los préstamos sean precisos
exports.getAllLoans = (req, res) => {
  // Verificar que el usuario esté autenticado
  if (!req.session.user) {
    return res.redirect('/login');
  }

  // Primero, actualizar estados de préstamos vencidos
  const today = new Date().toISOString().slice(0, 10);
  const updateStatusQuery = `
    UPDATE loans 
    SET status = 'vencido' 
    WHERE due_date < ? AND status = 'activo'
  `;
  
  db.query(updateStatusQuery, [today], (err) => {
    if (err) {
      console.error("Error al actualizar estados de préstamos:", err);
    }
    
    // Ahora obtener los préstamos con estados actualizados
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
  });
};

// Mostrar formulario para crear nuevo préstamo
exports.getNewLoanForm = (req, res) => {
  if (!req.session.user) {
    return res.redirect('/login');
  }

  // Obtener libros disponibles - para admins mostrar todos los libros
  let booksQuery = 'SELECT id, title FROM books';
  
  // Para usuarios normales solo mostrar libros con copias disponibles
  if (req.session.user.role !== 'admin') {
    booksQuery += ' WHERE available_copies > 0';
  }
  
  db.query(booksQuery, (err, books) => {
    if (err) {
      console.error("Error al obtener libros:", err);
      return res.status(500).send('Error en el servidor');
    }

    // Para usuarios normales, no es necesario seleccionar usuario
    if (req.session.user.role !== 'admin') {
      return res.render('loans/new', { 
        books, 
        users: null, 
        error: null,
        user: req.session.user
      });
    }

    // Si es admin, obtener lista de usuarios
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
  if (!req.session.user) {
    return res.redirect('/login');
  }

  const { book_id, loan_date } = req.body;
  // Si es admin, toma el user_id del formulario, si no, usa el del usuario actual
  const user_id = req.session.user.role === 'admin' ? req.body.user_id : req.session.user.id;
  // Por defecto, estado activo para nuevos préstamos
  const status = 'activo';

  // Validar datos
  if (!book_id || !loan_date || (req.session.user.role === 'admin' && !req.body.user_id)) {
    return db.query('SELECT id, title FROM books', (err, books) => {
      if (req.session.user.role === 'admin') {
        db.query('SELECT id, username, full_name FROM users', (err, users) => {
          res.render('loans/new', { 
            books, 
            users, 
            error: 'Por favor complete todos los campos requeridos',
            user: req.session.user
          });
        });
      } else {
        res.render('loans/new', { 
          books, 
          users: null, 
          error: 'Por favor complete todos los campos requeridos',
          user: req.session.user
        });
      }
    });
  }

  // Calcular la fecha de vencimiento (15 días después del préstamo por defecto)
  const loanDateObj = new Date(loan_date);
  const dueDate = new Date(loanDateObj);
  dueDate.setDate(dueDate.getDate() + 15);

  // Crear el préstamo - sin verificar disponibilidad para admin
  const query = `
    INSERT INTO loans (book_id, user_id, loan_date, due_date, status)
    VALUES (?, ?, ?, ?, ?)
  `;

  db.query(query, [book_id, user_id, loan_date, dueDate, status], (err, result) => {
    if (err) {
      console.error("Error al crear préstamo:", err);
      return res.status(500).send('Error en el servidor');
    }

    // Actualizar la cantidad de copias disponibles del libro
    // Solo decrementar si hay copias disponibles o si el usuario es normal
    if (req.session.user.role !== 'admin') {
      db.query(
        'UPDATE books SET available_copies = available_copies - 1 WHERE id = ? AND available_copies > 0',
        [book_id],
        (err) => {
          if (err) {
            console.error("Error al actualizar copias disponibles:", err);
          }
          res.redirect('/loans');
        }
      );
    } else {
      // Para admin, actualizar sin verificar disponibilidad
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
    }
  });
};

// Mostrar formulario para editar préstamo
exports.getEditLoanForm = (req, res) => {
  if (!req.session.user) {
    return res.redirect('/login');
  }

  const loanId = req.params.id;
  
  // Preparar la consulta para obtener el préstamo
  let loanQuery = 'SELECT * FROM loans WHERE id = ?';
  const loanParams = [loanId];
  
  // Si no es admin, asegurar que solo pueda editar sus propios préstamos
  if (req.session.user.role !== 'admin') {
    loanQuery += ' AND user_id = ?';
    loanParams.push(req.session.user.id);
  }

  // Obtener préstamo actual
  db.query(loanQuery, loanParams, (err, loans) => {
    if (err || !loans.length) {
      console.error("Error al obtener préstamo:", err);
      return res.status(404).send('Préstamo no encontrado o no autorizado');
    }

    const loan = loans[0];

    // Obtener todos los libros para admin, solo disponibles para usuarios normales
    let booksQuery = 'SELECT id, title FROM books';
    if (req.session.user.role !== 'admin') {
      booksQuery += ' WHERE available_copies > 0 OR id = ?';
      db.query(booksQuery, [loan.book_id], (err, books) => {
        if (err) {
          console.error("Error al obtener libros:", err);
          return res.status(500).send('Error en el servidor');
        }
        
        return res.render('loans/edit', { 
          loan, 
          books, 
          users: null,
          user: req.session.user
        });
      });
    } else {
      // Para admin obtener todos los libros
      db.query(booksQuery, (err, books) => {
        if (err) {
          console.error("Error al obtener libros:", err);
          return res.status(500).send('Error en el servidor');
        }
        
        // Si es admin, obtener usuarios
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
  });
};

// Actualizar préstamo
exports.updateLoan = (req, res) => {
  if (!req.session.user) {
    return res.redirect('/login');
  }

  const loanId = req.params.id;
  const { book_id, loan_date, status } = req.body;
  
  // Si es admin, toma el user_id del formulario, si no, usa el del usuario actual
  const user_id = req.session.user.role === 'admin' ? req.body.user_id : req.session.user.id;

  // Preparar la consulta para verificar acceso al préstamo
  let checkQuery = 'SELECT * FROM loans WHERE id = ?';
  const checkParams = [loanId];
  
  // Si no es admin, asegurar que solo pueda modificar sus propios préstamos
  if (req.session.user.role !== 'admin') {
    checkQuery += ' AND user_id = ?';
    checkParams.push(req.session.user.id);
  }

  // Validar datos
  if (!book_id || !loan_date) {
    return res.status(400).send('Por favor complete todos los campos requeridos');
  }

  // Verificar acceso al préstamo
  db.query(checkQuery, checkParams, (err, loans) => {
    if (err || !loans.length) {
      console.error("Error al verificar préstamo:", err);
      return res.status(404).send('Préstamo no encontrado o no autorizado');
    }

    const currentLoan = loans[0];
    const prevBookId = currentLoan.book_id;
    const prevStatus = currentLoan.status;
    
    // Determinar si debemos actualizar el estado
    const newStatus = req.session.user.role === 'admin' && status ? status : prevStatus;

    // Calcular nueva fecha de vencimiento si se cambió la fecha de préstamo
    const loanDateObj = new Date(loan_date);
    const dueDate = new Date(loanDateObj);
    dueDate.setDate(dueDate.getDate() + 15);

    // Actualizar préstamo
    let updateQuery = `
      UPDATE loans 
      SET book_id = ?, user_id = ?, loan_date = ?, due_date = ?
    `;
    
    let updateParams = [book_id, user_id, loan_date, dueDate];
    
    // Admin puede actualizar también el estado
    if (req.session.user.role === 'admin') {
      updateQuery += `, status = ?`;
      updateParams.push(newStatus);
    }
    
    updateQuery += ` WHERE id = ?`;
    updateParams.push(loanId);

    db.query(updateQuery, updateParams, (err, result) => {
      if (err) {
        console.error("Error al actualizar préstamo:", err);
        return res.status(500).send('Error en el servidor');
      }

      // Manejar cambios en libros (actualizar copias disponibles)
      const handleBookChanges = () => {
        // Si se cambió el libro y el usuario es admin o si el préstamo no estaba devuelto
        if (prevBookId != book_id && (req.session.user.role === 'admin' || prevStatus !== 'devuelto')) {
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
        } else if (prevStatus !== 'devuelto' && newStatus === 'devuelto') {
          // Si el préstamo se está marcando como devuelto
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
        } else if (prevStatus === 'devuelto' && newStatus !== 'devuelto') {
          // Si el préstamo se está marcando como no devuelto (solo admin puede hacer esto)
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
      };

      handleBookChanges();
    });
  });
};

// Devolver libro
exports.returnBook = (req, res) => {
  if (!req.session.user) {
    return res.redirect('/login');
  }

  const loanId = req.params.id;
  
  // Preparar la consulta para verificar acceso al préstamo
  let query = 'SELECT * FROM loans WHERE id = ?';
  const params = [loanId];
  
  // Si no es admin, verificar que el préstamo pertenezca al usuario
  if (req.session.user.role !== 'admin') {
    query += ' AND user_id = ?';
    params.push(req.session.user.id);
  }
  
  db.query(query, params, (err, loans) => {
    if (err || !loans.length) {
      console.error("Error al obtener préstamo:", err);
      return res.status(404).send('Préstamo no encontrado o no autorizado');
    }
    
    const loan = loans[0];
    
    // Verificar que el préstamo no esté ya en estado "devuelto"
    if (loan.status === 'devuelto') {
      return res.status(400).send('El préstamo ya ha sido devuelto');
    }
    
    // Actualizar préstamo a estado "devuelto" y establecer fecha de devolución
    const returnDate = new Date().toISOString().slice(0, 10);
    db.query(
      'UPDATE loans SET status = ?, return_date = ? WHERE id = ?',
      ['devuelto', returnDate, loanId],
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

exports.reactivateLoan = (req, res) => {
  if (!req.session.user) {
    return res.redirect('/login');
  }

  const loanId = req.params.id;
  
  // Preparar la consulta para verificar acceso al préstamo
  let query = 'SELECT * FROM loans WHERE id = ?';
  const params = [loanId];
  
  // Si no es admin, verificar que el préstamo pertenezca al usuario
  if (req.session.user.role !== 'admin') {
    query += ' AND user_id = ?';
    params.push(req.session.user.id);
  }
  
  db.query(query, params, (err, loans) => {
    if (err || !loans.length) {
      console.error("Error al obtener préstamo:", err);
      return res.status(404).send('Préstamo no encontrado o no autorizado');
    }
    
    const loan = loans[0];
    
    // Verificar que el préstamo esté en estado "devuelto"
    if (loan.status !== 'devuelto') {
      return res.status(400).send('Solo se pueden reactivar préstamos devueltos');
    }
    
    // Actualizar préstamo a estado "activo" y eliminar fecha de devolución
    db.query(
      'UPDATE loans SET status = ?, return_date = ? WHERE id = ?',
      ['activo', null, loanId],
      (err, result) => {
        if (err) {
          console.error("Error al actualizar préstamo:", err);
          return res.status(500).send('Error en el servidor');
        }
        
        // Decrementar copias disponibles del libro (ya que se vuelve a prestar)
        db.query(
          'UPDATE books SET available_copies = available_copies - 1 WHERE id = ?',
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
  if (!req.session.user) {
    return res.redirect('/login');
  }

  const loanId = req.params.id;
  
  // Preparar la consulta para verificar acceso al préstamo
  let query = 'SELECT * FROM loans WHERE id = ?';
  const params = [loanId];
  
  // Si no es admin, verificar que el préstamo pertenezca al usuario
  if (req.session.user.role !== 'admin') {
    query += ' AND user_id = ?';
    params.push(req.session.user.id);
  }

  // Obtener información del préstamo antes de eliminarlo
  db.query(query, params, (err, loans) => {
    if (err || !loans.length) {
      console.error("Error al obtener préstamo:", err);
      return res.status(404).send('Préstamo no encontrado o no autorizado');
    }

    const loan = loans[0];

    // Eliminar préstamo
    db.query('DELETE FROM loans WHERE id = ?', [loanId], (err, result) => {
      if (err) {
        console.error("Error al eliminar préstamo:", err);
        return res.status(500).send('Error en el servidor');
      }

      // Si el préstamo no estaba en estado "devuelto", incrementar copias disponibles
      if (loan.status !== 'devuelto') {
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