import os
import shutil
import subprocess
from pathlib import Path

top = Path(__file__).resolve().parent
tracked_dir = top / "tracked_prod"
if tracked_dir.exists():
    shutil.rmtree(tracked_dir)
tracked_dir.mkdir()

result = subprocess.run(["git", "ls-files"], cwd=top, capture_output=True, text=True)
result.check_returncode()
for line in result.stdout.splitlines():
    src = top / line
    dest = tracked_dir / line
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)

print('Copied tracked files to', tracked_dir)
print('Has model.joblib?', (tracked_dir / 'model.joblib').exists())
print('Has insurance.csv?', (tracked_dir / 'insurance.csv').exists())

import sys
sys.path.insert(0, str(tracked_dir))
from model_utils import InsuranceModelService

try:
    service = InsuranceModelService()
    print('Model loaded ok:', service.model is not None)
    print('Predict:', service.predict({'age': 35, 'sex': 'male', 'bmi': 24.5, 'children': 0, 'smoker': 'no', 'region': 'southeast'}))
except Exception as exc:
    import traceback
    traceback.print_exc()
    raise
