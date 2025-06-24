from flask import Flask, render_template
import random

app = Flask(__name__)

fun_gifs = [
    "https://media.giphy.com/media/3o7TKrDwL1Is6vBfQk/giphy.gif",
    "https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif",
    "https://media.giphy.com/media/3o6Zt8zb1f1fFtzPFC/giphy.gif",
    "https://media.giphy.com/media/xT9IgG50Fb7Mi0prBC/giphy.gif",
    "https://media.giphy.com/media/l0HlMOBiF57GzFRpG/giphy.gif"
]

@app.route("/")
def home():
    gif_url = random.choice(fun_gifs)
    return render_template("index.html", gif_url=gif_url)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
