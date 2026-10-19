import os
import re
import sys
import time
import traceback

import nbformat
import papermill as pm
from papermill.exceptions import PapermillExecutionError


class NotebookRunError(Exception):
    """
    שגיאה בהרצת מחברת בשרשרת.
    השורה הראשונה בהודעה היא שרשרת המחברות (run_basic.ipynb -> ... -> המחברת שנכשלה), ושאר השורות הן פרטי השגיאה המקורית.
    """
    pass


# קודי צבע (ANSI) שמופיעים ב-traceback ש-Jupyter שומר כטקסט
_ANSI_RE = re.compile(r'\x1b\[[0-9;]*[A-Za-z]')

# פריים של פונקציה ב-traceback טקסטואלי של IPython, לדוגמה:
# File c:\...\global_functions.py:253, in get_forecast_version_folder_location(file_path)
_FRAME_RE = re.compile(r'^File (.+?):(\d+), in ([^\s(]+)', re.MULTILINE)


# שורת התקדמות, לדוגמה: "[10:02:15]   ▶ fix_cbs_data_230717.ipynb"
_PROGRESS_RE = re.compile(r'^\[\d\d:\d\d:\d\d\] +[▶✔✖⏭] ')


def _strip_ansi(text):
    return _ANSI_RE.sub('', text)


def _format_duration(seconds):
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    return '{}:{:02d}:{:02d}'.format(hours, minutes, seconds) if hours else '{:02d}:{:02d}'.format(minutes, seconds)


def _print_progress(symbol, notebook_name, start_time=None):
    # ▶ = התחלה, ✔ = סיום מוצלח, ✖ = כישלון, ⏭ = דילוג. בסיום/כישלון מוצג גם משך הריצה
    line = '[{}] {} {}'.format(time.strftime('%H:%M:%S'), symbol, notebook_name)
    if start_time is not None:
        line += ' ({})'.format(_format_duration(time.time() - start_time))
    print(line, flush=True)


class _ProgressForwarder:
    """
    מקבל מ-papermill את ההדפסות של המחברת שרצה (בזמן אמת), ומעביר הלאה רק שורות התקדמות.
    כך שורות ההתקדמות של כל הרמות מגיעות עד main, בלי שאר ההדפסות של המחברות.
    כל רמה מוסיפה הזחה, כדי שיראו איזו מחברת רצה בתוך איזו.
    """
    def __init__(self, target):
        self.target = target
        self.buffer = ''

    def write(self, text):
        self.buffer += text
        *lines, self.buffer = self.buffer.split('\n')
        for line in lines:
            if _PROGRESS_RE.match(line):
                time_part, _, rest = line.partition('] ')
                self.target.write('{}]   {}\n'.format(time_part, rest))

    def flush(self):
        self.target.flush()


def _is_library_file(filename):
    # קבצים של ספריות חיצוניות (pandas, IPython וכו') - לא מעניינים לצורך זיהוי הפונקציה
    filename = os.path.normcase(os.path.expanduser(filename))
    return 'site-packages' in filename or filename.startswith(os.path.normcase(sys.base_prefix))


def _prepend_location(location, message):
    # מוסיף מחברת לתחילת השרשרת שבשורה הראשונה, ומשאיר את פרטי השגיאה כמו שהם
    chain, _, details = message.partition('\n')
    return '{} -> {}\n{}'.format(location, chain, details)


def _find_wrapped_error(output_notebook_path):
    """
    papermill מדווח על פלט השגיאה הראשון בתא שנכשל. כש-run_step עוטפת שגיאה של מחברת פנימית,
    השגיאה המקורית מודפסת לפני העטופה - ולכן מחפשים במחברת הפלט את ה-NotebookRunError האחרון.
    """
    try:
        nb = nbformat.read(output_notebook_path, as_version=4)
    except Exception:
        return None
    wrapped = [output.evalue
               for cell in nb.cells
               for output in cell.get('outputs', [])
               if output.get('output_type') == 'error' and output.get('ename') == 'NotebookRunError']
    return wrapped[-1] if wrapped else None


def run_notebook(notebook_path, params):
    """
    הרצת מחברת Jupyter עם פרמטרים נתונים.

    notebook_path: נתיב למחברת ה-Jupyter.
    params: מילון פרמטרים שיש להעביר למחברת.

    מחזירה True אם ההרצה הצליחה.
    אם ההרצה נכשלה - זורקת NotebookRunError עם שם המחברת ופרטי השגיאה, כדי שהשרשרת תיעצר מיד.
    """
    notebook_name = os.path.basename(notebook_path)
    output_notebook_path = notebook_path.replace('.ipynb', '_output.ipynb')  # נתיב למחברת הפלט
    start_time = time.time()
    _print_progress('▶', notebook_name)
    try:
        pm.execute_notebook(
            notebook_path,  # נתיב למחברת המקורית
            output_notebook_path,  # נתיב לפלט (מחברת חדשה)
            parameters=params,  # פרמטרים למחברת
            progress_bar=False,  # הבר סופר רק תאים של המחברת הזו ולא מייצג את ההתקדמות האמיתית
            stdout_file=_ProgressForwarder(sys.stdout)  # מעביר למעלה את שורות ההתקדמות של המחברות הפנימיות
        )
    except PapermillExecutionError as e:
        _print_progress('✖', notebook_name, start_time)

        # השגיאה כבר נעטפה ברמה פנימית יותר (run_step או run_notebook) - רק מוסיפים את שם המחברת הזו לשרשרת
        wrapped_error = _find_wrapped_error(output_notebook_path)
        if wrapped_error is not None:
            raise NotebookRunError(_prepend_location(notebook_name, wrapped_error)) from None

        # השגיאה קרתה ישירות בתא של המחברת הזו - בונים את ההודעה המלאה
        tb_text = _strip_ansi('\n'.join(e.traceback))
        details = ['סוג: {}'.format(e.ename), 'הודעה: {}'.format(e.evalue)]

        # שם הפונקציה מחולץ מטקסט ה-traceback, ולכן מוצג כהערכה בלבד
        user_frames = [m for m in _FRAME_RE.finditer(tb_text) if not _is_library_file(m.group(1))]
        if user_frames:
            file_name, line_no, func_name = user_frames[-1].groups()
            details.append('probably in {} ({}:{})'.format(func_name, os.path.basename(file_name), line_no))

        details.append('קוד התא שנכשל:\n{}'.format(e.source))
        details.append('--- Traceback ---\n{}'.format(tb_text))
        raise NotebookRunError('{}\n{}'.format(notebook_name, '\n'.join(details))) from None

    _print_progress('✔', notebook_name, start_time)
    return True


def run_step(notebook_file, skip_if_exists=None):
    """
    מריצה מחברת באמצעות %run (באותו kernel ועם אותם משתנים, בדיוק כמו %run רגיל).
    אם המחברת נכשלת - זורקת NotebookRunError עם שם המחברת, הפונקציה שבה קרתה השגיאה וה-traceback.

    notebook_file: נתיב למחברת, לדוגמה "./emp_current_year.ipynb".
    skip_if_exists: נתיב לקובץ שהמחברת יוצרת. אם הוא כבר קיים - מדלגים על המחברת ומשתמשים בקובץ הקיים.
    """
    from IPython import get_ipython

    notebook_name = os.path.basename(notebook_file)

    if skip_if_exists is not None and os.path.exists(skip_if_exists):
        _print_progress('⏭', '{} - משתמש בקובץ הקיים {}'.format(notebook_name, skip_if_exists))
        return

    start_time = time.time()
    _print_progress('▶', notebook_name)
    try:
        get_ipython().run_line_magic('run', '"{}"'.format(notebook_file))
    except NotebookRunError as e:
        _print_progress('✖', notebook_name, start_time)
        # מחברת שהורצה מתוך המחברת הזו כבר עטפה את השגיאה - רק מוסיפים את השם לשרשרת
        raise NotebookRunError(_prepend_location(notebook_name, str(e))) from None
    except Exception as e:
        _print_progress('✖', notebook_name, start_time)
        details = ['סוג: {}'.format(type(e).__name__), 'הודעה: {}'.format(e)]

        # הפריים האחרון שאינו של ספרייה חיצונית = המקום בקוד שלנו שבו קרתה השגיאה
        user_frames = [f for f in traceback.extract_tb(e.__traceback__) if not _is_library_file(f.filename)]
        if user_frames:
            frame = user_frames[-1]
            if frame.name == '<module>':
                details.append('מיקום: בקוד התא עצמו (לא בתוך פונקציה)')
            else:
                details.append('פונקציה: {} ({}:{})'.format(frame.name, os.path.basename(frame.filename), frame.lineno))
            if frame.line:
                details.append('שורה שנכשלה: {}'.format(frame.line))

        details.append('--- Traceback ---\n{}'.format(''.join(traceback.format_exception(e))))
        raise NotebookRunError('{}\n{}'.format(notebook_name, '\n'.join(details))) from None

    _print_progress('✔', notebook_name, start_time)
