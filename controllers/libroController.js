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
  // Get all authors and categories to populate the form
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

// Create a new book with support for multiple authors and categories
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

  // Validación básica: se requiere título y copias totales
  if (!title || !total_copies) {
    return getFormDataAndRenderNewForm(res, 'Los campos Título y Copias Totales son requeridos.');
  }

  // Make sure author_ids and category_ids are arrays even if one item is selected
  const selectedAuthorIds = Array.isArray(author_ids) ? author_ids : (author_ids ? [author_ids] : []);
  const selectedCategoryIds = Array.isArray(category_ids) ? category_ids : (category_ids ? [category_ids] : []);
  
  // Prepare new author names to be added (convert to array if it's a string)
  const newAuthorNames = Array.isArray(new_author_names) ? new_author_names : (new_author_names ? [new_author_names] : []);
  // Filter out empty author names
  const filteredNewAuthorNames = newAuthorNames.filter(name => name && name.trim() !== '');
  
  // Prepare new category names to be added
  const newCategoryNames = Array.isArray(new_category_names) ? new_category_names : (new_category_names ? [new_category_names] : []);
  // Filter out empty category names
  const filteredNewCategoryNames = newCategoryNames.filter(name => name && name.trim() !== '');

  // Check if there's at least one author (either selected or new)
  if (selectedAuthorIds.length === 0 && filteredNewAuthorNames.length === 0) {
    return getFormDataAndRenderNewForm(res, 'Debe seleccionar al menos un autor o ingresar uno nuevo.');
  }

  try {
    // Start transaction
    await beginTransaction();
    
    // 1. Create the book
    const bookId = await insertBook(title, publisher, year, total_copies);
    
    // 2. Process authors (existing and new)
    const allAuthorIds = [...selectedAuthorIds];
    
    // Add new authors if any
    for (const authorName of filteredNewAuthorNames) {
      const authorId = await addNewAuthor(authorName);
      allAuthorIds.push(authorId);
    }
    
    // 3. Associate authors with the book
    await associateAuthorsWithBook(bookId, allAuthorIds);
    
    // 4. Process categories (existing and new)
    const allCategoryIds = [...selectedCategoryIds];
    
    // Add new categories if any
    for (const categoryName of filteredNewCategoryNames) {
      const categoryId = await addNewCategory(categoryName);
      allCategoryIds.push(categoryId);
    }
    
    // 5. Associate categories with the book
    await associateCategoriesWithBook(bookId, allCategoryIds);
    
    // Commit transaction
    await commitTransaction();
    
    res.redirect('/books');
  } catch (err) {
    // Rollback transaction on error
    await rollbackTransaction();
    console.error('Error al guardar libro:', err);
    return getFormDataAndRenderNewForm(res, 'Error al guardar el libro: ' + err.message);
  }
};

exports.getEditBookForm = (req, res) => {
  const bookId = req.params.id;
  
  // Fetch book data
  const bookQuery = 'SELECT * FROM books WHERE id = ?';
  
  // Fetch all authors
  const authorsQuery = 'SELECT id, name FROM authors ORDER BY name';
  
  // Fetch all categories
  const categoriesQuery = 'SELECT id, name FROM categories ORDER BY name';
  
  // Fetch book's authors
  const bookAuthorsQuery = 'SELECT author_id FROM book_authors WHERE book_id = ?';
  
  // Fetch book's categories
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
            
            // Extract author_ids and category_ids
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

  // Validación básica
  if (!title || !total_copies) {
    return res.redirect(`/books/editar/${bookId}`);
  }

  // Make sure author_ids and category_ids are arrays even if one item is selected
  const selectedAuthorIds = Array.isArray(author_ids) ? author_ids : (author_ids ? [author_ids] : []);
  const selectedCategoryIds = Array.isArray(category_ids) ? category_ids : (category_ids ? [category_ids] : []);
  
  // Prepare new author names to be added
  const newAuthorNames = Array.isArray(new_author_names) ? new_author_names : (new_author_names ? [new_author_names] : []);
  // Filter out empty author names
  const filteredNewAuthorNames = newAuthorNames.filter(name => name && name.trim() !== '');
  
  // Prepare new category names to be added
  const newCategoryNames = Array.isArray(new_category_names) ? new_category_names : (new_category_names ? [new_category_names] : []);
  // Filter out empty category names
  const filteredNewCategoryNames = newCategoryNames.filter(name => name && name.trim() !== '');

  // Check if there's at least one author (either selected or new)
  if (selectedAuthorIds.length === 0 && filteredNewAuthorNames.length === 0) {
    return res.redirect(`/books/editar/${bookId}`);
  }

  try {
    // Start transaction
    await beginTransaction();
    
    // 1. Update the book
    await updateBookInfo(bookId, title, publisher, year, total_copies, available_copies);
    
    // 2. Process authors (existing and new)
    const allAuthorIds = [...selectedAuthorIds];
    
    // Add new authors if any
    for (const authorName of filteredNewAuthorNames) {
      const authorId = await addNewAuthor(authorName);
      allAuthorIds.push(authorId);
    }
    
    // 3. Update book authors (clear existing and add new ones)
    await clearBookAuthors(bookId);
    await associateAuthorsWithBook(bookId, allAuthorIds);
    
    // 4. Process categories (existing and new)
    const allCategoryIds = [...selectedCategoryIds];
    
    // Add new categories if any
    for (const categoryName of filteredNewCategoryNames) {
      const categoryId = await addNewCategory(categoryName);
      allCategoryIds.push(categoryId);
    }
    
    // 5. Update book categories (clear existing and add new ones)
    await clearBookCategories(bookId);
    await associateCategoriesWithBook(bookId, allCategoryIds);
    
    // Commit transaction
    await commitTransaction();
    
    res.redirect('/books');
  } catch (err) {
    // Rollback transaction on error
    await rollbackTransaction();
    console.error("Error al actualizar libro:", err);
    res.redirect(`/books/editar/${bookId}`);
  }
};

exports.deleteBook = async (req, res) => {
  const bookId = req.params.id;
  
  try {
    // Start transaction
    await beginTransaction();
    
    // Delete book associations first
    await clearBookAuthors(bookId);
    await clearBookCategories(bookId);
    
    // Delete the book itself
    await deleteBookById(bookId);
    
    // Commit transaction
    await commitTransaction();
    
    res.redirect('/books');
  } catch (err) {
    // Rollback transaction on error
    await rollbackTransaction();
    console.error("Error al eliminar libro:", err);
    return res.status(500).send('Error en el servidor');
  }
};

// Helper functions for DB operations

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
    db.rollback(() => resolve());  // Always resolve even if rollback fails
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
    // First check if author already exists
    db.query("SELECT id FROM authors WHERE name = ?", [authorName], (err, results) => {
      if (err) return reject(err);
      
      if (results.length > 0) {
        // Author exists, return its id
        resolve(results[0].id);
      } else {
        // Create new author
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
    // First check if category already exists
    db.query("SELECT id FROM categories WHERE name = ?", [categoryName], (err, results) => {
      if (err) return reject(err);
      
      if (results.length > 0) {
        // Category exists, return its id
        resolve(results[0].id);
      } else {
        // Create new category
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
    // Create value sets for bulk insert
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
    // Create value sets for bulk insert
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

// Helper function to get form data and render the new book form with an error message
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