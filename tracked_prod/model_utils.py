from __future__ import annotations

import csv
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
        self.storage_path = Path(storage_path).resolve() if storage_path else None
        self.model: Optional[LinearRegression] = None
        self._initialize()

    def _initialize(self) -> None:
        self._load_or_train_model()
        if self.storage_path:
            self._ensure_storage_file()

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
        df = pd.read_csv(self.data_path, on_bad_lines="skip", engine="python")
        if df.empty:
            raise ValueError("El dataset no contiene filas válidas para entrenar el modelo.")

        df = self._prepare_dataframe(df)

        x = df.drop(columns="charges")
        y = df["charges"]
        x_train, _, y_train, _ = train_test_split(x, y, test_size=0.2, random_state=42)

        reg = LinearRegression()
        reg.fit(x_train, y_train)
        return reg

    def _prepare_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        expected_columns = {"age", "sex", "bmi", "children", "smoker", "region", "charges"}
        if not expected_columns.issubset(df.columns):
            missing = expected_columns.difference(df.columns)
            raise ValueError(f"Missing required columns in dataset: {sorted(missing)}")

        df = df.copy()
        df["sex"] = df["sex"].map({"male": 0, "female": 1}).fillna(0).astype(int)
        df["smoker"] = df["smoker"].map({"yes": 1, "no": 0}).fillna(0).astype(int)
        df["region"] = df["region"].map({"southeast": 0, "southwest": 1, "northeast": 2, "northwest": 3}).fillna(0).astype(int)
        return df

    def _ensure_storage_file(self) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_path.exists():
            self.storage_path.write_text("age,sex,bmi,children,smoker,region,charges\n", encoding="utf-8")

    def predict(self, payload: Dict[str, Any]) -> float:
        if self.model is None:
            raise RuntimeError("The model has not been trained yet.")

        encoded_features = self._encode_features(payload)
        if encoded_features.shape[1] != 6:
            raise ValueError("Invalid feature set for prediction.")

        prediction = self.model.predict(encoded_features)[0]
        return max(float(prediction), 0.0)

    def append_prediction(self, payload: Dict[str, Any], prediction: float) -> None:
        if not self.storage_path:
            return

        row = {
            "age": self._format_integer(payload.get("age")),
            "sex": self._decode_sex(payload.get("sex")),
            "bmi": self._format_numeric(payload.get("bmi")),
            "children": self._format_integer(payload.get("children")),
            "smoker": self._decode_smoker(payload.get("smoker")),
            "region": self._decode_region(payload.get("region")),
            "charges": self._format_charge(prediction),
        }

        with self.storage_path.open("a", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["age", "sex", "bmi", "children", "smoker", "region", "charges"])
            if self.storage_path.stat().st_size == 0:
                writer.writeheader()
            writer.writerow(row)

    def _encode_features(self, payload: Dict[str, Any]) -> pd.DataFrame:
        data = {
            "age": [self._parse_float(payload.get("age"), default=0.0)],
            "sex": [self._encode_sex(payload.get("sex"))],
            "bmi": [self._parse_float(payload.get("bmi"), default=0.0)],
            "children": [self._parse_int(payload.get("children"), default=0)],
            "smoker": [self._encode_smoker(payload.get("smoker"))],
            "region": [self._encode_region(payload.get("region"))],
        }
        return pd.DataFrame(data)[["age", "sex", "bmi", "children", "smoker", "region"]]

    def _encode_sex(self, value: Any) -> int:
        mapping = {
            "male": 0,
            "female": 1,
            "mujer": 1,
            "hombre": 0,
            "0": 0,
            "1": 1,
        }
        return mapping.get(str(value).strip().lower(), 0)

    def _encode_smoker(self, value: Any) -> int:
        mapping = {
            "yes": 1,
            "no": 0,
            "sí": 1,
            "si": 1,
            "s": 1,
            "n": 0,
            "1": 1,
            "0": 0,
        }
        return mapping.get(str(value).strip().lower(), 0)

    def _encode_region(self, value: Any) -> int:
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
        return mapping.get(str(value).strip().lower(), 0)

    def _decode_sex(self, value: Any) -> str:
        mapping = {
            "0": "male",
            "1": "female",
            "male": "male",
            "female": "female",
            "hombre": "male",
            "mujer": "female",
        }
        return mapping.get(str(value).strip().lower(), "male")

    def _decode_smoker(self, value: Any) -> str:
        mapping = {
            "0": "no",
            "1": "yes",
            "no": "no",
            "yes": "yes",
            "n": "no",
            "s": "yes",
            "si": "yes",
            "sí": "yes",
        }
        return mapping.get(str(value).strip().lower(), "no")

    def _decode_region(self, value: Any) -> str:
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
        return mapping.get(str(value).strip().lower(), "southeast")

    def _format_integer(self, value: Any) -> str:
        if value in (None, ""):
            return ""
        return str(int(float(value)))

    def _format_numeric(self, value: Any) -> str:
        if value in (None, ""):
            return ""
        numeric = float(value)
        return str(int(numeric)) if numeric.is_integer() else format(numeric, ".15g")

    def _parse_int(self, value: Any, default: int = 0) -> int:
        try:
            return int(float(value))
        except (TypeError, ValueError):
            return default

    def _parse_float(self, value: Any, default: float = 0.0) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    def _format_charge(self, value: float) -> str:
        return f"{value:.2f}" if value != 0 else "0.00"
