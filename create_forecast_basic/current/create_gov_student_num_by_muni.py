#!/usr/bin/env python
# coding: utf-8

# קודים של הקדמה
# 

# In[1]:


import os
import sys
import pandas as pd


# לייצר טבלה עם כמות תלמידים לפי רשות
# 

# In[2]:


cwd = os.getcwd()

create_forecast_basic_folder_path = os.path.dirname(cwd)

sys.path.append(create_forecast_basic_folder_path)


# ### פונקציות
# 

# In[3]:


from global_functions import up_load_shp, up_load_df


# In[4]:


muni_JTMT=up_load_shp(r'{}\background_files\muni_under_JTMT_ITM.shp'.format(cwd))


# In[5]:


col=['CR_PNIM','Muni_Heb']
muni_JTMT=muni_JTMT[col]
muni_JTMT['CR_PNIM']=muni_JTMT['CR_PNIM'].astype(int)


# In[6]:


# Define the directory path
directory_path = r'{}\background_files'.format(cwd)

# # Load each DataFrame separately
df1 = up_load_df(directory_path, 'cbs_student_2020_by_muni_3')
df2 = up_load_df(directory_path, 'cbs_student_2020_by_muni_1')
df3 = up_load_df(directory_path, 'cbs_student_2020_by_muni_2')

# # Concatenate the DataFrames
student_gov_by_muni = pd.concat([df1, df2, df3])


# In[7]:


col=[ 'סמל_יישוב',
 'תלמידים_בבתי_ספר_יסודיים_תש_ף_2019_20',
 'תלמידים_בחטיבות_ביניים_תש_ף_2019_20',
 'תלמידים_בבתי_ספר_תיכוניים_תש_ף_2019_20']

student_gov_by_muni=student_gov_by_muni[col]


# In[8]:


student_gov_by_muni=student_gov_by_muni.merge(muni_JTMT,left_on='סמל_יישוב',right_on='CR_PNIM')
student_gov_by_muni=student_gov_by_muni.drop_duplicates(subset='CR_PNIM',keep='first')


# In[9]:


col=[ 'תלמידים_בבתי_ספר_יסודיים_תש_ף_2019_20',
 'תלמידים_בחטיבות_ביניים_תש_ף_2019_20',
 'תלמידים_בבתי_ספר_תיכוניים_תש_ף_2019_20']


# In[10]:


student_gov_by_muni['student_gov']=student_gov_by_muni[col].sum(axis=1)


# In[14]:


student_gov_by_muni.to_excel('gov_muni_students.xlsx')

