from bottle import run, get, response, delete, put, post, request, template, static_file #type: ignore
import requests
import sqlite3
import pathlib

# SERVING STATIC FILES
##############################
@get("/style.css")
def _():
    return static_file("style.css", ".")


##############################
@get("/<file_name>.js")
def _(file_name):
    return static_file(file_name+".js", ".")


###########################################################################################
# SQLite database connection


def dict_factory(cursor, row):
    col_names = [col[0] for col in cursor.description]
    return {key: value for key, value in zip(col_names, row)}


def db_sqlite():
    try:
        db = sqlite3.connect(str(pathlib.Path(__file__).parent.resolve())+"/database.db")  
        db.row_factory = dict_factory
        return db
    except Exception as ex:
        print(ex)


###########################################################################################
## ARANGODB CONNECTION

def db_arango(query):
    try:
        url = "http://arangodb:8529/_api/cursor"
        res = requests.post( url, json = query )
        print(res)
        print(res.text)
        return res.json()
    
    except Exception as ex:
        print(ex)
        return None
    
    finally:
        pass

###########################################################################################
# Home

@get("/")
def _():
    try:
        # Fetch books from SQLite
        db = db_sqlite()
        q = db.execute("SELECT * FROM books")
        books = q.fetchall()

        # Fetch books from ArangoDB
        arango_books_response = db_arango({
            "query": "FOR book IN books RETURN book"
        })
        arango_books = arango_books_response["result"] if arango_books_response and "result" in arango_books_response else []

        # Render the template with books from both databases
        return template("index.html", books=books, arango_books=arango_books)
    
    except Exception as ex:
        print(ex)
    
    finally:
        if "db" in locals(): db.close()


########################################################################################### 
# ArangoDB
# Get all books
##############################
@get("/arangodb/books")
def _():
    try:
        books = db_arango({
            "query": "FOR book IN books RETURN book"
            })
        
        if books and "result" in books:
            response.content_type = 'application/json'
            return {"status": "success", "data": books["result"]}
        else:
            return {"status": "failure", "message": "Failed to fetch books."}
    
    except Exception as ex:
        print(ex)
    
    finally:
        pass

# Get book by id
##############################

@get("/arangodb/book/<id>")
def _(id):
    try:
        book = db_arango({
            "query": "FOR book IN books FILTER book._key == @id RETURN book",
            "bindVars": { "id": id }
            })
        
        print(book)
        
        if book and "result" in book:
            response.content_type = 'application/json'
            return {"status": "success", "data": book["result"]}
        else:
            return {"status": "failure", "message": "Failed to fetch book."}
    
    except Exception as ex:
        print(ex)
    
    finally:
        pass

# Post book
##############################

@post("/arangodb/book")
def _():
    try:
        data = request.json
        print(data)
        book = db_arango({
            "query": "INSERT @data INTO books RETURN NEW",
            "bindVars": { "data": data }
            })
        
        print(book)
        
        if book and "result" in book:
            response.content_type = 'application/json'
            return {"status": "success", "data": book["result"]}
        else:
            return {"status": "failure", "message": "Failed to add book."}
    
    except Exception as ex:
        print(ex)
    
    finally:
        pass

# Put book by id
##############################

@put("/arangodb/book/<id>")
def _(id):
    try:
        data = request.json
        print(data)
        book = db_arango({
            "query": "UPDATE @id WITH @data IN books RETURN NEW",
            "bindVars": { "id": id, "data": data }
            })
        
        print(book)
        
        if book and "result" in book:
            response.content_type = 'application/json'
            return {"status": "success", "data": book["result"]}
        else:
            return {"status": "failure", "message": "Failed to update book."}
    
    except Exception as ex:
        print(ex)
    
    finally:
        pass
    
# Delete book by id
##############################

@delete("/arangodb/book/<id>")
def _(id):
    try:
        book = db_arango({
            "query": "REMOVE @id IN books RETURN OLD",
            "bindVars": { "id": id }
            })
        
        print(book)
        
        if book and "result" in book:
            response.content_type = 'application/json'
            return {"status": "success", "data": book["result"]}
        else:
            return {"status": "failure", "message": "Failed to delete book."}
    
    except Exception as ex:
        print(ex)
    
    finally:
        pass

run(host="0.0.0.0", port=80, debug=True, reloader=True)