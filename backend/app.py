from datetime import datetime

from flask import Flask, render_template

import resume_data
from weather import get_weather_for_cities

app = Flask(
    __name__,
    static_folder="../frontend/static",
    template_folder="../frontend/templates",
)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/weather")
def weather():
    return render_template(
        "weather.html",
        cities=get_weather_for_cities(),
        today=datetime.now().strftime("%B %-d, %Y"),
    )


@app.route("/resume")
def resume():
    return render_template(
        "resume.html",
        contact=resume_data.CONTACT,
        education=resume_data.EDUCATION,
        experiences=resume_data.EXPERIENCES,
        projects=resume_data.PROJECTS,
        skills=resume_data.SKILLS,
    )


@app.route("/health")
def health():
    return {"status": "ok"}, 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000)
