#!/usr/bin/env python
# coding: utf-8

# ## הגדרות ומקדים

# ### ספריות

# In[29]:


import os
import sys
import pandas as pd
import geopandas as gpd


# In[30]:


pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', lambda x: '%.3f' % x)


# ### העלת משתנים להרצת הקוד

# In[31]:


cwd = os.getcwd()

create_forecast_basic_folder_path = os.path.dirname(cwd)

sys.path.append(create_forecast_basic_folder_path)


# ## פונקציות

# ### פונקציות גלובליות

# In[32]:


from global_functions import up_load_shp, up_load_df, drop_geo, up_load_gdb


# ## להריץ תלמידים

# In[33]:


get_ipython().run_line_magic('run', '"students_current_year.ipynb"')


# ## להעלות שכבות

# In[34]:


path=r'{}\background_files\EMP_KIBOLET.gdb'.format(create_forecast_basic_folder_path)

EMP_kibolet=up_load_gdb(path,'EMP_kibolet')


# In[35]:


EMP_kibolet=EMP_kibolet.fillna(0)

EMP_kibolet['emp_without_palestin']=EMP_kibolet['kayim_emp']-EMP_kibolet['Palestinians']

emp_without_palestin_not_okev=EMP_kibolet['emp_without_palestin'].sum().item()

emp_Education=taz.query('main_secto!="Palestinian"')['emp_Education'].sum().item()


# ## הוספת סטודנטים לאוכלוסיה ולהתפלגות גילים

# In[36]:


student_dorms=up_load_shp(r'{}\background_files\student_dorms.shp'.format(cwd))


# In[37]:


#העלה של נתוני אנשים התפלגות גילים שנוצר לפני הקוד הזה
path=r'{}\Intermediates'.format(cwd)
taz_with_pop=up_load_df(path,'taz_with_pop_info')


# In[38]:


col_needed=['Taz_num','aprt_20',
 'pop',
 'pop_0',
 'pop_10',
 'pop_15',
 'pop_20',
 'pop_25',
 'pop_30',
 'pop_35',
 'pop_40',
 'pop_45',
 'pop_5',
 'pop_50',
 'pop_55',
 'pop_60',
 'pop_65',
 'pop_70',
 'pop_75up', 'hh_size']


# In[39]:


taz=taz.merge(taz_with_pop[col_needed],on='Taz_num',how='left')


# In[40]:


taz=taz.set_index('Taz_num')


# In[41]:


taz['student_dorms']=gpd.sjoin(taz[['geometry']].reset_index(),student_dorms)[['Taz_num','student_nu']].pivot_table(index='Taz_num',aggfunc='sum')


# In[42]:


taz=taz.fillna(0)

taz['pop_without_dorms_yeshiva']=taz['pop']

taz['pop']=taz['pop']+taz['student_dorms']

taz['pop_20_just_from_aprt']=taz['pop_20']

taz['pop_25_just_from_aprt']=taz['pop_25']

taz['pop_20']=taz['pop_20']+taz['student_dorms']*0.6

taz['pop_25']=taz['pop_25']+taz['student_dorms']*0.4


# In[43]:


col=['pop_0',
 'pop_10',
 'pop_15',
 'pop_20',
 'pop_25',
 'pop_30',
 'pop_35',
 'pop_40',
 'pop_45',
 'pop_5',
 'pop_50',
 'pop_55',
 'pop_60',
 'pop_65',
 'pop_70',
 'pop_75up',]

taz['pop_check']=round(taz[col].sum(axis=1)-taz['pop'])

taz.loc[taz['main_secto']!="Palestinian"].loc[taz['pop_check']!=0]


# ## הוספת תלמידי ישיבה (באזורים חרדיים) אל כמות אוכלוסיה,התפלגות גילים 

# In[44]:


taz['pop_15_just_from_aprt']=taz['pop_15']


# In[45]:


taz.loc[taz['main_secto']=="U_Orthodox",'pop']=taz['pop']+taz['yeshiva_dorms_pop_sum']

taz.loc[taz['main_secto']=="U_Orthodox",'pop_15']=taz['pop_15']+taz['yeshiva_dorms_pop_15']

taz.loc[taz['main_secto']=="U_Orthodox",'pop_20']=taz['pop_20']+taz['yeshiva_dorms_pop_20']

taz.loc[taz['main_secto']=="U_Orthodox",'pop_25']=taz['pop_25']+taz['yeshiva_dorms_pop_25']


# In[46]:


col=['pop_0',
 'pop_10',
 'pop_15',
 'pop_20',
 'pop_25',
 'pop_30',
 'pop_35',
 'pop_40',
 'pop_45',
 'pop_5',
 'pop_50',
 'pop_55',
 'pop_60',
 'pop_65',
 'pop_70',
 'pop_75up',]

taz['pop_check']=round(taz[col].sum(axis=1)-taz['pop'])

taz.loc[taz['main_secto']!="Palestinian"].loc[taz['pop_check']!=0]


# ## כימות מועסקים במרחב צתאל

# In[47]:


pre_woman=0.5

pre_man=1-pre_woman


# In[48]:


work_age=[ 'pop_25',
 'pop_30',
 'pop_35',
 'pop_40',
 'pop_45',
 'pop_50',
 'pop_55',
 'pop_60']

under_work_age=[ 'pop_15', 'pop_20']

over_work_age=[ 'pop_65', 'pop_70', 'pop_75up']


# In[49]:


taz['work_age']=taz[work_age].sum(axis=1)

taz['under_work_age']=taz[under_work_age].sum(axis=1)

taz['over_work_age']=taz[over_work_age].sum(axis=1)


# In[50]:


sector='U_Orthodox'

taz.loc[taz['main_secto']==sector,'pop_emp']=taz['work_age']*pre_woman*0.75+taz['work_age']*pre_man*0.55
taz.loc[taz['main_secto']==sector,'pop_emp']=taz['pop_emp']+taz['under_work_age']*pre_woman*0.07+taz['under_work_age']*pre_man*0.09
taz.loc[taz['main_secto']==sector,'pop_emp']=taz['pop_emp']+taz['over_work_age']*pre_woman*0.05+taz['over_work_age']*pre_man*0.09

sector='Jewish'

taz.loc[taz['main_secto']==sector,'pop_emp']=taz['work_age']*pre_woman*0.9+taz['work_age']*pre_man*0.92
taz.loc[taz['main_secto']==sector,'pop_emp']=taz['pop_emp']+taz['under_work_age']*pre_woman*0.20+taz['under_work_age']*pre_man*0.15
taz.loc[taz['main_secto']==sector,'pop_emp']=taz['pop_emp']+taz['over_work_age']*pre_woman*0.2+taz['over_work_age']*pre_man*0.15

sector='Arab'

taz.loc[taz['main_secto']==sector,'pop_emp']=taz['work_age']*pre_woman*0.25+taz['work_age']*pre_man*0.7
taz.loc[taz['main_secto']==sector,'pop_emp']=taz['pop_emp']+taz['under_work_age']*pre_woman*0.2+taz['under_work_age']*pre_man*0.15
taz.loc[taz['main_secto']==sector,'pop_emp']=taz['pop_emp']+taz['over_work_age']*pre_woman*0.05+taz['over_work_age']*pre_man*0.09

sector='arabs_behined_seperation_wall'

taz.loc[taz['main_secto']==sector,'pop_emp']=taz['work_age']*pre_woman*0.25+taz['work_age']*pre_man*0.7
taz.loc[taz['main_secto']==sector,'pop_emp']=taz['pop_emp']+taz['under_work_age']*pre_woman*0.2+taz['under_work_age']*pre_man*0.15
taz.loc[taz['main_secto']==sector,'pop_emp']=taz['pop_emp']+taz['over_work_age']*pre_woman*0.05+taz['over_work_age']*pre_man*0.09


# ## חישוב אבטלה

# In[51]:


taz['pop_emp_employed']=0

taz.loc[taz['main_secto']=="U_Orthodox",'pop_emp_employed']=taz['pop_emp']*0.97

taz.loc[taz['main_secto']=="Jewish",'pop_emp_employed']=taz['pop_emp']*0.98

taz.loc[taz['jew']==0,'pop_emp_employed']=taz['pop_emp']*0.95


# ## חישוב יוממות

# In[52]:


taz['pop_emp_employed_out_of_jtmt_area']=taz['pop_emp_employed']*taz['commuting']

emp_left_jtmt_area=taz['pop_emp_employed_out_of_jtmt_area'].sum().item()

round(emp_left_jtmt_area,-3)


# In[53]:


emp_from_jtmt_area=taz['pop_emp_employed'].sum().item()-emp_left_jtmt_area

emp_in_jtmt_area=emp_from_jtmt_area*1.07 #יוממות פנימה מחוץ למרחב

round(emp_in_jtmt_area,-3)


# In[54]:


emp_in_jtmt_area_without_mobile=emp_in_jtmt_area*0.95 #הפחחת עובדים ניידים

round(emp_in_jtmt_area_without_mobile,-3)


# In[55]:


emp_okev=emp_in_jtmt_area_without_mobile-emp_Education-emp_without_palestin_not_okev


# ## פיזור עוקב

# In[56]:


list(EMP_kibolet)


# In[57]:


EMP_kibolet['geometry_buff']=EMP_kibolet.buffer(250)

EMP_buffer=EMP_kibolet.set_geometry('geometry_buff').query('kayim_emp>0 & effects_okev==1')

EMP_buffer=EMP_buffer.dissolve()[['geometry_buff']]

taz['taz_area']=taz.area


# In[58]:


emp_buffer_taz=gpd.overlay(EMP_buffer,taz.reset_index())

emp_buffer_taz['emp_samll_area']=emp_buffer_taz.area

emp_buffer_taz['emp_pre_from_taz']=emp_buffer_taz['emp_samll_area']/emp_buffer_taz['taz_area']


# In[59]:


taz_num_no_need_okev=emp_buffer_taz.loc[emp_buffer_taz['emp_pre_from_taz']>0.4].Taz_num.to_list()


# In[60]:


taz['okev']=0
taz.loc[(~taz.index.isin(taz_num_no_need_okev))&(taz['pop']>0)&(taz['main_secto']!="Palestinia"),'okev']=1

taz.loc[taz['main_secto']=="arabs_behined_seperation_wall",'okev']=1


# ## מקדם עוקב

# In[592]:


taz['emp_okev']=0

taz.loc[(taz['jew']==0)&(taz['okev']==1),'emp_okev']=taz['aprt_20']*0.3

taz.loc[(taz['main_secto']=="U_Orthodox")&(taz['okev']==1),'emp_okev']=taz['aprt_20']*0.3

taz.loc[(taz['main_secto']=="Jewish")&(taz['okev']==1),'emp_okev']=taz['aprt_20']*0.2

taz.emp_okev.sum().item()-emp_okev


# ## פיצול שכבת לא עוקב לאזורי תנועה

# In[548]:


EMP_kibolet['emp_area']=EMP_kibolet.area

EMP_kibolet['ID']=EMP_kibolet.index

EMP_kibolet_by_taz=gpd.overlay(taz.reset_index()[['Taz_num','taz_area','geometry']],EMP_kibolet)

EMP_kibolet_by_taz['small_area']=EMP_kibolet_by_taz.area


# In[549]:


EMP_kibolet_by_taz['pre_small_area_emp']=EMP_kibolet_by_taz['small_area']/EMP_kibolet_by_taz['emp_area']

EMP_kibolet_by_taz['pre_small_area_taz']=EMP_kibolet_by_taz['small_area']/EMP_kibolet_by_taz['taz_area']

EMP_kibolet_by_taz=EMP_kibolet_by_taz.query('(pre_small_area_taz >0.7) | (pre_small_area_emp >0.1)').drop(columns='geometry_buff')

EMP_kibolet_by_taz=EMP_kibolet_by_taz.set_index('ID')


# In[550]:


EMP_kibolet_by_taz['id_area_for_pre']=EMP_kibolet_by_taz.reset_index().groupby(by='ID')['small_area'].sum()

EMP_kibolet_by_taz['prec_from_id']=EMP_kibolet_by_taz['small_area']/EMP_kibolet_by_taz['id_area_for_pre']



# מתחמי תעסוקה גדולים מאוד פיזור של המועסקים מבוסס על הפיזור של גירסא 3

# In[551]:


path=r'{}\background_files'.format(cwd)
pre_for_dis_emp_by_taz_v3=up_load_df(path,'pre_for_dis_emp_by_taz_v3')


# In[553]:


EMP_kibolet_by_taz=EMP_kibolet_by_taz.merge(pre_for_dis_emp_by_taz_v3[['Taz_num','pre_dis_emp']],on='Taz_num',how='left').fillna(0)


# In[554]:


EMP_kibolet_by_taz.loc[EMP_kibolet_by_taz['name'].isin(list(pre_for_dis_emp_by_taz_v3['name'])),'prec_from_id']=0 #לאפס את המתחמים שאני רוצה לפזר לפי גירסא 3


# In[555]:


EMP_kibolet_by_taz['emp_without_palestin_in_taz']=EMP_kibolet_by_taz['emp_without_palestin']*EMP_kibolet_by_taz['prec_from_id']


# In[556]:


EMP_kibolet_by_taz.loc[EMP_kibolet_by_taz['name'].isin(list(pre_for_dis_emp_by_taz_v3['name'])),'emp_without_palestin_in_taz']=EMP_kibolet_by_taz['emp_without_palestin']*EMP_kibolet_by_taz['pre_dis_emp']


# In[ ]:


taz['emp_not_okev']=drop_geo(EMP_kibolet_by_taz).pivot_table(index='Taz_num',aggfunc='sum')[['emp_without_palestin_in_taz']]



# In[ ]:


taz=taz.fillna(0)

taz['total_emp']=taz['emp_not_okev']+taz['emp_okev']+taz['emp_Education']

taz.query('main_secto!="Palestinian"')['total_emp'].sum()-emp_in_jtmt_area_without_mobile


# ## התפלגות ענפי תעסוקה

# In[ ]:


col=['Indus',
'Com_hotel',
'Business',
'Public',
'agri']


# In[ ]:


for i in col:
    taz['{}'.format(i)]=taz['{}'.format(i)]*(taz['emp_not_okev']+taz['emp_okev'])


# In[ ]:


taz['check_emp_sum']=taz[col].sum(axis=1)-(taz['emp_not_okev']+taz['emp_okev'])

taz.query('check_emp_sum>10 |check_emp_sum<-10')


# ## הוספת סטודנטים אל כמות משקי בית

# In[ ]:


taz=taz.fillna(0)

taz['hh']=taz['aprt_20']+taz['student_dorms']/1.5


# ## הוספת תלמידי ישיבה (באזורים לא חרדיים) אל כמות אוכלוסיה,התפלגות גילים ומשקי בית (לכלל תלמידי הישיבה)

# In[ ]:


taz['hh']=taz['hh']+taz['yeshiva_dorms_pop_sum']


# In[ ]:


taz.loc[taz['main_secto']!="U_Orthodox",'pop']=taz['pop']+taz['yeshiva_dorms_pop_sum']

taz.loc[taz['main_secto']!="U_Orthodox",'pop_15']=taz['pop_15']+taz['yeshiva_dorms_pop_15']

taz.loc[taz['main_secto']!="U_Orthodox",'pop_20']=taz['pop_20']+taz['yeshiva_dorms_pop_20']

taz.loc[taz['main_secto']!="U_Orthodox",'pop_25']=taz['pop_25']+taz['yeshiva_dorms_pop_25']


# ## הוספת אוכלוסיה פלסטינאית

# In[ ]:


path=r'{}\arab_and_palestinian\Intermediates'.format(create_forecast_basic_folder_path)
taz_demo_pls_2020=up_load_df(path,'taz_demo_pls_2020_and_pre_growth_till_2050')[['Taz_num','pop_2020']].set_index('Taz_num')


# In[ ]:


taz.loc[taz['main_secto']=='Palestinian','pop']=taz['pop']+taz_demo_pls_2020['pop_2020']


# In[ ]:


save_taz_path=r'{}\Intermediates'.format(cwd)
taz.to_excel(r'{}\taz_before_add_geo.xlsx'.format(save_taz_path))

