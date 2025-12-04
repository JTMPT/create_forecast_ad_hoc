#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Parameters
output_folder_path = "W:\\Projects\\\u05d1\u05d4\u05ea\\\u05de\u05d8\u05d4_\u05d1\u05e0\u05d9\u05de\u05d9\u05df_261\\\u05e7\u05d1\u05e6\u05d9 \u05e2\u05d1\u05d5\u05d3\u05d4\\\u05ea\u05d7\u05d6\u05d9\u05d5\u05ea_\u05d3\u05de\u05d5\u05d2\u05e8\u05e4\u05d9\u05d5\u05ea\\For_approval\\Reference_tabels"
new_layer_path = "W:\\Projects\\\u05d1\u05d4\u05ea\\\u05de\u05d8\u05d4_\u05d1\u05e0\u05d9\u05de\u05d9\u05df_261\\\u05e7\u05d1\u05e6\u05d9 \u05e2\u05d1\u05d5\u05d3\u05d4\\\u05ea\u05d7\u05d6\u05d9\u05d5\u05ea_\u05d3\u05de\u05d5\u05d2\u05e8\u05e4\u05d9\u05d5\u05ea\\For_approval\\Reference_tabels\\shp\\TAZ_V4_241103_with_geo_info.shp"


# ### ייבוא ספריות
# 

# In[2]:


params = {"output_folder_path": output_folder_path, "new_layer_path": new_layer_path}


# In[3]:


import os
import sys


# ### הגדרת נתיבים
# 

# In[4]:


# cwd: מאחסן את הנתיב הנוכחי.
cwd = os.getcwd()

# arab_and_palestinian מגדיר נתיב לתיקית
arab_and_palestinian_directory = r'{}\arab_and_palestinian'.format(cwd)

# current מגדיר נתיב לתיקית
current_directory = r'{}\current'.format(cwd)


# ### הוספת נתיבים
# 

# In[5]:


# מוסיף את הנתיבים של התיקיות השונות, כך שניתן לייבא מודולים מהתיקיות הללו.
sys.path.append(arab_and_palestinian_directory)
sys.path.append(current_directory)


# ### ייבוא מודולים
# 

# In[6]:


# מייבא את המודולים המכילים את הפונקציות להרצת המחברות
import run_current


# ### הרצת מחברות
# 

# In[7]:


# מחליף את הנתיב הנוכחי לתיקייה current
os.chdir(current_directory)

# מריץ את המחברת באמצעות הפונקציה run_notebook
run_current.run_notebook(r'{}\current\run_current.ipynb'.format(cwd), params)

