from bottle import run, get # type: ignore

@get("/")
def _():
    return "Database Exam - Go to 0.0.0.0:8529"

run(host="0.0.0.0", port=80, debug=True, reloader=True)