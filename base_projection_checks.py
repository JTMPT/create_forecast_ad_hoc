"""
בקרות על התוצר הסופי (base projection / project scenario).

כל בקרה היא פונקציה שמקבלת DataFrame ומחזירה DataFrame של השורות שנכשלו.
DataFrame ריק = הבקרה עברה.

שימוש:
    summary, details = run_all_checks(final_df, base_df=base_proj)
    save_checks_report(summary, details, path)
    raise_if_errors(summary)
"""
import pandas as pd

ERROR = 'ERROR'      # עוצר את הריצה - התוצר לא תקין
WARNING = 'WARNING'  # מדווח בלבד - דורש בדיקה ידנית

AGE_COLS = ['age0_4', 'age5_9', 'age10_14', 'age15_19', 'age20_24', 'age25_29', 'age30_34',
            'age35_39', 'age40_44', 'age45_49', 'age50_54', 'age55_59', 'age60_64', 'age65_69',
            'age70_74', 'age75up']

EMP_COLS = ['indus', 'com_hotel', 'business', 'public', 'education', 'agri']

# העמודות של קובץ BaseProjections (התוצר נבנה מהן ב-delete_and_add_by_TAZ)
REQUIRED_COLS = ['TAZ', 'yosh', 'in_jerusalem_metropolin', 'jerusalem_city', 'sector',
                 'hh_total', 'pop'] + AGE_COLS + ['emp_tot'] + EMP_COLS + [
                 'student', 'univ', 'UO_Hi_Ed', 'pop_emp_employed', 'slope', 'urban']

# עמודות קוד/סיווג - לא כמויות, לכן לא נבדקות בבקרת "שורה של אפסים"
CODE_COLS = ['TAZ', 'yosh', 'in_jerusalem_metropolin', 'jerusalem_city', 'slope', 'urban']

# בשורות פלסטיניות אין פירוק גילאים ו-hh_total, לכן הן מוחרגות מבקרות האוכלוסייה
EXCLUDED_SECTORS = ['Palestinian']


def _without_excluded_sectors(df):
    return df[~df['sector'].isin(EXCLUDED_SECTORS)]


# ---------------------------------------------------------------- בקרות מבנה

def check_required_columns(df):
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    return pd.DataFrame({'missing_column': missing})


def check_unique_taz(df):
    return df[df['TAZ'].duplicated(keep=False)]


def check_no_nulls(df):
    return df[df[REQUIRED_COLS].isna().any(axis=1)]


def check_no_negatives(df):
    num_cols = df[REQUIRED_COLS].select_dtypes('number').columns
    return df[(df[num_cols] < 0).any(axis=1)]


def check_all_zero_row(df, new_taz):
    # רק על אזורי התנועה מהתחזית החדשה - בקובץ הבסיס יש TAZ ריקים לגיטימיים
    df = df[df['TAZ'].isin(new_taz)]
    num_cols = [c for c in df[REQUIRED_COLS].select_dtypes('number').columns if c not in CODE_COLS]
    return df.loc[(df[num_cols] == 0).all(axis=1), ['TAZ', 'sector']]


# ---------------------------------------------------------------- בקרות עקביות

def check_pop_equals_age_sum(df, tolerance=15):
    # טולרנס בגלל עיגולים - בקובץ הבסיס יש סטייה של עד ~13
    df = _without_excluded_sectors(df)
    df = df.assign(age_sum_diff=(df['pop'] - df[AGE_COLS].sum(axis=1)).abs())
    return df.loc[df['age_sum_diff'] > tolerance, ['TAZ', 'sector', 'pop', 'age_sum_diff']]


def check_emp_tot_equals_emp_sum(df, tolerance=5):
    df = df.assign(emp_sum_diff=(df['emp_tot'] - df[EMP_COLS].sum(axis=1)).abs())
    return df.loc[df['emp_sum_diff'] > tolerance, ['TAZ', 'sector', 'emp_tot', 'emp_sum_diff']]


def check_pop_without_hh(df):
    df = _without_excluded_sectors(df)
    return df.loc[(df['pop'] > 0) & (df['hh_total'] == 0), ['TAZ', 'sector', 'pop', 'hh_total']]

def check_hh_without_pop(df):
    df = _without_excluded_sectors(df)
    return df.loc[(df['hh_total'] > 0) & (df['pop'] == 0), ['TAZ', 'sector', 'pop', 'hh_total']]


def check_hh_size_range(df, min_size=1, max_size=8):
    df = _without_excluded_sectors(df)
    df = df[df['hh_total'] > 0]
    df = df.assign(hh_size=df['pop'] / df['hh_total'])
    return df.loc[(df['hh_size'] < min_size) | (df['hh_size'] > max_size),
                  ['TAZ', 'sector', 'pop', 'hh_total', 'hh_size']]


# ---------------------------------------------------------------- השוואה לקובץ הבסיס

def check_taz_missing_vs_base(df, base_df):
    return base_df.loc[~base_df['TAZ'].isin(df['TAZ']), ['TAZ', 'sector']]


def check_unchanged_vs_base(df, base_df, new_taz):
    # אזורי תנועה שלא בתחזית החדשה צריכים להגיע כמו שהם מקובץ הבסיס
    cols = [c for c in REQUIRED_COLS if c != 'TAZ']
    old = df[~df['TAZ'].isin(new_taz)].set_index('TAZ')[cols]
    base = base_df.set_index('TAZ')[cols]
    # TAZ שחסר בתוצר נתפס ב-taz_missing_vs_base
    common_taz = base.index.intersection(old.index)
    old, base = old.loc[common_taz], base.loc[common_taz]

    changed = (old != base) & ~(old.isna() & base.isna())
    changed = changed[changed.any(axis=1)]
    return pd.DataFrame({'TAZ': changed.index,
                         'changed_columns': [', '.join(row.index[row]) for _, row in changed.iterrows()]})


# ---------------------------------------------------------------- רישום הבקרות

# (שם, חומרה, תיאור, פונקציה) - להוספת בקרה: לכתוב פונקציה ולהוסיף שורה כאן
CHECKS = [
    ('required_columns', ERROR, 'כל העמודות הנדרשות קיימות', check_required_columns),
    ('unique_taz', ERROR, 'אין TAZ כפול', check_unique_taz),
    ('no_nulls', ERROR, 'אין ערכים חסרים', check_no_nulls),
    ('no_negatives', ERROR, 'אין ערכים שליליים', check_no_negatives),
    ('pop_equals_age_sum', WARNING, 'pop שווה לסכום קבוצות הגיל', check_pop_equals_age_sum),
    ('emp_tot_equals_emp_sum', WARNING, 'emp_tot שווה לסכום ענפי התעסוקה', check_emp_tot_equals_emp_sum),
    ('pop_without_hh', WARNING, 'אין אוכלוסייה ללא משקי בית', check_pop_without_hh),
    ('hh_without_pop', WARNING, 'אין משקי בית ללא אוכלוסייה', check_hh_without_pop),
    ('hh_size_range', WARNING, 'גודל משק בית בטווח סביר', check_hh_size_range),
    
]


def run_all_checks(df, base_df=None, new_taz=None):
    """
    מריץ את כל הבקרות על התוצר.

    Args:
        df: התוצר הסופי
        base_df: קובץ הבסיס (BaseProjections) - להשוואה
        new_taz: רשימת אזורי התנועה מהתחזית החדשה - לבקרות שרלוונטיות רק להם

    Returns:
        summary (DataFrame): שורה לכל בקרה - סטטוס, מספר שורות שנכשלו ודוגמת TAZ
        details (dict): שם בקרה -> DataFrame של השורות שנכשלו (רק לבקרות שלא עברו)
    """
    checks = list(CHECKS)
    if base_df is not None:
        checks.append(('taz_missing_vs_base', ERROR, 'כל ה-TAZ שבקובץ הבסיס קיימים בתוצר',
                       lambda d: check_taz_missing_vs_base(d, base_df)))
    if new_taz is not None:
        checks.append(('all_zero_row', WARNING, 'אין TAZ חדש שכל הערכים הכמותיים בו אפס',
                       lambda d: check_all_zero_row(d, new_taz)))
    if base_df is not None and new_taz is not None:
        checks.append(('unchanged_vs_base', ERROR, 'TAZ שלא בתחזית החדשה זהים לקובץ הבסיס',
                       lambda d: check_unchanged_vs_base(d, base_df, new_taz)))

    summary_rows = []
    details = {}
    for name, severity, description, func in checks:
        try:
            failed = func(df)
            status = 'PASS' if failed.empty else 'FAIL'
        except Exception as e:
            # בקרה שקרסה (למשל עמודה חסרה) נחשבת כשלון ולא עוצרת את שאר הבקרות
            failed = pd.DataFrame({'exception': [repr(e)]})
            status = 'CRASH'

        example_taz = list(failed['TAZ'].head(5)) if 'TAZ' in failed.columns else []
        summary_rows.append({'check': name,
                             'severity': severity,
                             'description': description,
                             'status': status,
                             'n_failed': 0 if status == 'PASS' else len(failed),
                             'example_taz': example_taz})
        if status != 'PASS':
            details[name] = failed

    return pd.DataFrame(summary_rows), details


def save_checks_report(summary, details, path):
    with pd.ExcelWriter(path) as writer:
        summary.to_excel(writer, sheet_name='summary', index=False)
        for name, failed in details.items():
            failed.to_excel(writer, sheet_name=name[:31], index=False)


def raise_if_errors(summary):
    errors = summary[(summary['severity'] == ERROR) & (summary['status'] != 'PASS')]
    if not errors.empty:
        raise ValueError('בקרות שנכשלו: {}'.format(', '.join(errors['check'])))
