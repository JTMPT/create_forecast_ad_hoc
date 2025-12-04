#!/usr/bin/env python
# coding: utf-8

# <span style="color:red; font-family:Helvetica Neue, Helvetica, Arial, sans-serif; font-size:2em;">An Exception was encountered at '<a href="#papermill-error-cell">In [9]</a>'.</span>

# In[1]:


# Parameters
output_folder_path = "W:\\Projects\\\u05d1\u05d4\u05ea\\\u05de\u05d8\u05d4_\u05d1\u05e0\u05d9\u05de\u05d9\u05df_261\\\u05e7\u05d1\u05e6\u05d9 \u05e2\u05d1\u05d5\u05d3\u05d4\\\u05ea\u05d7\u05d6\u05d9\u05d5\u05ea_\u05d3\u05de\u05d5\u05d2\u05e8\u05e4\u05d9\u05d5\u05ea\\For_approval\\Reference_tabels"
new_layer_path = "W:\\Projects\\\u05d1\u05d4\u05ea\\\u05de\u05d8\u05d4_\u05d1\u05e0\u05d9\u05de\u05d9\u05df_261\\\u05e7\u05d1\u05e6\u05d9 \u05e2\u05d1\u05d5\u05d3\u05d4\\\u05ea\u05d7\u05d6\u05d9\u05d5\u05ea_\u05d3\u05de\u05d5\u05d2\u05e8\u05e4\u05d9\u05d5\u05ea\\For_approval\\Reference_tabels\\shp\\TAZ_V4_241103_with_geo_info.shp"


# ### ייבוא ספריות
# 

# In[2]:


params = {"output_folder_path": output_folder_path, "new_layer_path": new_layer_path}
print(params)


# In[3]:


import os
import sys


# In[4]:


def delete_folder_contents(folder_path):
    """
    Deletes all files and subfolders inside the given folder,
    except for README.md.
    """
    for filename in os.listdir(folder_path):

        # Skip README.md
        if filename.lower() == "readme.md":
            continue

        file_path = os.path.join(folder_path, filename)

        if os.path.isfile(file_path):
            os.remove(file_path)

        elif os.path.isdir(file_path):
            delete_folder_contents(file_path)
            os.rmdir(file_path)


# ### הגדרת נתיב תיקייה ומחיקת תוכן
# 

# In[5]:


# מגדיר את הנתיב לתיקייה בשם "Intermediates".
folder_path = './Intermediates'

# קורא לפונקציה delete_folder_contents כדי למחוק את התוכן של התיקייה
delete_folder_contents(folder_path)


# ### הגדרת נתיבים וייבוא מודולים
# 

# In[6]:


# cwd: מאחסן את הנתיב הנוכחי.
cwd = os.getcwd()

# create_forecast_basic מגדיר נתיב לתיקית
create_forecast_basic_folder_path = os.path.dirname(cwd)

# arab_and_palestinian מגדיר נתיב לתיקית
arab_and_palestinian_directory = r'{}\arab_and_palestinian'.format(create_forecast_basic_folder_path)

# מוסיף את הנתיב של התיקייה "arab_and_palestinian", כך שניתן לייבא מודולים מהתיקייה הזו.
sys.path.append(arab_and_palestinian_directory)

# מייבא את המודול run_arab_and_palestinian הנמצא בתיקייה "arab_and_palestinian".
import run_arab_and_palestinian


# ### הרצת מחברות
# 

# In[7]:


get_ipython().run_line_magic('run', '"./fix_cbs_data_230717.ipynb"')
get_ipython().run_line_magic('run', '"./from_sa_cbs_to_ta_jtmt.ipynb"')
get_ipython().run_line_magic('run', '"./create_gov_student_num_by_muni.ipynb"')
get_ipython().run_line_magic('run', '"./prepare_students.ipynb"')


# In[8]:


# os.chdir(arab_and_palestinian_directory): משנה את הספרייה הנוכחית לספרייה שבה נמצאת המחברת הראשונה.
os.chdir(arab_and_palestinian_directory)

# קורא לפונקציה run_notebook שבמודול run_arab_and_palestinian כדי להריץ את המחברת run_arab_and_palestinian.ipynb.
run_arab_and_palestinian.run_notebook(r'{}\run_arab_and_palestinian.ipynb'.format(arab_and_palestinian_directory), params)


# <span id="papermill-error-cell" style="color:red; font-family:Helvetica Neue, Helvetica, Arial, sans-serif; font-size:2em;">Execution using papermill encountered an exception here and stopped:</span>

# In[9]:


# os.chdir(cwd): מחזיר את הספרייה הנוכחית לספרייה המקורית.
os.chdir(cwd)

# הרצת מחברות
get_ipython().run_line_magic('run', '"./emp_current_year.ipynb"')
get_ipython().run_line_magic('run', '"./add_geo_info_and_export.ipynb"')
get_ipython().run_line_magic('run', '"./Determining_type_of_age_distribution_230719.ipynb"')

