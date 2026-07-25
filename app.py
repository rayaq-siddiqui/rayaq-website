from datetime import datetime

from flask import Flask, render_template

from weather import get_weather_for_cities

app = Flask(__name__, static_folder="static", template_folder="templates")


@app.route("/")
def index():
    return render_template(
        "index.html",
        cities=get_weather_for_cities(),
        today=datetime.now().strftime("%B %-d, %Y"),
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000)
