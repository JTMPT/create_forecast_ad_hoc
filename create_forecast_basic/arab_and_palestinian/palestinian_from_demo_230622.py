#!/usr/bin/env python
# coding: utf-8

# ### קוד מבוא
# 

# #### ספריות
# 

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
# 

# In[3]:


cwd = os.getcwd()

create_forecast_basic_folder_path = os.path.dirname(cwd)

# create_forecast_basic_folder_path = os.path.dirname(create_forecast_basic_jtmt_folder_path)

sys.path.append(create_forecast_basic_folder_path)


# ### פונקציות
# 

# ### פונקציות גלובליות
# 

# In[4]:


from global_functions import up_load_shp, up_load_df, drop_geo, get_newest_date_file


# ### ביצוע
# 

# #### עיבוד מידע טבלאי של הדמוגרף
# 

# In[5]:


demo=up_load_df(r'{}\background_files'.format(cwd),'‏‏PalestiniansResults_forecast_zone')


# In[6]:


col=['male_2020',
 'female_2020',
 'male_2025',
 'female_2025',
 'male_2030',
 'female_2030',
 'male_2035',
 'female_2035',
 'male_2040',
 'female_2040',
 'male_2045',
 'female_2045',
 'male_2050',
 'female_2050']

demo=demo.pivot_table(index='Proj_Area',aggfunc=sum)[col]


# In[7]:


year=['2020','2025','2030','2035','2040','2045','2050']

for x in year:
    demo['pop_{}'.format(x)]= demo['female_{}'.format(x)]+demo['male_{}'.format(x)]


# #### שכבת אזורי תחזית של דמוגרף
# 

# In[8]:


proj_zones=up_load_shp(r'{}\background_files\proj_zones_pls.shp'.format(cwd))

proj_zones['Proj_Area']=proj_zones['projection']

proj_zones=proj_zones[['Proj_Area', 'geometry']]


# #### חיבור נתוני דמוגרף
# 

# In[9]:


pd.merge(proj_zones,demo,on='Proj_Area',how='right').query('geometry.isna()')


# אנחנו מוכנים לוותר עליהם
# זה ניקוז של כל הבדואיים שאין להם אזור תחזית
# 

# In[10]:


proj_zones=pd.merge(proj_zones,demo,on='Proj_Area',how='left')


# #### שכבת אזורי תנועה
# 

# In[11]:


taz=up_load_shp(r'{}'.format(new_layer_path))

taz=taz.query('main_secto=="Palestinian"')[['Taz_num','geometry']]


# #### שכבת בינוי
# 

# In[12]:


bld=up_load_shp(r'{}\background_files\palestinian_bld_area_pcbs_220710.shp'.format(cwd))

bld=bld.to_crs(2039)

bld=bld.dissolve()

bld=bld[['geometry']]


# #### הצלבת בין בינוי לבין אזורי תחזית ותנועה
# 

# In[13]:


col=['Proj_Area',
 'geometry',
 'pop_2020',
 'pop_2025',
 'pop_2030',
 'pop_2035',
 'pop_2040',
 'pop_2045',
 'pop_2050']

demo_taz_bld=bld.overlay(taz).overlay(proj_zones[col])

demo_taz_bld['small_area']=demo_taz_bld.area

demo_taz_bld=demo_taz_bld.set_index('Proj_Area')

demo_taz_bld['proj_sum_area']=drop_geo(demo_taz_bld).groupby(by='Proj_Area').sum()[['small_area']]

demo_taz_bld['pre_from_proj']=demo_taz_bld['small_area']/demo_taz_bld['proj_sum_area']


# In[14]:


pop_year=['pop_2020',
 'pop_2025',
 'pop_2030',
 'pop_2035',
 'pop_2040',
 'pop_2045',
 'pop_2050']

for y in pop_year:
    demo_taz_bld['{}'.format(y)]=demo_taz_bld['{}'.format(y)]*demo_taz_bld['pre_from_proj']


# בדיקה שלא הומצא כמות אנשים
# 

# In[15]:


demo_taz_bld[pop_year].sum().sum()-proj_zones[pop_year].sum().sum()


# #### סכום אנשים לפי אזורי תנועה
# 

# In[16]:


taz_demo_pls=drop_geo(demo_taz_bld).pivot_table(index='Taz_num',aggfunc=sum)


# In[17]:


add_year=['2025', '2030', '2035', '2040', '2045', '2050']

x=2020

for y in add_year:
    taz_demo_pls['precent_add_pop_{}'.format(y)]=taz_demo_pls['pop_{}'.format(y)]/taz_demo_pls['pop_{}'.format(str(x))]
    taz_demo_pls['precent_add_pop_{}'.format(y)]=taz_demo_pls['precent_add_pop_{}'.format(y)].round(2)
    taz_demo_pls['precent_add_pop_{}'.format(y)].fillna(0)
    x+=5


# #### ייצוא
# 

# In[18]:


col=['pop_2020',
 'precent_add_pop_2025',
 'precent_add_pop_2030',
 'precent_add_pop_2035',
 'precent_add_pop_2040',
 'precent_add_pop_2045',
 'precent_add_pop_2050']


# In[19]:


taz_demo_pls[col].to_excel(r'{}\Intermediates\taz_demo_pls_2020_and_pre_growth_till_2050.xlsx'.format(cwd))

