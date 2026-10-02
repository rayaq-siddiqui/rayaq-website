from datetime import datetime

from flask import Flask, abort, render_template

import jj_docs
import resume_data
import static_assets
from assembly import get_showcase
from weather import get_weather_for_cities

app = Flask(
    __name__,
    static_folder="../frontend/static",
    template_folder="../frontend/templates",
)
# Asset URLs carry the file's mtime, so a deploy that changes a file changes its URL.
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = static_assets.MAX_AGE_SECONDS


@app.url_defaults
def version_static_urls(endpoint, values):
    if endpoint == "static":
        static_assets.add_version(app.static_folder, values)


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


@app.route("/jj", defaults={"slug": None})
@app.route("/jj/<slug>")
def jj(slug):
    html = jj_docs.render(slug, render_template)
    if html is None:
        abort(404)
    return html


@app.route("/health")
def health():
    return {"status": "ok"}, 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000)
