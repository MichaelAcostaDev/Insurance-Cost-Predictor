from __future__ import annotations

from flask import Flask, jsonify, render_template, request, send_from_directory

from model_utils import InsuranceModelService

app = Flask(__name__, template_folder="templates", static_folder="static")
service = InsuranceModelService()
application = app


@app.route("/")
def index() -> str:
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict() -> tuple:
    payload = request.get_json(silent=True) or {}

    try:
        prediction = service.predict(payload)
        service.append_prediction(payload, prediction)
    except Exception as exc:  # pragma: no cover - safety net for user-facing validation
        return jsonify({"error": str(exc)}), 400

    return jsonify({"prediction": round(prediction, 2)})


@app.route("/static/<path:filename>")
def serve_static(filename: str):
    return send_from_directory(app.static_folder, filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
