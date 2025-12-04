#!/usr/bin/env python
# coding: utf-8

# ## הגדרות ומקדים

# ### ספריות

# In[97]:


import os
import sys
import pandas as pd
import geopandas as gpd


# In[98]:


pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', lambda x: '%.3f' % x)


# ### העלת משתנים להרצת הקוד

# In[99]:


cwd = os.getcwd()

create_forecast_basic_folder_path = os.path.dirname(cwd)

sys.path.append(create_forecast_basic_folder_path)


# ## פונקציות

# ### פונקציות גלובליות

# In[100]:


from global_functions import up_load_shp, up_load_df, drop_geo, up_load_gdb


# ## להריץ תלמידים

# In[101]:


get_ipython().run_line_magic('run', '"students_current_year.ipynb"')


# ## להעלות שכבות

# In[102]:


path=r'{}\background_files\EMP_KIBOLET.gdb'.format(create_forecast_basic_folder_path)

EMP_kibolet=up_load_gdb(path,'EMP_kibolet')


# In[103]:


EMP_kibolet=EMP_kibolet.fillna(0)

EMP_kibolet['emp_without_palestin']=EMP_kibolet['kayim_emp']-EMP_kibolet['Palestinians']

emp_without_palestin_not_okev=EMP_kibolet['emp_without_palestin'].sum().item()

emp_Education=taz.query('main_secto!="Palestinian"')['emp_Education'].sum().item()


# ## הוספת סטודנטים לאוכלוסיה ולהתפלגות גילים

# In[104]:


student_dorms=up_load_shp(r'{}\background_files\student_dorms.shp'.format(cwd))


# In[105]:


#העלה של נתוני אנשים התפלגות גילים שנוצר לפני הקוד הזה
path=r'{}\Intermediates'.format(cwd)
taz_with_pop=up_load_df(path,'taz_with_pop_info')


# In[106]:


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


# In[107]:


taz=taz.merge(taz_with_pop[col_needed],on='Taz_num',how='left')


# In[108]:


taz=taz.set_index('Taz_num')


# In[109]:


taz['student_dorms']=gpd.sjoin(taz[['geometry']].reset_index(),student_dorms)[['Taz_num','student_nu']].pivot_table(index='Taz_num',aggfunc='sum')


# In[110]:


taz=taz.fillna(0)

taz['pop_without_dorms_yeshiva']=taz['pop']

taz['pop']=taz['pop']+taz['student_dorms']

taz['pop_20_just_from_aprt']=taz['pop_20']

taz['pop_25_just_from_aprt']=taz['pop_25']

taz['pop_20']=taz['pop_20']+taz['student_dorms']*0.6

taz['pop_25']=taz['pop_25']+taz['student_dorms']*0.4


# In[111]:


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

# In[112]:


taz['pop_15_just_from_aprt']=taz['pop_15']


# In[113]:


taz.loc[taz['main_secto']=="U_Orthodox",'pop']=taz['pop']+taz['yeshiva_dorms_pop_sum']

taz.loc[taz['main_secto']=="U_Orthodox",'pop_15']=taz['pop_15']+taz['yeshiva_dorms_pop_15']

taz.loc[taz['main_secto']=="U_Orthodox",'pop_20']=taz['pop_20']+taz['yeshiva_dorms_pop_20']

taz.loc[taz['main_secto']=="U_Orthodox",'pop_25']=taz['pop_25']+taz['yeshiva_dorms_pop_25']


# In[114]:


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

# In[115]:


pre_woman=0.5

pre_man=1-pre_woman


# In[116]:


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


# In[117]:


taz['work_age']=taz[work_age].sum(axis=1)

taz['under_work_age']=taz[under_work_age].sum(axis=1)

taz['over_work_age']=taz[over_work_age].sum(axis=1)


# In[118]:


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

# In[119]:


taz['pop_emp_employed']=0

taz.loc[taz['main_secto']=="U_Orthodox",'pop_emp_employed']=taz['pop_emp']*0.97

taz.loc[taz['main_secto']=="Jewish",'pop_emp_employed']=taz['pop_emp']*0.98

taz.loc[taz['jew']==0,'pop_emp_employed']=taz['pop_emp']*0.95


# ## חישוב יוממות

# In[120]:


taz['pop_emp_employed_out_of_jtmt_area']=taz['pop_emp_employed']*taz['commuting']

emp_left_jtmt_area=taz['pop_emp_employed_out_of_jtmt_area'].sum().item()

round(emp_left_jtmt_area,-3)


# In[121]:


emp_from_jtmt_area=taz['pop_emp_employed'].sum().item()-emp_left_jtmt_area

emp_in_jtmt_area=emp_from_jtmt_area*1.07 #יוממות פנימה מחוץ למרחב

round(emp_in_jtmt_area,-3)


# In[122]:


emp_in_jtmt_area_without_mobile=emp_in_jtmt_area*0.95 #הפחחת עובדים ניידים

round(emp_in_jtmt_area_without_mobile,-3)


# In[123]:


emp_okev=emp_in_jtmt_area_without_mobile-emp_Education-emp_without_palestin_not_okev


# ## פיזור עוקב

# In[124]:


EMP_kibolet['geometry_buff']=EMP_kibolet.buffer(250)

EMP_buffer=EMP_kibolet.set_geometry('geometry_buff').query('kayim_emp>0')

EMP_buffer=EMP_buffer.dissolve()[['geometry_buff']]

taz['taz_area']=taz.area


# In[125]:


emp_buffer_taz=gpd.overlay(EMP_buffer,taz.reset_index())

emp_buffer_taz['emp_samll_area']=emp_buffer_taz.area

emp_buffer_taz['emp_pre_from_taz']=emp_buffer_taz['emp_samll_area']/emp_buffer_taz['taz_area']


# In[126]:


taz_num_no_need_okev=emp_buffer_taz.loc[emp_buffer_taz['emp_pre_from_taz']>0.4].Taz_num.to_list()


# In[127]:


taz['okev']=0
taz.loc[(~taz.index.isin(taz_num_no_need_okev))&(taz['pop']>0)&(taz['main_secto']!="Palestinia"),'okev']=1

taz.loc[taz['main_secto']=="arabs_behined_seperation_wall",'okev']=1


# In[128]:


city_muni=['מודיעין עילית','בית שמש','ירושלים','מודיעין - מכבים - רעות']


# ## מקדם עוקב

# In[129]:


okev_level=0.15

arab_city=taz.query('jew==0 & okev==1')['aprt_20'].sum().item()

arab_sub=0

ou_sub=taz.query('main_secto=="U_Orthodox" & ~Muni_Heb.isin(@city_muni) & okev==1')['aprt_20'].sum().item()


# In[130]:


ou_city=taz.query('main_secto=="U_Orthodox" & Muni_Heb.isin(@city_muni) & okev==1')['aprt_20'].sum().item()

general_city=taz.query('main_secto=="Jewish" & Muni_Heb.isin(@city_muni) & okev==1')['aprt_20'].sum().item()

general_sub=taz.query('main_secto=="Jewish" & ~Muni_Heb.isin(@city_muni) & okev==1')['aprt_20'].sum().item()

base_okev_factor=(emp_okev-(okev_level*general_city-okev_level*(ou_sub+arab_city)-2*okev_level*arab_sub))/(general_sub+general_city+ou_city+ou_sub+arab_city+arab_sub)

base_okev_factor=round(base_okev_factor,3)


# In[131]:


data = [['Jewish', base_okev_factor,base_okev_factor+okev_level],['arab', base_okev_factor-okev_level,base_okev_factor], ['U_Orthodox',base_okev_factor-2*okev_level,base_okev_factor-okev_level]]

# Create the pandas DataFrame
df = pd.DataFrame(data, columns=['sector', 'sub','city'])
okev_factor=df.set_index('sector')
okev_factor.to_excel(r'{}\Intermediates\okev_factor.xlsx'.format(cwd))


# In[132]:


taz['emp_okev']=0

taz.loc[(taz['jew']==0)&(taz['okev']==1),'emp_okev']=taz['aprt_20']*okev_factor.loc['arab','city']

taz.loc[(taz['main_secto']=="U_Orthodox")&(~taz['Muni_Heb'].isin(city_muni))&(taz['okev']==1),'emp_okev']=taz['aprt_20']*okev_factor.loc['U_Orthodox','sub']

taz.loc[(taz['main_secto']=="U_Orthodox")&(taz['Muni_Heb'].isin(city_muni))&(taz['okev']==1),'emp_okev']=taz['aprt_20']*okev_factor.loc['U_Orthodox','city']

taz.loc[(taz['main_secto']=="Jewish")&(taz['Muni_Heb'].isin(city_muni))&(taz['okev']==1),'emp_okev']=taz['aprt_20']*okev_factor.loc['Jewish','city']

taz.loc[(taz['main_secto']=="Jewish")&(~taz['Muni_Heb'].isin(city_muni))&(taz['okev']==1),'emp_okev']=taz['aprt_20']*okev_factor.loc['Jewish','sub']

taz.emp_okev.sum().item()-emp_okev


# ## פיצול שכבת לא עוקב לאזורי תנועה

# In[133]:


EMP_kibolet['emp_area']=EMP_kibolet.area

EMP_kibolet['ID']=EMP_kibolet.index

EMP_kibolet_by_taz=gpd.overlay(taz.reset_index()[['Taz_num','taz_area','geometry']],EMP_kibolet)

EMP_kibolet_by_taz['small_area']=EMP_kibolet_by_taz.area


# In[134]:


EMP_kibolet_by_taz['pre_small_area_emp']=EMP_kibolet_by_taz['small_area']/EMP_kibolet_by_taz['emp_area']

EMP_kibolet_by_taz['pre_small_area_taz']=EMP_kibolet_by_taz['small_area']/EMP_kibolet_by_taz['taz_area']

EMP_kibolet_by_taz=EMP_kibolet_by_taz.query('(pre_small_area_taz >0.7) | (pre_small_area_emp >0.1)').drop(columns='geometry_buff')

EMP_kibolet_by_taz=EMP_kibolet_by_taz.set_index('ID')


# In[135]:


EMP_kibolet_by_taz['id_area_for_pre']=EMP_kibolet_by_taz.reset_index().groupby(by='ID')['small_area'].sum()

EMP_kibolet_by_taz['prec_from_id']=EMP_kibolet_by_taz['small_area']/EMP_kibolet_by_taz['id_area_for_pre']



# מתחמי תעסוקה גדולים מאוד פיזור של המועסקים מבוסס על הפיזור של גירסא 3

# In[136]:


path=r'{}\background_files'.format(cwd)
pre_for_dis_emp_by_taz_v3=up_load_df(path,'pre_for_dis_emp_by_taz_v3')


# In[137]:


EMP_kibolet_by_taz=EMP_kibolet_by_taz.merge(pre_for_dis_emp_by_taz_v3[['Taz_num','pre_dis_emp']],on='Taz_num',how='left')


# In[138]:


EMP_kibolet_by_taz['emp_without_palestin_in_taz']=EMP_kibolet_by_taz['emp_without_palestin']*EMP_kibolet_by_taz['prec_from_id']


# In[139]:


EMP_kibolet_by_taz.loc[EMP_kibolet_by_taz['name'].isin(list(pre_for_dis_emp_by_taz_v3['name'])),'prec_from_id']=0 #לאפס את המתחמים שאני רוצה לפזר לפי גירסא 3


# In[140]:


EMP_kibolet_by_taz['emp_without_palestin_in_taz']=EMP_kibolet_by_taz['emp_without_palestin']*EMP_kibolet_by_taz['pre_dis_emp']


# In[141]:


EMP_kibolet_by_taz.loc[~(EMP_kibolet_by_taz['prec_from_id'].isna()),'emp_without_palestin_in_taz']=EMP_kibolet_by_taz['emp_without_palestin']*EMP_kibolet_by_taz['pre_dis_emp']


# In[142]:


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

