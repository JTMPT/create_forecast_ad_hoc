#!/usr/bin/env python
# coding: utf-8

# ### קוד מבוא

# #### ספריות

# In[1]:


import os
import sys
import pandas as pd


# In[2]:


pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.options.display.float_format = '{:.4f}'.format
pd.set_option('display.float_format',  '{:,.2f}'.format)


# #### העלאת משתנים להרצת הקוד

# In[3]:


cwd = os.getcwd()

create_forecast_basic_folder_path = os.path.dirname(cwd)

sys.path.append(create_forecast_basic_folder_path)


# ### פונקציות

# ### פונקציות גלובליות

# In[4]:


from global_functions import up_load_shp, up_load_df


# ### העלאת שכבת אזורי תנועה ישנים

# In[5]:


taz16=up_load_shp(r'{}\background_files\ezorey_tnua_600_2015_ITM.shp'.format(cwd))

taz16['taz']=taz16['TAZ_Num'].astype(str).astype(int)


# ### העלאת טבלת תחזיות ערבים מחוז ירושלים

# In[6]:


taz_arab_demo=up_load_df(r'{}\background_files'.format(cwd), '‏‏ArabTAZ_in_jeru_dis_after_jtmt')


# In[7]:


year=["2020",
"2025",
"2030",
"2035",
"2040",
"2045",
"2050"]

for y in year:
    taz_arab_demo['pop_{}'.format(y)]=taz_arab_demo['זכרים {}'.format(y)]+taz_arab_demo['נקבות {}'.format(y)]

    locals()['taz_arab_demo_age_{}'.format(y)]=pd.pivot_table(taz_arab_demo,columns='Age',values='pop_{}'.format(y),index='taz',aggfunc='sum')

    locals()['taz_arab_demo_age_{}'.format(y)]=locals()['taz_arab_demo_age_{}'.format(y)].apply(lambda row: row / row.sum(), axis=1).round(2).fillna(0).reset_index()

    col_new=['taz','pop_0','pop_10','pop_15','pop_20','pop_25','pop_30','pop_35','pop_40','pop_45','pop_5','pop_50','pop_55','pop_60','pop_65','pop_70','pop_75up']

    locals()['taz_arab_demo_age_{}'.format(y)].columns=col_new


# לייצר גידול שנתי

# In[8]:


taz_arab_demo=pd.pivot_table(taz_arab_demo,index='taz',aggfunc=sum)[['pop_2020',
 'pop_2025',
 'pop_2030',
 'pop_2035',
 'pop_2040',
 'pop_2045',
 'pop_2050']]


# In[9]:


add_year=['2025', '2030', '2035', '2040', '2045', '2050']

x=2020
for y in add_year:
    taz_arab_demo['precent_add_pop_{}'.format(y)]=taz_arab_demo['pop_{}'.format(y)]/taz_arab_demo['pop_{}'.format(str(x))]
    taz_arab_demo['precent_add_pop_{}'.format(y)]=taz_arab_demo['precent_add_pop_{}'.format(y)].round(2)
    taz_arab_demo['precent_add_pop_{}'.format(y)].fillna(0)
    x+=5


# In[10]:


taz_arab_demo=taz_arab_demo.fillna(0).reset_index()


# ### חיבור בין הטבלה לשכבה של דמוגרף 

# In[11]:


taz16_info=pd.merge(taz16[['taz','geometry']],taz_arab_demo,on='taz')


# In[12]:


col_age=['pop_0','pop_10','pop_15','pop_20','pop_25','pop_30','pop_35','pop_40','pop_45','pop_5','pop_50','pop_55','pop_60','pop_65','pop_70','pop_75up']

for y in add_year:
    col_age_new = col_age[:] 
    col_age_new.append('precent_add_pop_{}'.format(y))
    pd.merge(taz16_info,locals()['taz_arab_demo_age_{}'.format(y)],how='left',on='taz').dissolve(by=col_age_new)[['geometry']].reset_index().to_file(r'{}\Intermediates\pre_demo_growth_dislov_{}.shp'.format(cwd,y))

