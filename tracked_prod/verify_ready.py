from pathlib import Path
from model_utils import InsuranceModelService

# Ensure the model file can be regenerated
model_path = Path('model.joblib')
if model_path.exists():
    model_path.unlink()

service = InsuranceModelService()
print('model trained:', service.model is not None)
print('model file exists:', model_path.exists())
print('prediction:', service.predict({'age': 35, 'sex': 'male', 'bmi': 24.5, 'children': 0, 'smoker': 'no', 'region': 'southeast'}))
