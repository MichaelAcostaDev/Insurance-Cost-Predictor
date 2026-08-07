from __future__ import annotations

import csv
import os
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split


class InsuranceModelService:
    def __init__(self, data_path: Optional[str] = None, model_path: Optional[str] = None, storage_path: Optional[str] = None) -> None:
        base_dir = Path(__file__).resolve().parent
        self.data_path = Path(data_path or base_dir / "insurance.csv")
        self.model_path = Path(model_path or base_dir / "model.joblib")
        self.storage_path = Path(storage_path or os.getenv("PREDICTION_STORE_PATH") or self.data_path)
        self.model = None  # type: Optional[LinearRegression]
        self._initialize()

    def _initialize(self) -> None:
        self._ensure_storage_file()
        self._load_or_train_model()

    def _load_or_train_model(self) -> None:
        if self.model_path.exists():
            import joblib

            self.model = joblib.load(self.model_path)
            return

        self.model = self._train_model()
        import joblib

        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, self.model_path)

    def _train_model(self) -> LinearRegression:
        df = pd.read_csv(self.data_path)
        df.replace({"sex": {"male": 0, "female": 1}}, inplace=True)
        df.replace({"smoker": {"yes": 1, "no": 0}}, inplace=True)
        df.replace({"region": {"southeast": 0, "southwest": 1, "northeast": 2, "northwest": 3}}, inplace=True)

        x = df.drop(columns="charges")
        y = df["charges"]
        x_train, _, y_train, _ = train_test_split(x, y, test_size=0.2)

        reg = LinearRegression()
        reg.fit(x_train, y_train)
        return reg

    def _ensure_storage_file(self) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_path.exists():
            self.storage_path.write_text("age,sex,bmi,children,smoker,region,charges\n", encoding="utf-8")

    def predict(self, payload: Dict[str, Any]) -> float:
        if self.model is None:
            raise RuntimeError("The model has not been trained yet.")

        encoded_features = self._encode_features(payload)
        prediction = self.model.predict(encoded_features)[0]
        return max(float(prediction), 0.0)

    def append_prediction(self, payload: Dict[str, Any], prediction: float) -> None:
        row = {
            "age": self._format_age(payload.get("age", "")),
            "sex": self._decode_sex(payload.get("sex", "")),
            "bmi": self._format_value(payload.get("bmi", "")),
            "children": self._format_value(payload.get("children", "")),
            "smoker": self._decode_smoker(payload.get("smoker", "")),
            "region": self._decode_region(payload.get("region", "")),
            "charges": self._format_charge(prediction),
        }

        with self.storage_path.open("a", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["age", "sex", "bmi", "children", "smoker", "region", "charges"])
            if self.storage_path.stat().st_size == 0:
                writer.writeheader()
            writer.writerow(row)

    def _encode_features(self, payload: Dict[str, Any]) -> pd.DataFrame:
        data = {
            "age": [float(payload.get("age", 0))],
            "sex": [self._encode_sex(payload.get("sex", ""))],
            "bmi": [float(payload.get("bmi", 0))],
            "children": [int(payload.get("children", 0))],
            "smoker": [self._encode_smoker(payload.get("smoker", ""))],
            "region": [self._encode_region(payload.get("region", ""))],
        }
        return pd.DataFrame(data)[["age", "sex", "bmi", "children", "smoker", "region"]]

    def _encode_sex(self, value: Any) -> int:
        if isinstance(value, str):
            value = value.lower()
            mapping = {"male": 0, "female": 1, "mujer": 1, "hombre": 0, "0": 0, "1": 1}
            return mapping.get(value, 0)
        return int(value)

    def _encode_smoker(self, value: Any) -> int:
        if isinstance(value, str):
            value = value.lower()
            mapping = {"yes": 1, "no": 0, "sí": 1, "si": 1, "s": 1, "n": 0, "1": 1, "0": 0}
            return mapping.get(value, 0)
        return int(value)

    def _encode_region(self, value: Any) -> int:
        if isinstance(value, str):
            value = value.lower()
            mapping = {
                "southeast": 0,
                "southwest": 1,
                "northeast": 2,
                "northwest": 3,
                "sureste": 0,
                "suroeste": 1,
                "noreste": 2,
                "noroeste": 3,
            }
            return mapping.get(value, 0)
        return int(value)

    def _decode_sex(self, value: Any) -> str:
        if isinstance(value, str):
            value = value.lower()
            mapping = {"0": "male", "1": "female", "male": "male", "female": "female", "hombre": "male", "mujer": "female"}
            return mapping.get(value, "male")
        return "male" if int(value) == 0 else "female"

    def _decode_smoker(self, value: Any) -> str:
        if isinstance(value, str):
            value = value.lower()
            mapping = {"0": "no", "1": "yes", "no": "no", "yes": "yes", "n": "no", "s": "yes", "si": "yes", "sí": "yes"}
            return mapping.get(value, "no")
        return "no" if int(value) == 0 else "yes"

    def _decode_region(self, value: Any) -> str:
        if isinstance(value, str):
            value = value.lower()
            mapping = {
                "0": "southeast",
                "1": "southwest",
                "2": "northeast",
                "3": "northwest",
                "southeast": "southeast",
                "southwest": "southwest",
                "northeast": "northeast",
                "northwest": "northwest",
                "sureste": "southeast",
                "suroeste": "southwest",
                "noreste": "northeast",
                "noroeste": "northwest",
            }
            return mapping.get(value, "southeast")
        return ["southeast", "southwest", "northeast", "northwest"][int(value)]

    def _format_age(self, value: Any) -> str:
        if value in (None, ""):
            return ""
        return str(int(float(value)))

    def _format_value(self, value: Any) -> str:
        if value in (None, ""):
            return ""
        numeric = float(value)
        if numeric.is_integer():
            return str(int(numeric))
        return format(numeric, ".15g")

    def _format_charge(self, value: float) -> str:
        return f"{value:.10f}".rstrip("0").rstrip(".") if value != 0 else "0"
