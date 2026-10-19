import os
import sys

# הפונקציה run_notebook משותפת לכל המחברות ונמצאת ב-create_forecast_basic/notebook_runner.py
# (היא זורקת NotebookRunError עם שם המחברת ופרטי השגיאה אם ההרצה נכשלת)
_create_forecast_basic_folder_path = os.path.dirname(os.path.abspath(__file__))
if _create_forecast_basic_folder_path not in sys.path:
    sys.path.append(_create_forecast_basic_folder_path)

from notebook_runner import run_notebook, NotebookRunError
