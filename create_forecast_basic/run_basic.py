import papermill as pm

def run_notebook(notebook_path, params):
    """
    הרצת מחברת Jupyter עם פרמטרים נתונים.
    
    notebook_path: נתיב למחברת ה-Jupyter.
    params: מילון פרמטרים שיש להעביר למחברת.
    
    מחזירה True אם ההרצה הצליחה, אחרת False.
    """
    try:
        # הפעלת המחברת עם פרמטרים
        output_notebook_path = notebook_path.replace('.ipynb', '_output.ipynb')  # נתיב למחברת הפלט
        pm.execute_notebook(
            notebook_path,  # נתיב למחברת המקורית
            output_notebook_path,  # נתיב לפלט (מחברת חדשה)
            parameters=params  # פרמטרים למחברת
        )
        print(f"Notebook executed successfully: {output_notebook_path}")
        return True
    except Exception as e:
        print(f"Error executing notebook: {str(e)}")
        return False
