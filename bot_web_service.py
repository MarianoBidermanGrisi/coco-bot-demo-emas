from flask import Flask
app = Flask(__name__)

# Aquí irían las rutas de la aplicación web
@app.route('/')
def home():
    return "Bot is running"

if __name__ == "__main__":
    app.run()