const db = require('../database/db');

exports.getAllBooks = (req, res) => {
  const query = `
    SELECT books.id, books.title, authors.name AS author_name,
           books.publisher, books.year, books.category,
           books.total_copies, books.available_copies
    FROM books
    INNER JOIN authors ON books.author_id = authors.id
  `;
  db.query(query, (err, results) => {
    if (err) {
      console.error("Error al obtener libros:", err);
      return res.status(500).send('Error en el servidor');
    }
    res.render('books/index', { books: results });
  });
};

exports.getNewBookForm = (req, res) => {
  const query = 'SELECT id, name FROM authors';
  db.query(query, (err, authors) => {
    if (err) {
      console.error("Error al obtener autores:", err);
      return res.status(500).send("Error en el servidor");
    }
    res.render('books/new', { authors, error: null });
  });
};

// Crea un nuevo libro, permitiendo ingresar un nuevo autor si fuera necesario
exports.createBook = async (req, res) => {
  const {
    title,
    author_id,
    new_author_name,
    new_author_bio,
    publisher,
    year,
    category,
    total_copies
  } = req.body;

  // Validación básica: se requiere título, (autor existente o nuevo) y copias totales
  if (!title || ((!author_id || author_id.trim() === '') && !new_author_name) || !total_copies) {
    return db.query('SELECT id, name FROM authors', (err, authors) => {
      if (err) {
        console.error("Error al cargar autores:", err);
        return res.status(500).send("Error en el servidor");
      }
      res.status(400).render('books/new', { authors, error: 'Los campos Título, Autor y Copias Totales son requeridos.' });
    });
  }

  let finalAuthorId = author_id && author_id.trim() !== '' ? author_id : null;

  try {
    // Si no se seleccionó un autor y se ingresó un nuevo autor, verificamos que no se repita.
    if (!finalAuthorId && new_author_name) {
      finalAuthorId = await new Promise((resolve, reject) => {
        // Buscar si existe un autor con ese nombre
        db.query("SELECT id FROM authors WHERE name = ?", [new_author_name], (err, results) => {
          if (err) return reject(err);
          if (results.length > 0) {
            // Si ya existe, usamos ese ID.
            resolve(results[0].id);
          } else {
            // Si no existe, lo insertamos.
            db.query('INSERT INTO authors (name, bio) VALUES (?, ?)',
              [new_author_name, new_author_bio || null],
              (err, result) => {
                if (err) return reject(err);
                resolve(result.insertId);
              }
            );
          }
        });
      });
    }

    if (!finalAuthorId) {
      return res.status(400).send('Debe seleccionar o ingresar un autor válido.');
    }

    await new Promise((resolve, reject) => {
      const queryInsertBook = `
        INSERT INTO books 
          (title, author_id, publisher, year, category, total_copies, available_copies)
        VALUES (?, ?, ?, ?, ?, ?, ?)
      `;
      db.query(queryInsertBook,
        [title, finalAuthorId, publisher, year, category, total_copies, total_copies],
        (err, result) => {
          if (err) return reject(err);
          resolve(result);
        });
    });

    res.redirect('/books');
  } catch (err) {
    console.error('Error al guardar libro:', err);
    res.status(500).send('Error al guardar libro');
  }
};


// Renderiza el formulario de edición para un libro específico
exports.getEditBookForm = (req, res) => {
  const bookId = req.params.id;
  const queryBook = 'SELECT * FROM books WHERE id = ?';
  const queryAuthors = 'SELECT id, name FROM authors';

  db.query(queryBook, [bookId], (err, bookResults) => {
    if (err) {
      console.error("Error al obtener libro:", err);
      return res.status(500).send('Error en el servidor');
    }
    if (bookResults.length === 0) {
      return res.status(404).send('Libro no encontrado');
    }
    db.query(queryAuthors, (err, authors) => {
      if (err) {
        console.error("Error al obtener autores:", err);
        return res.status(500).send("Error en el servidor");
      }
      res.render('books/edit', { book: bookResults[0], authors });
    });
  });
};


exports.updateBook = async (req, res) => {
  const bookId = req.params.id;
  const {
    title,
    author_id,
    new_author_name,
    new_author_bio,
    publisher,
    year,
    category,
    total_copies,
    available_copies
  } = req.body;

  // Validación: se requiere título, (autor existente o nuevo) y copias totales
  if (!title || (((!author_id || author_id.trim() === '') && !new_author_name)) || !total_copies) {
    return res.redirect(`/books/editar/${bookId}`);
  }

  let finalAuthorId = author_id && author_id.trim() !== '' ? author_id : null;

  try {
    // Si no se seleccionó autor y se ingresó un nuevo autor, se verifica que no exista ya.
    if (!finalAuthorId && new_author_name) {
      finalAuthorId = await new Promise((resolve, reject) => {
        db.query("SELECT id FROM authors WHERE name = ?", [new_author_name], (err, results) => {
          if (err) return reject(err);
          if (results.length > 0) {
            resolve(results[0].id);
          } else {
            db.query("INSERT INTO authors (name, bio) VALUES (?, ?)", [new_author_name, new_author_bio || null], (err, result) => {
              if (err) return reject(err);
              resolve(result.insertId);
            });
          }
        });
      });
    }

    if (!finalAuthorId) {
      return res.redirect(`/books/editar/${bookId}`);
    }

    await new Promise((resolve, reject) => {
      const query = `
        UPDATE books
        SET title = ?, author_id = ?, publisher = ?, year = ?, category = ?, total_copies = ?, available_copies = ?
        WHERE id = ?
      `;
      db.query(query,
        [title, finalAuthorId, publisher, year, category, total_copies, available_copies, bookId],
        (err, result) => {
          if (err) return reject(err);
          resolve(result);
        });
    });

    res.redirect('/books');
  } catch (err) {
    console.error("Error al actualizar libro:", err);
    res.redirect(`/books/editar/${bookId}`);
  }
};


exports.deleteBook = (req, res) => {
  const bookId = req.params.id;
  const query = 'DELETE FROM books WHERE id = ?';
  db.query(query, [bookId], (err, result) => {
    if (err) {
      console.error("Error al eliminar libro:", err);
      return res.status(500).send('Error en el servidor');
    }
    res.redirect('/books');
  });
};
