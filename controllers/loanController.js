const db = require('../database/db');

exports.getAllLoans = (req, res) => {
  if (!req.session.user) {
    return res.redirect('/login');
  }

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
    
    let query = `
      SELECT loans.id, books.title, users.username, 
             loans.loan_date, loans.due_date, loans.return_date, loans.status
      FROM loans
      INNER JOIN books ON loans.book_id = books.id
      INNER JOIN users ON loans.user_id = users.id
    `;

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

exports.getNewLoanForm = (req, res) => {
  if (!req.session.user) {
    return res.redirect('/login');
  }

  let booksQuery = 'SELECT id, title FROM books';
  
  if (req.session.user.role !== 'admin') {
    booksQuery += ' WHERE available_copies > 0';
  }
  
  db.query(booksQuery, (err, books) => {
    if (err) {
      console.error("Error al obtener libros:", err);
      return res.status(500).send('Error en el servidor');
    }

    if (req.session.user.role !== 'admin') {
      return res.render('loans/new', { 
        books, 
        users: null, 
        error: null,
        user: req.session.user
      });
    }

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

exports.createLoan = (req, res) => {
  if (!req.session.user) {
    return res.redirect('/login');
  }

  const { book_id, loan_date } = req.body;
  const user_id = req.session.user.role === 'admin' ? req.body.user_id : req.session.user.id;
  const status = 'activo';

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

  const loanDateObj = new Date(loan_date);
  const dueDate = new Date(loanDateObj);
  dueDate.setDate(dueDate.getDate() + 15);

  const query = `
    INSERT INTO loans (book_id, user_id, loan_date, due_date, status)
    VALUES (?, ?, ?, ?, ?)
  `;

  db.query(query, [book_id, user_id, loan_date, dueDate, status], (err, result) => {
    if (err) {
      console.error("Error al crear préstamo:", err);
      return res.status(500).send('Error en el servidor');
    }

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

exports.getEditLoanForm = (req, res) => {
  if (!req.session.user) {
    return res.redirect('/login');
  }

  const loanId = req.params.id;
  
  let loanQuery = 'SELECT * FROM loans WHERE id = ?';
  const loanParams = [loanId];
  
  if (req.session.user.role !== 'admin') {
    loanQuery += ' AND user_id = ?';
    loanParams.push(req.session.user.id);
  }

  db.query(loanQuery, loanParams, (err, loans) => {
    if (err || !loans.length) {
      console.error("Error al obtener préstamo:", err);
      return res.status(404).send('Préstamo no encontrado o no autorizado');
    }

    const loan = loans[0];

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
      db.query(booksQuery, (err, books) => {
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
  });
};

exports.updateLoan = (req, res) => {
  if (!req.session.user) {
    return res.redirect('/login');
  }

  const loanId = req.params.id;
  const { book_id, loan_date, status } = req.body;
  
  const user_id = req.session.user.role === 'admin' ? req.body.user_id : req.session.user.id;

  let checkQuery = 'SELECT * FROM loans WHERE id = ?';
  const checkParams = [loanId];
  
  if (req.session.user.role !== 'admin') {
    checkQuery += ' AND user_id = ?';
    checkParams.push(req.session.user.id);
  }

  if (!book_id || !loan_date) {
    return res.status(400).send('Por favor complete todos los campos requeridos');
  }

  db.query(checkQuery, checkParams, (err, loans) => {
    if (err || !loans.length) {
      console.error("Error al verificar préstamo:", err);
      return res.status(404).send('Préstamo no encontrado o no autorizado');
    }

    const currentLoan = loans[0];
    const prevBookId = currentLoan.book_id;
    const prevStatus = currentLoan.status;
    
    const newStatus = req.session.user.role === 'admin' && status ? status : prevStatus;

    const loanDateObj = new Date(loan_date);
    const dueDate = new Date(loanDateObj);
    dueDate.setDate(dueDate.getDate() + 15);

    let updateQuery = `
      UPDATE loans 
      SET book_id = ?, user_id = ?, loan_date = ?, due_date = ?
    `;
    
    let updateParams = [book_id, user_id, loan_date, dueDate];
    
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

      const handleBookChanges = () => {
        if (prevBookId != book_id && (req.session.user.role === 'admin' || prevStatus !== 'devuelto')) {
          db.query(
            'UPDATE books SET available_copies = available_copies + 1 WHERE id = ?',
            [prevBookId],
            (err) => {
              if (err) {
                console.error("Error al actualizar copias disponibles del libro anterior:", err);
              }

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

exports.returnBook = (req, res) => {
  if (!req.session.user) {
    return res.redirect('/login');
  }

  const loanId = req.params.id;
  
  let query = 'SELECT * FROM loans WHERE id = ?';
  const params = [loanId];
  
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
    
    if (loan.status === 'devuelto') {
      return res.status(400).send('El préstamo ya ha sido devuelto');
    }
    
    const returnDate = new Date().toISOString().slice(0, 10);
    db.query(
      'UPDATE loans SET status = ?, return_date = ? WHERE id = ?',
      ['devuelto', returnDate, loanId],
      (err, result) => {
        if (err) {
          console.error("Error al actualizar préstamo:", err);
          return res.status(500).send('Error en el servidor');
        }
        
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
  
  let query = 'SELECT * FROM loans WHERE id = ?';
  const params = [loanId];
  
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
    
    if (loan.status !== 'devuelto') {
      return res.status(400).send('Solo se pueden reactivar préstamos devueltos');
    }
    
    db.query(
      'UPDATE loans SET status = ?, return_date = ? WHERE id = ?',
      ['activo', null, loanId],
      (err, result) => {
        if (err) {
          console.error("Error al actualizar préstamo:", err);
          return res.status(500).send('Error en el servidor');
        }
        
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

exports.deleteLoan = (req, res) => {
  if (!req.session.user) {
    return res.redirect('/login');
  }

  const loanId = req.params.id;
  
  let query = 'SELECT * FROM loans WHERE id = ?';
  const params = [loanId];
  
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

    db.query('DELETE FROM loans WHERE id = ?', [loanId], (err, result) => {
      if (err) {
        console.error("Error al eliminar préstamo:", err);
        return res.status(500).send('Error en el servidor');
      }

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