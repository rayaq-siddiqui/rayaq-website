from datetime import datetime

from flask import Flask, render_template, request

import resume_data
from assembly import get_showcase
from flights import api as flights_api
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
        headline=resume_data.HEADLINE,
        location=resume_data.LOCATION,
        summary=resume_data.SUMMARY,
        education=resume_data.EDUCATION,
        experiences=resume_data.EXPERIENCES,
        projects=resume_data.PROJECTS,
        honors=resume_data.HONORS,
        certifications=resume_data.CERTIFICATIONS,
        skills=resume_data.SKILLS,
    )


@app.route("/assembly-agents")
def assembly_agents():
    return render_template("assembly.html", showcase=get_showcase())


@app.route("/flights")
def flights():
    return render_template("flights.html", **flights_api.page_context(request.args))


@app.route("/api/flights/airports")
def flights_airports():
    return flights_api.airports_response(request.args.get("q", ""))


@app.route("/api/flights/search", methods=["POST"])
def flights_search():
    return flights_api.search_response(
        request.get_json(silent=True),
        client_id=flights_api.client_id(
            request.headers.get("X-Forwarded-For"), request.remote_addr
        ),
    )


@app.route("/api/flights/health")
def flights_health():
    return flights_api.health_response()


@app.route("/health")
def health():
    return {"status": "ok"}, 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000)
