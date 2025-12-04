#!/usr/bin/env python
# coding: utf-8

# ## הגדרות ומקדים
# 

# ### ספריות
# 

# In[1]:


import os
import sys
import pandas as pd
import geopandas as gpd
import fiona


# In[2]:


pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', lambda x: '%.3f' % x)


# ### העלאת משתנים להרצת הקוד
# 

# In[3]:


cwd = os.getcwd()

create_forecast_basic_folder_path = os.path.dirname(cwd)

sys.path.append(create_forecast_basic_folder_path)


# In[4]:


from global_functions import get_newest_date_file, drop_geo, up_load_shp, up_load_df


# ## פונקציות
# 

# ## העלת שכבות רלוונטים
# 

# In[5]:


path=r'{}\background_files'.format(cwd)
student_chardi_not_gov=up_load_df(path,'מוסדות חינוך של המתבדלים _מעובד')
student_chardi_not_gov = gpd.GeoDataFrame(
    student_chardi_not_gov, geometry=gpd.points_from_xy(student_chardi_not_gov['x'], student_chardi_not_gov['y'],crs=2039))
student_chardi_not_gov=student_chardi_not_gov[['num_students','geometry']]


# In[6]:


taz=up_load_shp(r'{}'.format(new_layer_path))


# In[7]:


path=r'{}\background_files'.format(cwd)
student_arab_not_gov=up_load_df(path,'מוסדות_חינוך_270616')
student_arab_not_gov=student_arab_not_gov.pivot_table(index='Taz_num',aggfunc=sum)[['num_student']]


# In[8]:


needed_col=['Taz_num','SEA1',
 'SEA2',
 'SEA3',
 'UOA1',
 'UOA2',
 'UOA3',
 'ARA1',
 'ARA2',
 'ARA3']


# In[9]:


upload_df_path=r'{}\Intermediates'.format(cwd)
taz_students_gov=up_load_df(upload_df_path,'taz_with_gov_students')[needed_col]


# ## תלמידים לא במשרד החינוך
# 

# In[10]:


taz=taz.merge(taz_students_gov,on='Taz_num',how='left')


# In[11]:


taz=taz.set_index('Taz_num')


# In[12]:


student_chardi_not_gov_with_taz=gpd.sjoin(taz.reset_index(),student_chardi_not_gov)


# In[13]:


taz['student_chardi_not_gov']=drop_geo(student_chardi_not_gov_with_taz).pivot_table(index='Taz_num',aggfunc=sum)[['num_students']]


# In[14]:


taz['student_arab_not_gov']=student_arab_not_gov[['num_student']]


# In[15]:


taz=taz.fillna(0)


# In[16]:


def spilt_student_to_3(df,columns_to_split,columns_to_update):
    for i in columns_to_update:
        df['{}'.format(i)] += df['{}'.format(columns_to_split)] / 3
        return df


# In[17]:


columns_to_update = ['ARA1', 'ARA2', 'ARA3']


# In[18]:


taz=spilt_student_to_3(taz,'student_arab_not_gov',columns_to_update)


# In[19]:


columns_to_update = ['UOA1', 'UOA2', 'UOA3']


# In[20]:


taz=spilt_student_to_3(taz,'student_chardi_not_gov',columns_to_update)


# In[21]:


taz=taz.fillna(0)


# ## סך תלמידים
# 

# In[22]:


taz['TOA1']=taz['SEA1']+taz['UOA1']+taz['ARA1']
taz['TOA2']=taz['SEA2']+taz['UOA2']+taz['ARA2']
taz['TOA3']=taz['SEA3']+taz['UOA3']+taz['ARA3']


# In[23]:


taz['sector_for_chinuc']=taz['main_secto']
taz.loc[taz['sector_for_chinuc']=='arabs_behined_seperation_wall','sector_for_chinuc']='Arab'


# In[24]:


sector_for_loop=['SE','AR','UO']
sector_for_chinuc_for_loop=[ 'Jewish','Arab', 'U_Orthodox']
num_for_loop=['A1','A2','A3']

for sc,s in zip(sector_for_chinuc_for_loop,sector_for_loop):
    for n in num_for_loop:
        taz.loc[taz['sector_for_chinuc']==sc,'{}{}'.format(s,n)]=taz['TO{}'.format(n)]


# In[25]:


columns_to_sum = ['TOA1','TOA2','TOA3']

# Sum the values across each row for the selected columns
taz['student'] = taz[columns_to_sum].sum(axis=1)


# ## השכלה גבוהה
# 

# In[26]:


emp_Education_per_uni_student=0.15


# In[27]:


col=['geometry',
 'Univ_AR',
 'Univ_SE',
 'Univ_UO']


# In[28]:


uni=up_load_df(r'{}\background_files'.format(cwd),'uni_students')
uni = gpd.GeoDataFrame(
    uni, geometry= gpd.GeoSeries.from_wkt(uni['geometry']),crs=4326)
uni=uni.to_crs(crs=2039)
uni=uni.fillna(0)


# In[29]:


employ_high_edu=up_load_df(r'{}\background_files'.format(cwd),'employ_high_edu')
col=['edu_employ',
 'bussines_employ',
 'comm_employ']
employ_high_edu['emp_uni']=employ_high_edu[col].sum(axis=1)
uni=uni.merge(employ_high_edu,on='ID_camp',how='left')


# In[30]:


columns_to_sum = [
 'Univ_AR',
 'Univ_SE',
 'Univ_UO'
]

# Sum the values across each row for the selected columns
uni['univ'] = uni[columns_to_sum].sum(axis=1)


# In[31]:


uni.loc[uni['emp_uni'].isna(),'emp_uni']=uni['univ']*emp_Education_per_uni_student


# In[32]:


uni_students_with_taz=gpd.sjoin(taz[['geometry']].reset_index(),uni)


# In[33]:


col = ['Taz_num',
 'Univ_AR',
 'Univ_SE',
 'Univ_UO','univ','emp_uni']


# In[34]:


uni_students_sum_by_taz=uni_students_with_taz[col].pivot_table(index='Taz_num',aggfunc=sum).reset_index()


# In[35]:


taz=taz.merge(uni_students_sum_by_taz,on='Taz_num',how='left').fillna(0)


# איפוס של אזורי תנועה פלסטניאים
# 

# In[36]:


col=['Univ_AR',
 'Univ_SE',
 'Univ_UO',
 'emp_uni',
 'univ']


# In[37]:


taz.loc[taz['main_secto']=="Palestinian",col]=0


# ## ישיבות
# 

# In[38]:


taz=taz.fillna(0)


# In[39]:


student_yeshiva=up_load_shp(r'{}\background_files\yeshiva.shp'.format(cwd))

student_yeshiva=gpd.sjoin(taz[['Taz_num','geometry']],student_yeshiva)


# In[40]:


student_yeshiva_by_gender_taz=drop_geo(student_yeshiva).pivot_table(index=['Taz_num','gender'],aggfunc=sum).reset_index()


# In[41]:


col=['Taz_num', 'dorms_p00-',
 'dorms_p21-',
 'dorms_p26-',
 'dorms_tota',
 'emp','students']


# In[42]:


student_yeshiva_by_taz=student_yeshiva_by_gender_taz.loc[student_yeshiva_by_gender_taz['gender']=='male'][col]


# In[43]:


student_Seminar_by_taz=student_yeshiva_by_gender_taz.loc[student_yeshiva_by_gender_taz['gender']=='female'][col]


# In[44]:


new_col=['Taz_num','yeshiva_dorms_pop_15', 'yeshiva_dorms_pop_20', 'yeshiva_dorms_pop_25', 'yeshiva_dorms_pop_sum', 'emp_from_Yeshiva_student', 'Yeshiva']

student_yeshiva_by_taz.columns=new_col


# In[45]:


new_col=['Taz_num','Seminar_dorms_pop_15', 'Seminar_dorms_pop_20', 'Seminar_dorms_pop_25', 'Seminar_dorms_pop_sum', 'emp_from_Seminar_student', 'Seminar']

student_Seminar_by_taz.columns=new_col


# In[46]:


taz=taz.merge(student_yeshiva_by_taz,on='Taz_num',how='left').fillna(0)


# In[47]:


taz=taz.merge(student_Seminar_by_taz,on='Taz_num',how='left').fillna(0)


# In[48]:


needed_col=['Taz_num','kollim_demand']


# In[49]:


upload_df_path=r'{}\Intermediates'.format(cwd)
taz_with_kollim_demand=up_load_df(upload_df_path,'taz_with_kollim_demand')[needed_col]

taz=taz.merge(taz_with_kollim_demand,on='Taz_num',how='left').fillna(0)


# In[50]:


taz.loc[taz['main_secto']!='U_Orthodox','kollim_demand']=0  #אל אף שאנחנו יודעים שיש כוללים באזורים שהם לא מוגדרים כחרדים

taz['add_from_kollim_demand']=0


# In[51]:


taz.loc[(taz['main_secto']=='U_Orthodox')&(taz['kollim_demand']>taz['Yeshiva']),'add_from_kollim_demand']=taz['kollim_demand']-taz['Yeshiva']

taz=taz.fillna(0)


# In[52]:


taz['student_yeshiva_and_kollim']=taz['add_from_kollim_demand']+taz['Yeshiva']


# In[53]:


taz['UO_Hi_Ed']=taz['student_yeshiva_and_kollim']+taz['Seminar']


# In[54]:


taz['emp_UO_Hi_Ed']=taz['emp_from_Seminar_student']+taz['emp_from_Yeshiva_student']
taz=taz.fillna(0)


# In[55]:


taz['UNIVENRORTHFEMALE']=taz['Univ_UO']/2+taz['Seminar']
taz['UNIVENRORTHMALE']=taz['Univ_UO']/2+taz['student_yeshiva_and_kollim']


# ## מקדם מועסק חינוך לתלמידים
# 

# מקור לנתוני מועסקים בחינוך ירושלים יהודי :https://jerusaleminstitute.org.il/wp-content/uploads/2021/04/shnaton_G0721.pdf
# 

# ![image.png](attachment:image.png)
# 

# In[62]:


taz['jew']=0
taz.loc[(taz['main_secto']=="Jewish") |( taz['main_secto']=="U_Orthodox"),'jew']=1


# הגעתי עד לכאן - צריך לייצר כמות תעסוקה בישיבות כי כנראה שיש טעות
# 

# In[63]:


emp_from_uni_student_jeru=taz.query('Muni_Heb=="ירושלים" & jew==1 ')[['emp_uni']].sum().item()


# In[64]:


emp_from_Yeshiva_student_jeru=taz.query('Muni_Heb=="ירושלים" & jew==1 ')[['emp_UO_Hi_Ed']].sum().item()


# In[65]:


emp_for_student_jeru_jew=51.1*1000-emp_from_Yeshiva_student_jeru-emp_from_uni_student_jeru


# In[66]:


emp_education_per_student=round(taz.query('Muni_Heb=="ירושלים" & jew==1 ')[['student']].sum().item()/emp_for_student_jeru_jew,2) 


# In[67]:


emp_education_per_student


# In[68]:


taz['emp_from_student']=taz['student']/emp_education_per_student


# In[69]:


taz.loc[taz['main_secto']=="Palestinian",'emp_from_student']=0


# In[70]:


taz['emp_Education']=taz['emp_from_student']+taz['emp_UO_Hi_Ed']+taz['emp_uni']

