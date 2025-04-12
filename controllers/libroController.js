const db = require('../database/db');

exports.getAllBooks = (req, res) => {
  const query = `
    SELECT b.id, b.title, b.publisher, b.year, b.total_copies, b.available_copies,
           GROUP_CONCAT(DISTINCT a.name SEPARATOR ', ') AS authors,
           GROUP_CONCAT(DISTINCT c.name SEPARATOR ', ') AS categories
    FROM books b
    LEFT JOIN book_authors ba ON b.id = ba.book_id
    LEFT JOIN authors a ON ba.author_id = a.id
    LEFT JOIN book_categories bc ON b.id = bc.book_id
    LEFT JOIN categories c ON bc.category_id = c.id
    GROUP BY b.id
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
  const authorQuery = 'SELECT id, name FROM authors ORDER BY name';
  const categoryQuery = 'SELECT id, name FROM categories ORDER BY name';
  
  db.query(authorQuery, (err, authors) => {
    if (err) {
      console.error("Error al obtener autores:", err);
      return res.status(500).send("Error en el servidor");
    }
    
    db.query(categoryQuery, (err, categories) => {
      if (err) {
        console.error("Error al obtener categorías:", err);
        return res.status(500).send("Error en el servidor");
      }
      
      res.render('books/new', { authors, categories, error: null });
    });
  });
};

exports.createBook = async (req, res) => {
  const {
    title,
    author_ids,
    new_author_names,
    publisher,
    year,
    category_ids,
    new_category_names,
    total_copies
  } = req.body;

  if (!title || !total_copies) {
    return getFormDataAndRenderNewForm(res, 'Los campos Título y Copias Totales son requeridos.');
  }


  const selectedAuthorIds = Array.isArray(author_ids) ? author_ids : (author_ids ? [author_ids] : []);
  const selectedCategoryIds = Array.isArray(category_ids) ? category_ids : (category_ids ? [category_ids] : []);
  
  const newAuthorNames = Array.isArray(new_author_names) ? new_author_names : (new_author_names ? [new_author_names] : []);
  const filteredNewAuthorNames = newAuthorNames.filter(name => name && name.trim() !== '');
  const newCategoryNames = Array.isArray(new_category_names) ? new_category_names : (new_category_names ? [new_category_names] : []);
  const filteredNewCategoryNames = newCategoryNames.filter(name => name && name.trim() !== '');

  
  if (selectedAuthorIds.length === 0 && filteredNewAuthorNames.length === 0) {
    return getFormDataAndRenderNewForm(res, 'Debe seleccionar al menos un autor o ingresar uno nuevo.');
  }

  try {
   
    await beginTransaction();
    
   
    const bookId = await insertBook(title, publisher, year, total_copies);
    
    
    const allAuthorIds = [...selectedAuthorIds];
    
    for (const authorName of filteredNewAuthorNames) {
      const authorId = await addNewAuthor(authorName);
      allAuthorIds.push(authorId);
    }
    
    await associateAuthorsWithBook(bookId, allAuthorIds);
    
    const allCategoryIds = [...selectedCategoryIds];
    
    for (const categoryName of filteredNewCategoryNames) {
      const categoryId = await addNewCategory(categoryName);
      allCategoryIds.push(categoryId);
    }
    
    await associateCategoriesWithBook(bookId, allCategoryIds);
    
    await commitTransaction();
    
    res.redirect('/books');
  } catch (err) {
    await rollbackTransaction();
    console.error('Error al guardar libro:', err);
    return getFormDataAndRenderNewForm(res, 'Error al guardar el libro: ' + err.message);
  }
};

exports.getEditBookForm = (req, res) => {
  const bookId = req.params.id;
  
  const bookQuery = 'SELECT * FROM books WHERE id = ?';
  
  const authorsQuery = 'SELECT id, name FROM authors ORDER BY name';
  
  const categoriesQuery = 'SELECT id, name FROM categories ORDER BY name';
  
  const bookAuthorsQuery = 'SELECT author_id FROM book_authors WHERE book_id = ?';
  
  const bookCategoriesQuery = 'SELECT category_id FROM book_categories WHERE book_id = ?';
  
  db.query(bookQuery, [bookId], (err, bookResults) => {
    if (err) {
      console.error("Error al obtener libro:", err);
      return res.status(500).send('Error en el servidor');
    }
    
    if (bookResults.length === 0) {
      return res.status(404).send('Libro no encontrado');
    }
    
    const book = bookResults[0];
    
    db.query(authorsQuery, (err, authors) => {
      if (err) {
        console.error("Error al obtener autores:", err);
        return res.status(500).send("Error en el servidor");
      }
      
      db.query(categoriesQuery, (err, categories) => {
        if (err) {
          console.error("Error al obtener categorías:", err);
          return res.status(500).send("Error en el servidor");
        }
        
        db.query(bookAuthorsQuery, [bookId], (err, bookAuthors) => {
          if (err) {
            console.error("Error al obtener autores del libro:", err);
            return res.status(500).send("Error en el servidor");
          }
          
          db.query(bookCategoriesQuery, [bookId], (err, bookCategories) => {
            if (err) {
              console.error("Error al obtener categorías del libro:", err);
              return res.status(500).send("Error en el servidor");
            }
                        const bookAuthorIds = bookAuthors.map(item => item.author_id);
            const bookCategoryIds = bookCategories.map(item => item.category_id);
            
            res.render('books/edit', { 
              book, 
              authors, 
              categories, 
              bookAuthorIds, 
              bookCategoryIds 
            });
          });
        });
      });
    });
  });
};

exports.updateBook = async (req, res) => {
  const bookId = req.params.id;
  const {
    title,
    author_ids,
    new_author_names,
    publisher,
    year,
    category_ids,
    new_category_names,
    total_copies,
    available_copies
  } = req.body;

  if (!title || !total_copies) {
    return res.redirect(`/books/editar/${bookId}`);
  }

  const selectedAuthorIds = Array.isArray(author_ids) ? author_ids : (author_ids ? [author_ids] : []);
  const selectedCategoryIds = Array.isArray(category_ids) ? category_ids : (category_ids ? [category_ids] : []);
  
  const newAuthorNames = Array.isArray(new_author_names) ? new_author_names : (new_author_names ? [new_author_names] : []);
  const filteredNewAuthorNames = newAuthorNames.filter(name => name && name.trim() !== '');
  
  const newCategoryNames = Array.isArray(new_category_names) ? new_category_names : (new_category_names ? [new_category_names] : []);
  const filteredNewCategoryNames = newCategoryNames.filter(name => name && name.trim() !== '');

  if (selectedAuthorIds.length === 0 && filteredNewAuthorNames.length === 0) {
    return res.redirect(`/books/editar/${bookId}`);
  }

  try {
    await beginTransaction();
    
    await updateBookInfo(bookId, title, publisher, year, total_copies, available_copies);
    
    const allAuthorIds = [...selectedAuthorIds];
    
    for (const authorName of filteredNewAuthorNames) {
      const authorId = await addNewAuthor(authorName);
      allAuthorIds.push(authorId);
    }
    
    await clearBookAuthors(bookId);
    await associateAuthorsWithBook(bookId, allAuthorIds);
    
    const allCategoryIds = [...selectedCategoryIds];
    
    for (const categoryName of filteredNewCategoryNames) {
      const categoryId = await addNewCategory(categoryName);
      allCategoryIds.push(categoryId);
    }
    
    await clearBookCategories(bookId);
    await associateCategoriesWithBook(bookId, allCategoryIds);
    
    await commitTransaction();
    
    res.redirect('/books');
  } catch (err) {
    await rollbackTransaction();
    console.error("Error al actualizar libro:", err);
    res.redirect(`/books/editar/${bookId}`);
  }
};

exports.deleteBook = async (req, res) => {
  const bookId = req.params.id;
  
  try {
    await beginTransaction();
    
    await clearBookAuthors(bookId);
    await clearBookCategories(bookId);
    
    await deleteBookById(bookId);
    
    await commitTransaction();
    
    res.redirect('/books');
  } catch (err) {
    await rollbackTransaction();
    console.error("Error al eliminar libro:", err);
    return res.status(500).send('Error en el servidor');
  }
};


function beginTransaction() {
  return new Promise((resolve, reject) => {
    db.beginTransaction(err => {
      if (err) reject(err);
      else resolve();
    });
  });
}

function commitTransaction() {
  return new Promise((resolve, reject) => {
    db.commit(err => {
      if (err) reject(err);
      else resolve();
    });
  });
}

function rollbackTransaction() {
  return new Promise((resolve, reject) => {
    db.rollback(() => resolve());
  });
}

function insertBook(title, publisher, year, total_copies) {
  return new Promise((resolve, reject) => {
    const query = `
      INSERT INTO books (title, publisher, year, total_copies, available_copies)
      VALUES (?, ?, ?, ?, ?)
    `;
    db.query(query, [title, publisher, year, total_copies, total_copies], (err, result) => {
      if (err) reject(err);
      else resolve(result.insertId);
    });
  });
}

function updateBookInfo(bookId, title, publisher, year, total_copies, available_copies) {
  return new Promise((resolve, reject) => {
    const query = `
      UPDATE books
      SET title = ?, publisher = ?, year = ?, total_copies = ?, available_copies = ?
      WHERE id = ?
    `;
    db.query(query, [title, publisher, year, total_copies, available_copies, bookId], (err, result) => {
      if (err) reject(err);
      else resolve(result);
    });
  });
}

function addNewAuthor(authorName) {
  return new Promise((resolve, reject) => {
    db.query("SELECT id FROM authors WHERE name = ?", [authorName], (err, results) => {
      if (err) return reject(err);
      
      if (results.length > 0) {
        resolve(results[0].id);
      } else {
        db.query("INSERT INTO authors (name) VALUES (?)", [authorName], (err, result) => {
          if (err) return reject(err);
          resolve(result.insertId);
        });
      }
    });
  });
}

function addNewCategory(categoryName) {
  return new Promise((resolve, reject) => {
    db.query("SELECT id FROM categories WHERE name = ?", [categoryName], (err, results) => {
      if (err) return reject(err);
      
      if (results.length > 0) {
        resolve(results[0].id);
      } else {
        db.query("INSERT INTO categories (name) VALUES (?)", [categoryName], (err, result) => {
          if (err) return reject(err);
          resolve(result.insertId);
        });
      }
    });
  });
}

function associateAuthorsWithBook(bookId, authorIds) {
  if (!authorIds.length) return Promise.resolve();
  
  return new Promise((resolve, reject) => {
    const values = authorIds.map(authorId => [bookId, authorId]);
    
    const query = "INSERT INTO book_authors (book_id, author_id) VALUES ?";
    db.query(query, [values], (err, result) => {
      if (err) reject(err);
      else resolve(result);
    });
  });
}

function associateCategoriesWithBook(bookId, categoryIds) {
  if (!categoryIds.length) return Promise.resolve();
  
  return new Promise((resolve, reject) => {
    const values = categoryIds.map(categoryId => [bookId, categoryId]);
    
    const query = "INSERT INTO book_categories (book_id, category_id) VALUES ?";
    db.query(query, [values], (err, result) => {
      if (err) reject(err);
      else resolve(result);
    });
  });
}

function clearBookAuthors(bookId) {
  return new Promise((resolve, reject) => {
    const query = "DELETE FROM book_authors WHERE book_id = ?";
    db.query(query, [bookId], (err, result) => {
      if (err) reject(err);
      else resolve(result);
    });
  });
}

function clearBookCategories(bookId) {
  return new Promise((resolve, reject) => {
    const query = "DELETE FROM book_categories WHERE book_id = ?";
    db.query(query, [bookId], (err, result) => {
      if (err) reject(err);
      else resolve(result);
    });
  });
}

function deleteBookById(bookId) {
  return new Promise((resolve, reject) => {
    const query = "DELETE FROM books WHERE id = ?";
    db.query(query, [bookId], (err, result) => {
      if (err) reject(err);
      else resolve(result);
    });
  });
}

function getFormDataAndRenderNewForm(res, errorMessage) {
  const authorQuery = 'SELECT id, name FROM authors ORDER BY name';
  const categoryQuery = 'SELECT id, name FROM categories ORDER BY name';
  
  db.query(authorQuery, (err, authors) => {
    if (err) {
      console.error("Error al obtener autores:", err);
      return res.status(500).send("Error en el servidor");
    }
    
    db.query(categoryQuery, (err, categories) => {
      if (err) {
        console.error("Error al obtener categorías:", err);
        return res.status(500).send("Error en el servidor");
      }
      
      res.status(400).render('books/new', { 
        authors, 
        categories, 
        error: errorMessage 
      });
    });
  });
}