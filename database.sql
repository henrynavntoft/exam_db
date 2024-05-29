PRAGMA foreign_keys = ON;


-- #################################
-- Primary table

DROP TABLE IF EXISTS books;

CREATE TABLE books(
    book_pk          TEXT UNIQUE, 
    publisher_fk     TEXT,
    book_name        TEXT,
    book_version     INTEGER,
    last_updated     DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (publisher_fk) REFERENCES publishers(publisher_pk),
    PRIMARY KEY (book_pk)
) WITHOUT ROWID;


INSERT INTO books VALUES
("1", "1", "The Great Gatsby", 1, CURRENT_TIMESTAMP),
("2", "1", "To Kill a Mockingbird", 1, CURRENT_TIMESTAMP);

-- #################################
-- Primary table

DROP TABLE IF EXISTS publishers;

CREATE TABLE publishers (
    publisher_pk    TEXT UNIQUE,
    publisher_name  TEXT,
    PRIMARY KEY (publisher_pk)
) WITHOUT ROWID;

INSERT INTO publishers VALUES
("1", "Penguin Classics"),
("2", "HarperCollins");


-- #################################
-- Primary table

DROP TABLE IF EXISTS authors;
 
CREATE TABLE authors (
    author_pk       TEXT UNIQUE,
    author_name     TEXT,
    PRIMARY KEY (author_pk)
) WITHOUT ROWID;

INSERT INTO authors VALUES
("1", "F. Scott Fitzgerald"),
("2", "Harper Lee");


-- #################################

DROP TABLE IF EXISTS categories;
-- Primary table

CREATE TABLE categories (
    category_pk     TEXT UNIQUE,
    category_name   TEXT,
    PRIMARY KEY (category_pk)
) WITHOUT ROWID;

INSERT INTO categories VALUES
("1", "Classic Literature"),
("2", "Fiction");


-- #################################
-- Lookup table

DROP TABLE IF EXISTS books_format;

CREATE TABLE books_format (
    book_fk         TEXT,
    format_type     TEXT,
    FOREIGN KEY (book_fk) REFERENCES books(book_pk),
    PRIMARY KEY (book_fk, format_type) -- Composite key
) WITHOUT ROWID;

INSERT INTO books_format VALUES
("1", "Hardcover"),
("1", "Paperback"),
("1", "Ebook"),
("2", "Hardcover"),
("2", "Paperback");


-- #################################
-- Junction table for books and authors

DROP TABLE IF EXISTS book_authors;

CREATE TABLE book_authors (
    book_fk         TEXT,
    author_fk       TEXT,
    FOREIGN KEY (book_fk) REFERENCES books(book_pk),
    FOREIGN KEY (author_fk) REFERENCES authors(author_pk), 
    PRIMARY KEY (book_fk, author_fk) -- Compound key
) WITHOUT ROWID;

INSERT INTO book_authors VALUES
("1", "1"),
("2", "2");



-- #################################
-- Junction table for books and categories

DROP TABLE IF EXISTS book_categories;

CREATE TABLE book_categories (
    book_fk         TEXT,
    category_fk     TEXT,
    FOREIGN KEY (book_fk) REFERENCES books(book_pk), 
    FOREIGN KEY (category_fk) REFERENCES categories(category_pk), 
    PRIMARY KEY (book_fk, category_fk) -- Compound key
) WITHOUT ROWID;

INSERT INTO book_categories VALUES
("1", "1"),
("2", "1");

-- #################################

-- Select from primary entities first
SELECT * FROM books;
SELECT * FROM publishers;
SELECT * FROM authors;
SELECT * FROM categories;

-- Then from junction and lookup tables
SELECT * FROM books_format;
SELECT * FROM book_authors;
SELECT * FROM book_categories;





-- #################################
-- Full Text Search

-- Create the FTS5 virtual table for full-text search
DROP TABLE IF EXISTS books_fts;

CREATE VIRTUAL TABLE books_fts USING fts5(
    book_pk,
    book_name,
    content='books',
    content_rowid='book_pk'
);

-- Populate the FTS5 virtual table with data from the books table
INSERT INTO books_fts (book_pk, book_name)
SELECT book_pk, book_name FROM books;

-- Perform a full-text search for the term "Gatsby"
SELECT books.*
FROM books
JOIN books_fts ON books.book_pk = books_fts.book_pk
WHERE books_fts MATCH 'Gatsby';






-- #################################
-- Triggers

-- Trigger that will update the last_updated column whenever a book is updated
CREATE TRIGGER IF NOT EXISTS update_last_updated
AFTER UPDATE ON books
FOR EACH ROW
BEGIN
    UPDATE books SET last_updated = CURRENT_TIMESTAMP WHERE book_pk = OLD.book_pk;
END;

-- Trigger that will  auto-increment book_version on book_name update
CREATE TRIGGER IF NOT EXISTS auto_increment_book_version
BEFORE UPDATE OF book_name ON books
FOR EACH ROW
BEGIN
    UPDATE books SET book_version = OLD.book_version + 1 WHERE book_pk = NEW.book_pk;
END;

UPDATE books SET book_name = 'The Great Gatsby - Version 2' WHERE book_pk = '1';

SELECT * FROM books;






-- #################################
-- Views

-- Create a view that combines the books and publishers tables
CREATE VIEW IF NOT EXISTS BookPublisherView AS
SELECT b.book_pk, b.book_name, b.book_version, p.publisher_name
FROM books b
JOIN publishers p ON b.publisher_fk = p.publisher_pk;

SELECT * FROM BookPublisherView;

-- Create a view that combines the books, authors, and book_authors tables
CREATE VIEW IF NOT EXISTS BookAuthorView AS
SELECT b.book_pk, b.book_name, a.author_name
FROM books b
JOIN book_authors ba ON b.book_pk = ba.book_fk
JOIN authors a ON ba.author_fk = a.author_pk;

SELECT * FROM BookAuthorView;





-- #################################
-- Union - Combine author and publisher names

SELECT author_name AS name FROM authors
UNION
SELECT publisher_name AS name FROM publishers;


-- Group by - Count the number of books for each format type

SELECT format_type, COUNT(book_fk) AS book_count
FROM books_format
GROUP BY format_type;


-- Having - Count the number of books for each format type and filter out those with only 1 book

SELECT format_type, COUNT(book_fk) AS book_count
FROM books_format
GROUP BY format_type
HAVING book_count > 1;





-- #################################
-- Native SQLite joins

-- Inner join - Combines rows from books and publishers where the publisher_fk in books matches the publisher_pk in publishers. Only rows with matching values in both tables are returned.
SELECT b.book_pk, b.book_name, p.publisher_name 
FROM books b --alias 
INNER JOIN publishers p
ON b.publisher_fk = p.publisher_pk;


-- Left join - Combines all rows from books with the matching rows from publishers. If there is no match, the result is NULL on the right side.
SELECT b.book_name, p.publisher_name
FROM books b
LEFT JOIN publishers p
ON b.publisher_fk = p.publisher_pk;

-- Cross join - Combines all rows from books with all rows from authors, resulting in a Cartesian product. Every possible combination of book_name and author_name is returned.
SELECT b.book_name, a.author_name  
FROM books b
CROSS JOIN authors a;







-- #################################
-- Other joins - simulated in SQLite

-- Simulated RIGHT JOIN - Finding all authors and their books, ensuring all authors are listed even if they have no books.
SELECT a.author_name, b.book_name
FROM authors a
LEFT JOIN book_authors ba ON a.author_pk = ba.author_fk
LEFT JOIN books b ON ba.book_fk = b.book_pk;

-- Simulated FULL OUTER JOIN - Combining all books with all authors, even if there are books without authors and authors without books.
SELECT b.book_name, a.author_name
FROM books b
LEFT JOIN book_authors ba ON b.book_pk = ba.book_fk
LEFT JOIN authors a ON ba.author_fk = a.author_pk
UNION
SELECT b.book_name, a.author_name
FROM authors a
LEFT JOIN book_authors ba ON a.author_pk = ba.author_fk
LEFT JOIN books b ON ba.book_fk = b.book_pk;


-- Simulated SELF JOIN - Find pairs of books published by the same publisher
SELECT b1.book_name AS Book1, b2.book_name AS Book2, p.publisher_name
FROM books b1
JOIN books b2 ON b1.publisher_fk = b2.publisher_fk AND b1.book_pk != b2.book_pk
JOIN publishers p ON b1.publisher_fk = p.publisher_pk;


