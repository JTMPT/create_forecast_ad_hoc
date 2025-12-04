#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Parameters
output_folder_path = "W:\\Projects\\\u05d1\u05d4\u05ea\\\u05de\u05d8\u05d4_\u05d1\u05e0\u05d9\u05de\u05d9\u05df_261\\\u05e7\u05d1\u05e6\u05d9 \u05e2\u05d1\u05d5\u05d3\u05d4\\\u05ea\u05d7\u05d6\u05d9\u05d5\u05ea_\u05d3\u05de\u05d5\u05d2\u05e8\u05e4\u05d9\u05d5\u05ea\\For_approval\\Reference_tabels"
new_layer_path = "W:\\Projects\\\u05d1\u05d4\u05ea\\\u05de\u05d8\u05d4_\u05d1\u05e0\u05d9\u05de\u05d9\u05df_261\\\u05e7\u05d1\u05e6\u05d9 \u05e2\u05d1\u05d5\u05d3\u05d4\\\u05ea\u05d7\u05d6\u05d9\u05d5\u05ea_\u05d3\u05de\u05d5\u05d2\u05e8\u05e4\u05d9\u05d5\u05ea\\For_approval\\Reference_tabels\\shp\\TAZ_V4_241103_with_geo_info.shp"


# ### ייבוא ספריות
# 

# In[2]:


import os


# In[3]:


def delete_folder_contents(folder_path):
    # רץ על כל הקבצים והתיקיות בתיקייה.
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        # בודק אם הפריט הוא קובץ או תיקייה.
        if os.path.isfile(file_path):
            # אם הפריט הוא קובץ, מוחק אותו באמצעות os.remove
            os.remove(file_path)
        elif os.path.isdir(file_path):
            # אם הפריט הוא תיקייה, מוחק את התוכן שלה
            delete_folder_contents(file_path)
            # מוחק את התיקייה עצמה באמצעות os.rmdir
            os.rmdir(file_path)


# ### הגדרת נתיב תיקייה ומחיקת תוכן
# 

# In[4]:


# מגדיר את הנתיב לתיקייה בשם "Intermediates".
folder_path = './Intermediates'

# קורא לפונקציה delete_folder_contents כדי למחוק את התוכן של התיקייה
delete_folder_contents(folder_path)


# ### הרצת מחברות
# 

# In[5]:


get_ipython().run_line_magic('run', '"./palestinian_from_demo_230622.ipynb"')


# In[6]:


get_ipython().run_line_magic('run', '"./arab_growth_till_2050_from_demo_230618.ipynb"')


# In[7]:


get_ipython().run_line_magic('run', '"./230709_arab_growth_vs_kibolt.ipynb"')

