#!/usr/bin/env python
# coding: utf-8

# ### ייבוא ספריות
# 

# In[1]:


import os


# In[ ]:


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

# In[ ]:


# מגדיר את הנתיב לתיקייה בשם "Intermediates".
folder_path = './Intermediates'

# קורא לפונקציה delete_folder_contents כדי למחוק את התוכן של התיקייה
delete_folder_contents(folder_path)


# ### הרצת מחברות
# 

# In[ ]:


get_ipython().run_line_magic('run', '"./palestinian_from_demo_230622.ipynb"')


# In[ ]:


get_ipython().run_line_magic('run', '"./arab_growth_till_2050_from_demo_230618.ipynb"')


# In[ ]:


get_ipython().run_line_magic('run', '"./230709_arab_growth_vs_kibolt.ipynb"')

