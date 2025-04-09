from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return f"CONTACT MANAGEMENT SYSTEM"

if __name__ == "__main__":
    app.run(debug=True)