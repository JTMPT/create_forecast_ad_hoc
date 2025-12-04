#!/usr/bin/env python
# coding: utf-8

# ### ספריות
# 

# In[1]:


import os
import sys
import shutil
import pandas as pd


# In[2]:


pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', lambda x: '%.3f' % x)


# ### העלת משתנים להרצת הקוד
# 

# In[3]:


cwd = os.getcwd()

create_forecast_basic_folder_path = os.path.dirname(cwd)

sys.path.append(create_forecast_basic_folder_path)


# ### פונקציות גלובליות
# 

# In[4]:


from global_functions import up_load_shp, up_load_df, drop_geo, change_cols_names


# In[6]:


sen=['base_year']


# ממשיך את הקוד עכשיו שיכלול גם את המאפיינים הגיאוגרפים שעיסא צריך
# 

# In[7]:


#העלה של נתוני אנשים התפלגות גילים שנוצר לפני הקוד הזה
path=r'{}\Intermediates'.format(cwd)
taz=up_load_df(path,'taz_before_add_geo')


# In[8]:


taz['tazSector']=1 #ערבי
taz.loc[taz['main_secto']=='U_Orthodox','tazSector']=2
taz.loc[taz['main_secto']=='Jewish','tazSector']=3
taz.loc[taz['main_secto']=='Palestinian','tazSector']=4


# לייצר פומה
# 

# In[9]:


poly_pumas=up_load_shp(r'{}\background_files\poly_pumas.shp'.format(create_forecast_basic_folder_path))
col_old=['poly_puma',  'F3', 'F2', 'F1', 'geometry']
col_new=['poly_puma',  '3', '2', '1', 'geometry']
poly_pumas=drop_geo(change_cols_names(poly_pumas,col_old,col_new))
pumas_by_poly_sector=poly_pumas.melt(id_vars='poly_puma',var_name='tazSector',value_name='PUMA')
pumas_by_poly_sector['tazSector']=pumas_by_poly_sector['tazSector'].astype(int)


# In[10]:


taz=taz.merge(pumas_by_poly_sector,on=['poly_puma','tazSector'],how='left')


# In[11]:


taz.loc[taz['PUMA']==0,'PUMA']=999
taz.loc[taz['pop']==0,'PUMA']=999
taz.loc[taz['main_secto']=='Palestinian','PUMA']=999
taz.loc[taz['jeru_metro']==0,'PUMA']=999


# פלט של ההיברדי
# 

# In[12]:


#### תאריך
file_date=pd.Timestamp.today().strftime('%y%m%d')


# In[13]:


col_needed=['Taz_num',
'yosh',
'jeru_metro',
'jerusalem_',
'main_secto',
'hh',
'pop',
'pop_0',
'pop_5',
'pop_10',
'pop_15',
'pop_20',
'pop_25',
'pop_30',
'pop_35',
'pop_40',
'pop_45',
'pop_50',
'pop_55',
'pop_60',
'pop_65',
'pop_70',
'pop_75up',
'total_emp',
'Indus',
'Com_hotel',
'Business',
'Public',
'emp_Education',
'agri',
'student',
'univ',
'UO_Hi_Ed',
'pop_emp_employed',
'slope',
'Urban']

col_new_name=['TAZ',
'yosh',
'in_jerusalem_metropolin',
'jerusalem_city',
'sector',
'hh_total',
'pop',
'age0_4',
'age5_9',
'age10_14',
'age15_19',
'age20_24',
'age25_29',
'age30_34',
'age35_39',
'age40_44',
'age45_49',
'age50_54',
'age55_59',
'age60_64',
'age65_69',
'age70_74',
'age75up',
'emp_tot',
'indus',
'com_hotel',
'business',
'public',
'education',
'agri',
'student',
'univ',
'UO_Hi_Ed',
'pop_emp_employed',
'slop',
'urban']


# In[14]:


#### תאריך
file_date=pd.Timestamp.today().strftime('%y%m%d')


# In[15]:


df=change_cols_names(taz, col_needed, col_new_name)


# In[16]:


col_to_int=['TAZ',
'yosh',
'in_jerusalem_metropolin',
'jerusalem_city',
'hh_total',
'pop',
'age0_4',
'age5_9',
'age10_14',
'age15_19',
'age20_24',
'age25_29',
'age30_34',
'age35_39',
'age40_44',
'age45_49',
'age50_54',
'age55_59',
'age60_64',
'age65_69',
'age70_74',
'age75up',
'emp_tot',
'indus',
'com_hotel',
'business',
'public',
'education',
'agri',
'student',
'univ',
'UO_Hi_Ed',
'pop_emp_employed',
'slop',
'urban']


# In[17]:


for c in col_to_int:
    df.loc[:, c] = df.loc[:, c].astype(int)


# DISTRICT
# 

# In[19]:


taz['DISTRICT']=999
taz.loc[(taz['jew']==0)&(taz['main_secto']!='Palestinian'),'DISTRICT']=1
taz.loc[(taz['main_secto']=='U_Orthodox')&(taz['in_jerusal']=='yes'),'DISTRICT']=2
taz.loc[(taz['main_secto']=='Jewish')&(taz['in_jerusal']=='yes'),'DISTRICT']=3
taz.loc[(taz['main_secto']=='Jewish')&(taz['in_jerusal']=='no')&(taz['jeru_metro']==1),'DISTRICT']=5
taz.loc[(taz['main_secto']=='U_Orthodox')&(taz['in_jerusal']=='no')&(taz['jeru_metro']==1),'DISTRICT']=6
taz.loc[taz['pop']==0,'DISTRICT']=999


# In[20]:


col_needed=['Taz_num','Agg_taz_nu','PUMA','DISTRICT','REGION','SCHOOLDIST']

col_new_name=['TAZ','AGG_TAZ','PUMA','DISTRICT','REGION','SCHOOLDISTRICT']


# SED
# 

# In[22]:


col_needed=['Taz_num',
 'Taz_num',
 'hh',
 'PUMA',
 'DISTRICT',
 'county',
 'area',
 'parktot',
 'majunivenr',
 'tazSector',
 'Indus',
 'Com_hotel',
 'Business',
 'Public',
 'emp_Education',
 'agri',
 'total_emp',
 'UOA1',
 'UOA2',
 'UOA3',
 'SEA1',
 'SEA2',
 'SEA3',
 'ARA1',
 'ARA2',
 'ARA3',
 'TOA1',
 'TOA2',
 'TOA3',
 'Univ_AR',
 'Univ_SE',
 'UNIVENRORTHMALE',
 'UNIVENRORTHFEMALE',
 'ieold',
 'superZone',
 'IEProp',
 'Taz1',
 'perScaled',
 'EIProp',
 'CITYCODE1',
 'CITYCODE2',
 'CITYCODE3',
 'CITYCODE4',
 'codeseq',
 'codeseqCon',
 'PaidBuffer',
 'Rest_EmpBu',
 'FreeBuffer',
 'SCHOOLDIST',
 'SCHOOLDIST',
 'highBusine',
 'searchtime',
 'walktime',
 'cost']


# In[23]:


col_new_name=['maz',
 'taz',
 'hh_total',
 'puma',
 'district',
 'county',
 'area',
 'parktot',
 'majunivenr',
 'tazSector',
 'Indus',
 'Com_hotel',
 'Off_Bsness',
 'Public',
 'Education',
 'Agri',
 'totemp',
 'UOA1',
 'UOA2',
 'UOA3',
 'SEA1',
 'SEA2',
 'SEA3',
 'ARA1',
 'ARA2',
 'ARA3',
 'TOA1',
 'TOA2',
 'TOA3',
 'UNIVENRARAB',
 'UNIVENRSEC',
 'UNIVENRORTHMALE',
 'UNIVENRORTHFEMALE',
 'ieold',
 'superZone',
 'IEProp',
 'Taz1',
 'perScaled',
 'EIProp',
 'CITYCODE1',
 'CITYCODE2',
 'CITYCODE3',
 'CITYCODE4',
 'codeseq',
 'codeseqCons',
 'PaidBuffer',
 'Rest_EmpBuffer',
 'FreeBuffer',
 'schDistrict',
 'schDistrictAgg',
 'highBusinessFlag',
 'searchtime',
 'walktime',
 'cost']


# In[25]:


taz.to_excel(r'{}\2020_jtmt_forcast_full_{}_with_taz_changes.xlsx'.format(output_folder_path,file_date),index=False)

