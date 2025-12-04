#!/usr/bin/env python
# coding: utf-8

# קודים של הקדמה
# 

# In[1]:


import os
import sys
import pandas as pd
import geopandas as gpd


# In[2]:


cwd = os.getcwd()

create_forecast_basic_folder_path = os.path.dirname(cwd)

sys.path.append(create_forecast_basic_folder_path)


# In[3]:


from global_functions import get_newest_date_file, up_load_shp, up_load_df, drop_geo


# להעלות את הטבלה של גורי
# 

# In[4]:


col=['sector', 'geometry', 'ele_stu', 'mid_stu', 'high_stu']


# In[5]:


shcl=up_load_shp(r"{}\background_files\education.shp".format(cwd))[col] #לסנן רק את השכבות שצריך בלי גנים


# העלת שכבת טאז
# 

# In[6]:


col=['Taz_num','Taz_name','main_secto','Muni_Heb','zonetype','geometry']


# In[7]:


taz=up_load_shp(r'{}'.format(new_layer_path))


# In[8]:


taz['sector_for_students']=taz['main_secto']


# In[9]:


sector_of_arabs=['arabs_behined_seperation_wall','Arab']


# In[10]:


taz.loc[taz['main_secto'].isin(sector_of_arabs),'sector_for_students']='arab'


# להחבר לגיאוגרפיה ולהוריד אזורים שמחוץ לתחום שלנו
# 

# In[11]:


taz_without_palestinian=taz.loc[taz['main_secto']!='Palestinian']


# In[12]:


shcl_with_taz=gpd.sjoin(taz_without_palestinian,shcl).drop(columns='geometry')


# לסכום לפי אזור תנועה ומגזר
# 

# לשנות את השמות עמודות לפי איך שאני מודלים צריכים
# 

# In[13]:


old_col=['ele_stu','mid_stu','high_stu']


# In[14]:


shcl_with_taz_arab=shcl_with_taz.loc[shcl_with_taz['sector']==1].pivot_table(index='Taz_num',aggfunc=sum)[old_col]


# In[15]:


new_col=['ARA1','ARA2','ARA3']


# In[16]:


shcl_with_taz_arab.columns=new_col


# In[17]:


shcl_with_taz_hardi=shcl_with_taz.loc[shcl_with_taz['sector']==2].pivot_table(index='Taz_num',aggfunc=sum)[old_col]


# In[18]:


new_col=['UOA1','UOA2','UOA3']


# In[19]:


shcl_with_taz_hardi.columns=new_col


# In[20]:


shcl_with_taz_Jewish=shcl_with_taz.loc[shcl_with_taz['sector']==3].pivot_table(index='Taz_num',aggfunc=sum)[old_col]


# In[21]:


new_col=['SEA1','SEA2','SEA3']


# In[22]:


shcl_with_taz_Jewish.columns=new_col


# In[23]:


taz_students=taz.merge(shcl_with_taz_Jewish.reset_index(), on='Taz_num', how='left') \
   .merge(shcl_with_taz_hardi.reset_index(), on='Taz_num', how='left') \
   .merge(shcl_with_taz_arab.reset_index(), on='Taz_num', how='left') \

taz_students=taz_students.fillna(0)


# In[24]:


# Columns to be summed
columns_to_sum = [
    'SEA1',
    'SEA2',
    'SEA3',
    'UOA1',
    'UOA2',
    'UOA3',
    'ARA1',
    'ARA2',
    'ARA3'
]

# Sum the values across each row for the selected columns
taz_students['student_gov'] = taz_students[columns_to_sum].sum(axis=1)


# מהשוואה אל נתוני משרד החינוך ברמת רשות אני יודע שחסר לי תלמידים ברשויות מסויימים
# אני צריך לפזר את התלמידים שחסרים לי
# השיטה לפיזור בהתאם לביקוש לחינוך
# 

# In[25]:


#העלה של נתוני אנשים התפלגות גילים שנוצר לפני הקוד הזה
path=r'{}\Intermediates'.format(cwd)
taz_with_pop=up_load_df(path,'taz_with_pop_info')


# In[26]:


#לחשב ביקוש בהתאם למקדמים לכל שנתון
taz_with_pop['student_demand']=taz_with_pop['pop_5']/5*4+taz_with_pop['pop_10']+taz_with_pop['pop_15']/5*3


# אחוז מתוך הביקוש
# 

# In[27]:


taz_students_with_demand=taz_students.merge(taz_with_pop[['Taz_num','student_demand']],on='Taz_num',how='left')


# In[28]:


taz_students_with_demand=taz_students_with_demand.fillna(0)


# In[29]:


taz_students_with_demand['student_demand_left']=taz_students_with_demand['student_demand']-taz_students_with_demand['student_gov']
taz_students_with_demand.loc[taz_students_with_demand['student_demand_left']<0,'student_demand_left']=0


# In[30]:


# Group by 'Muni_Heb' and 'main_secto', then calculate the sum for each group
sum_students_by_demand_by_muni_sector=drop_geo(taz_students_with_demand).groupby(by=['Muni_Heb', 'sector_for_students'])[['student_demand_left']].sum().reset_index()


# In[31]:


muni_to_keep=['ביתר עילית','מודיעין עילית','ירושלים'] #אלו הרשויות שאני רוצה להוסיף תלמידים


# In[32]:


sum_students_by_muni_sector_demand_add_from_gov_by_muni=sum_students_by_demand_by_muni_sector.loc[sum_students_by_demand_by_muni_sector['Muni_Heb'].isin(muni_to_keep)]


# In[33]:


filter_condition = sum_students_by_muni_sector_demand_add_from_gov_by_muni['Muni_Heb'] == 'ביתר עילית'
sum_students_by_muni_sector_demand_add_from_gov_by_muni.loc[filter_condition, 'sum_add_students'] = 3000
filter_condition = sum_students_by_muni_sector_demand_add_from_gov_by_muni['Muni_Heb'] == 'מודיעין עילית'
sum_students_by_muni_sector_demand_add_from_gov_by_muni.loc[filter_condition, 'sum_add_students'] = 10000
filter_condition = (sum_students_by_muni_sector_demand_add_from_gov_by_muni['Muni_Heb'] == 'ירושלים') & (sum_students_by_muni_sector_demand_add_from_gov_by_muni['sector_for_students'] == 'U_Orthodox')
sum_students_by_muni_sector_demand_add_from_gov_by_muni.loc[filter_condition, 'sum_add_students'] = 20000
filter_condition = (sum_students_by_muni_sector_demand_add_from_gov_by_muni['Muni_Heb'] == 'ירושלים') & (sum_students_by_muni_sector_demand_add_from_gov_by_muni['sector_for_students'] == 'arab')
sum_students_by_muni_sector_demand_add_from_gov_by_muni.loc[filter_condition, 'sum_add_students'] = 5000


# In[34]:


sum_students_by_muni_sector_demand_add_from_gov_by_muni=sum_students_by_muni_sector_demand_add_from_gov_by_muni.fillna(0)


# In[35]:


# Rename the column 'student_demand_left' to 'sum_student_demand_left'
sum_students_by_muni_sector_demand_add_from_gov_by_muni.rename(columns={'student_demand_left': 'sum_student_demand_left'}, inplace=True)


# In[36]:


taz_students=taz_students.merge(sum_students_by_muni_sector_demand_add_from_gov_by_muni,on=['Muni_Heb','sector_for_students'],how='left').fillna(0)


# In[37]:


taz_students=taz_students.merge(taz_students_with_demand[['Taz_num','student_demand_left']],on='Taz_num',how='left').fillna(0)


# In[38]:


taz_students['add_students_from_gov_by_muni']=taz_students['student_demand_left']/taz_students['sum_student_demand_left']*taz_students['sum_add_students']
taz_students=taz_students.fillna(0)


# זה היה הוספה של סך הכל תלמידים אבל את הסך הכל צריך להוסיף לעמודות שמפצלות לפי שכבה
# 

# In[39]:


# Filter rows where 'sector_for_students' is 'sector' and update the 'ARA1' column
sector_filter = taz_students['sector_for_students'] == 'arab'


# List of columns to be updated
columns_to_update = ['ARA1', 'ARA2', 'ARA3']

# Iterate over each column and perform the operation
for column in columns_to_update:
    # Perform the operation for each column
    taz_students.loc[sector_filter, column] += taz_students['add_students_from_gov_by_muni'] / 3


# In[40]:


# Filter rows where 'sector_for_students' is 'sector' and update the 'ARA1' column
sector_filter = taz_students['sector_for_students'] == 'U_Orthodox'

# List of columns to be updated
columns_to_update = ['UOA1', 'UOA2', 'UOA3']

# Iterate over each column and perform the operation
for column in columns_to_update:
    # Perform the operation for each column
    taz_students.loc[sector_filter, column] += taz_students['add_students_from_gov_by_muni'] / 3


# In[46]:


save_taz_path=r'{}\Intermediates'.format(cwd)
taz_students.to_excel(r'{}\taz_with_gov_students.xlsx'.format(save_taz_path))


# In[47]:


taz_with_pop['kollim_demand']=(taz_with_pop['pop_20']*0.8+taz_with_pop['pop_25']*0.65+taz_with_pop['pop_30']*0.30+taz_with_pop['pop_35']*0.30+taz_with_pop['pop_40']*0.30+taz_with_pop['pop_45']*0.20+taz_with_pop['pop_50']*0.20+taz_with_pop['pop_55']*0.20+taz_with_pop['pop_60']*0.20)*0.5 #הכפלה בחצי בשביל לקבל אוכלוסיית גברים מעורכת


# In[48]:


save_taz_path=r'{}\Intermediates'.format(cwd)
taz_with_pop.to_excel(r'{}\taz_with_kollim_demand.xlsx'.format(save_taz_path))

