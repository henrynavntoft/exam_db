from bottle import run, get, response, delete, put, post, request #type: ignore
import requests

@get("/")
def _():
    return "Database Exam - Go to 0.0.0.0:8529"



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
        print("Error in db_arango: ", ex)
        return None
    
# ARANGO DB
# CRUD OPERATIONS
########################################################################################################

# Get all users
##############################
@get("/arangodb/users")
def _():
    try:
        # Query to fetch all users
        users = db_arango({
            "query": "FOR user IN users RETURN user"
            })
        
        # Check if users are fetched successfully
        if users and "result" in users:
            # Return the users as JSON
            response.content_type = 'application/json'
            return {"status": "success", "data": users["result"]}
        else:
            return {"status": "failure", "message": "Failed to fetch users."}
    except Exception as ex:
        return x.handle_exception(ex)
    finally:
        pass

# Get user by user_id
##############################
@get("/arangodb/user/<user_id>")
def _(user_id):
    try:
        # Fetch the user from the database
        user = x.db_arango({
            "query": "FOR user IN users FILTER user.user_id == @user_id RETURN user", 
            "bindVars": {"user_id": int(user_id)}
            })
        
        # Check if user is fetched successfully
        if user and "result" in user and user["result"]:
            # Return the user as JSON
            return {"status": "success", "data": user["result"][0]}
        else:
            response.status = 404
            return {"status": "failure", "message": "User not found"}
    except Exception as ex:
        return x.handle_exception(ex)
    finally:
        pass


# Create a new user
##############################
@post("/arangodb/user")
def _():
    try:
        # Get JSON data from request body
        user_data = request.json
        
        # Validate and extract user fields from the JSON data
        user_id = user_data.get("user_id")
        user_name = user_data.get("user_name")
        user_email = user_data.get("user_email")

        # Construct user document
        user = {
            "user_id": user_id,
            "user_name": user_name,
            "user_email": user_email
        }
        
        # Insert user document into ArangoDB
        res = x.db_arango({
            "query": "INSERT @doc IN users RETURN NEW", 
            "bindVars": {"doc": user}
            })
        if res and "result" in res:
            new_user = res["result"][0]
            print("New User Added:", new_user)
            return {"status": "success", "data": new_user}
        else:
            return {"status": "failure", "message": "Failed to insert user."}
    except Exception as ex:
        return x.handle_exception(ex)
    finally:
        pass


# Update user by user_id
##############################
@put("/arangodb/user/<user_id>")
def _(user_id):
    try:
        # Fetch the user data from the request body
        user_data = request.json

        # Check if user data is provided
        if not user_data:
            response.status = 400
            return {"status": "failure", "message": "User data is required"}

        # Fetch the user from the database to check if it exists
        user = x.db_arango({
            "query": "FOR user IN users FILTER user.user_id == @user_id RETURN user",
            "bindVars": {"user_id": int(user_id)}
        })
        
        if not user or "result" not in user or not user["result"]:
            response.status = 404
            return {"status": "failure", "message": "User not found"}

        # Perform the update operation
        update_query = """
            FOR user IN users
            FILTER user.user_id == @user_id
            UPDATE user WITH @user_data IN users
            RETURN NEW
        """
        res = x.db_arango({
            "query": update_query,
            "bindVars": {
                "user_id": int(user_id),
                "user_data": user_data
            }
        })

        if res and "result" in res:
            updated_user = res["result"][0]
            return {"status": "success", "data": updated_user}
        else:
            return {"status": "failure", "message": "Failed to update user"}
    except Exception as ex:
        return x.handle_exception(ex)
    finally:
        pass


# Delete user by user_id
##############################
@delete("/arangodb/user/<user_id>")
def _(user_id):
        try:
        # Fetch the user from the database to check if it exists
            user = x.db_arango({
            "query": "FOR user IN users FILTER user.user_id == @user_id RETURN user", 
            "bindVars": {"user_id": int(user_id)}
            })

            if not user or "result" not in user or not user["result"]:
                response.status = 404
                return {"status": "failure", "message": "User not found"}

            # Perform the delete operation
            delete_query = """
            FOR user IN users
            FILTER user.user_id == @user_id
            REMOVE user IN users
            RETURN OLD
            """
            res = x.db_arango({
            "query": delete_query, 
            "bindVars": {"user_id": int(user_id)}
            })

            if res and "result" in res:
                deleted_user = res["result"][0]
                return {"status": "success", "data": deleted_user}
            else:
                return {"status": "failure", "message": "Failed to delete user"}
        except Exception as ex:
            return x.handle_exception(ex)
        finally:
            pass


    

run(host="0.0.0.0", port=80, debug=True, reloader=True)