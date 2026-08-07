from __future__ import annotations

import os
from typing import Any

from flask import Flask, jsonify, render_template, request

from model_utils import InsuranceModelService

app = Flask(__name__, template_folder="templates", static_folder="static", static_url_path="/static")
service = InsuranceModelService(storage_path=os.getenv("PREDICTION_STORE_PATH", ""))
application = app


def _parse_int_value(value: Any, field_name: str, min_value: int = 0, max_value: int | None = None) -> int:
    try:
        parsed = int(float(value))
    except (TypeError, ValueError):
        raise ValueError(f"El campo '{field_name}' debe ser un número entero válido.")

    if parsed < min_value or (max_value is not None and parsed > max_value):
        raise ValueError(f"El campo '{field_name}' debe estar entre {min_value} y {max_value}.")

    return parsed


def _parse_float_value(value: Any, field_name: str, min_value: float = 0.0, max_value: float | None = None) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"El campo '{field_name}' debe ser un número válido.")

    if parsed < min_value or (max_value is not None and parsed > max_value):
        raise ValueError(f"El campo '{field_name}' debe estar entre {min_value} y {max_value}.")

    return parsed


def _validate_payload(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("El cuerpo de la solicitud debe ser un objeto JSON.")

    required_fields = ["age", "sex", "bmi", "children", "smoker", "region"]
    for field in required_fields:
        if field not in payload:
            raise ValueError(f"Falta el campo obligatorio '{field}'.")

    sex = str(payload["sex"]).strip().lower()
    if sex not in {"male", "female", "hombre", "mujer", "0", "1"}:
        raise ValueError("El campo 'sex' debe ser 'male' o 'female'.")

    smoker = str(payload["smoker"]).strip().lower()
    if smoker not in {"yes", "no", "sí", "si", "s", "n", "0", "1"}:
        raise ValueError("El campo 'smoker' debe ser 'yes' o 'no'.")

    region = str(payload["region"]).strip().lower()
    if region not in {"southeast", "southwest", "northeast", "northwest", "sureste", "suroeste", "noreste", "noroeste", "0", "1", "2", "3"}:
        raise ValueError("El campo 'region' debe ser una región válida.")

    return {
        "age": _parse_int_value(payload["age"], "age", min_value=1, max_value=120),
        "sex": sex,
        "bmi": _parse_float_value(payload["bmi"], "bmi", min_value=10.0, max_value=80.0),
        "children": _parse_int_value(payload["children"], "children", min_value=0, max_value=20),
        "smoker": smoker,
        "region": region,
    }


@app.route("/")
def index() -> str:
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict() -> tuple:
    payload = request.get_json(silent=True)

    try:
        validated = _validate_payload(payload or {})
        prediction = service.predict(validated)
        service.append_prediction(validated, prediction)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception:  # pragma: no cover - safety net for unexpected errors
        return jsonify({"error": "Internal server error"}), 500

    return jsonify({"prediction": round(prediction, 2)})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=False)
