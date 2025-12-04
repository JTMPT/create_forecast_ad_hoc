#!/usr/bin/env python
# coding: utf-8

# ### קוד מבוא
# 

# #### ספריות
# 

# In[2]:


import os
import sys
import pathlib
import pandas as pd


# In[3]:


pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.options.display.float_format = '{:.4f}'.format
pd.set_option('display.float_format',  '{:,.2f}'.format)


# #### העלאת משתנים להרצת הקוד
# 

# In[4]:


cwd = os.getcwd()

create_forecast_basic_folder_path = os.path.dirname(cwd)

sys.path.append(create_forecast_basic_folder_path)


# ### פונקציות
# 

# ### פונקציות גלובליות
# 

# In[5]:


from global_functions import get_newest_date_file, make_point, up_load_shp, up_load_df, find_files_with_pattern


# ### ביצוע
# 

# #### העלאת שכבות
# 

# In[7]:


taz=up_load_shp(r'{}'.format(new_layer_path))


# In[8]:


taz=taz.query('main_secto=="Arab" | main_secto=="arabs_behined_seperation_wall" ').set_index('Taz_num')

taz_point=make_point(taz)


# #### יצירת אוכלוסיה לפי קיבולת
# 

# תוספת קיבולת אפשרית
# 

# In[9]:


path=r'{}\background_files\kibolet_with_behind_wall_230709.shp'.format(cwd)

kibolet_with_behind_wall=up_load_shp(path).set_index('Taz_num')


# יח"ד דיור קיימות
# 

# matching_files=find_files_with_pattern(r'{}'.format(forecast_version_folder_location), '2020_jtmt_forcast_full')
# 
# file = pathlib.Path(matching_files[0])
# file_name = file.name[:-5]
# 

# In[10]:


taz_kayim=up_load_df(r'{}\current\Intermediates'.format(create_forecast_basic_folder_path), 'taz_with_pop_info').set_index('Taz_num')


# ג"מ
# 

# In[10]:


path=r'{}\background_files\hh_size_2050.shp'.format(cwd)

hh_size_2050=up_load_shp(path)


# In[11]:


hh_size_2050=taz_point.sjoin(hh_size_2050,how='left')[['2050_hh_si']]

taz['hh_size']=hh_size_2050['2050_hh_si']


# הכנה ללופ : מצב קיים הופך למצב נוכחי
# 

# In[12]:


taz['current_pop']=taz_kayim['pop']

taz['pop_2020']=taz_kayim['pop']

taz['current_hh']=taz_kayim['aprt_20']

taz['hh_2020']=taz_kayim['aprt_20']


# להוציא את האזורים שמחוץ לירושלים
# 

# In[13]:


taz_out_of_jeru=taz.loc[taz.index.isin([7651.0, 7652.0])]


# In[14]:


taz=taz.loc[~taz.index.isin([7651.0, 7652.0])]


# עכשיו חישוב של כמות אוכלוסיה כל חומש
# 

# In[15]:


taz['pop_kibolet']=taz['hh_size']*kibolet_with_behind_wall['kibolet']


# הכנה ללופ : הלאה של אוכלסייה פלסטינאית
# 

# In[16]:


folder_path=r'{}\Intermediates'.format(cwd)
file_name='taz_demo_pls_2020_and_pre_growth_till_2050'

taz_demo_pls=up_load_df(folder_path,file_name)

taz_demo_pls['current_pop']=taz_demo_pls['pop_2020']


# #### לופ לייצר אנשים כל חומש
# 

# In[17]:


col_age=['Taz_num','pop_0',
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
 'pop_75up']


# חישוב מחוץ לירושלים
# 

# In[18]:


taz_out_of_jeru_point=make_point(taz_out_of_jeru)


# In[19]:


year=['2025','2030','2035','2040','2045','2050']

for y in year:
    # לחבר למצב הנוכחי את הגידול והתפלגות שהוא צריך לקבל
    path=r'{}\Intermediates\pre_demo_growth_dislov_{}.shp'.format(cwd, y)

    demo=up_load_shp(path)  

    demand=taz_out_of_jeru_point.sjoin(demo,how='left')

    taz_age=demand.reset_index()[col_age]

    taz_out_of_jeru_point['add_current_pop']=taz_out_of_jeru_point['current_pop']*demand['precent_ad']-taz_out_of_jeru_point['current_pop']

    taz_out_of_jeru_point['current_pop']=taz_out_of_jeru_point['current_pop']+taz_out_of_jeru_point['add_current_pop']

    taz_out_of_jeru_point['current_hh']=taz_out_of_jeru_point['current_hh']+taz_out_of_jeru_point['add_current_pop']/taz_out_of_jeru_point['hh_size']

    taz_out_of_jeru_point['hh_{}'.format(y)]=taz_out_of_jeru_point['current_hh']

    taz_out_of_jeru_point['pop_{}'.format(y)]=taz_out_of_jeru_point['current_pop']

    col=['Taz_num','hh_{}'.format(y),'pop_{}'.format(y)]

    locals()['taz_out_jeru_{}'.format(y)]=taz_out_of_jeru_point.reset_index()[col].merge(taz_age,how='left',on='Taz_num')   


# חישוב לירושלים ואז הוספה של המרכיבים
# 

# In[20]:


#מייצר קטלוג לאזורים ללא התפלגות מדמוגרף
age_dis=up_load_df(r'{}\background_files'.format(create_forecast_basic_folder_path),'age_des_types')

age_col_catalog=['pop_0',
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
 'pop_75up']

age_dis=age_dis.query('sector=="Arab" & age_cycle==2')[age_col_catalog]


# In[21]:


taz['precent_ad']=0


# In[22]:


x=2020


# In[23]:


year=['2025','2030','2035','2040','2045','2050']


# In[24]:


for y in year:
    # לחבר למצב הנוכחי את הגידול והתפלגות שהוא צריך לקבל
    path=r'{}\Intermediates\pre_demo_growth_dislov_{}.shp'.format(cwd, y)

    demo=up_load_shp(path)

    taz_point=make_point(taz.reset_index()[['Taz_num','geometry']])

    demand=taz_point.sjoin(demo,how='left')
    taz_age=demand.reset_index()[col_age]

    demand=demand[['Taz_num','precent_ad']].set_index('Taz_num')

    taz['precent_ad']=demand['precent_ad']
    taz['precent_ad']=taz['precent_ad'].fillna(0)
    taz['precent_ad_{}'.format(y)]=taz['precent_ad']

    taz.loc[taz['precent_ad']>0,'pop_demand']=taz['current_pop']*taz['precent_ad']-taz['current_pop']
    taz.loc[taz['precent_ad']<=0,'pop_demand']=0
    taz['pop_demand_{}'.format(y)]=taz['pop_demand']
    taz['pop_kibolet_{}'.format(y)]=taz['pop_kibolet']

    # יצירת התפלגות,גידול וג"מ הממוצע של כל אחד מהערכים האלו בחומש
    # אזורים עם אוכלוסייה וללא התפלגות,גידול וג"מ יקבלו את הערך הממוצע הנל
    # מצב נוכחי גדל לפי אחוז
    # השוואה בין אוכלוסית ביקוש לקיבולת
    print("------------------------------------------")
    print(y)
    print("total_kibolet: ",taz['pop_kibolet'].sum().item())
    print("total_demand: ",taz['pop_demand'].sum().item())

    taz['pop_delta']=taz['pop_kibolet']-taz['pop_demand']
    taz['pop_delta_{}'.format(y)]=taz['pop_delta']

    # יש מקום לביקוש - לקחת את הביקוש
    taz.loc[taz['pop_delta']>0,'current_pop']=taz['pop_demand']+taz['current_pop']
    taz.loc[taz['pop_delta']>0,'pop_kibolet']=taz['pop_kibolet']-taz['pop_demand']
    taz.loc[taz['pop_delta']>0,'pop_{}_explanation'.format(y)]='pop_demand'


    # אין מקום לביקוש - לקחת את הקיבולת
    taz.loc[(taz['pop_delta']<=0)&(taz['pop_kibolet']>0),'current_pop']=taz['pop_kibolet']+taz['current_pop']
    taz.loc[(taz['pop_delta']<=0)&(taz['pop_kibolet']>0),'pop_kibolet']=0
    taz.loc[(taz['pop_delta']<=0)&(taz['pop_kibolet']>0),'pop_{}_explanation'.format(y)]='full_pop_kibolet'

    # לקבץ את כלל האוכלוסיה ללא בית לסל אחד
    pop_not_fit_in_taz=taz.loc[taz['pop_delta']<=0]['pop_delta'].sum().item()

    pop_not_fit_in_taz=abs(pop_not_fit_in_taz)

    print("pop_not_fit_in_taz: ",pop_not_fit_in_taz)

    # כימות כמה עוד מקום יש בקיבולת של ירושלים
    pop_kibolet_left=taz['pop_kibolet'].sum().item()

    print("pop_kibolet_left: ",pop_kibolet_left)

    if pop_not_fit_in_taz>pop_kibolet_left:
        print("pop_not_fit_in_taz>pop_kibolet_left")

        taz['current_pop']=taz['pop_kibolet']+taz['current_pop']
        taz['pop_kibolet']=0
        taz['pop_{}_explanation'.format(y)]=taz['pop_{}_explanation'.format(y)]+' +add_pop_to_fill_kibolet'

        pop_not_fit_in_jeru=pop_not_fit_in_taz-pop_kibolet_left

        print("pop_not_fit_in_jeru: ",pop_not_fit_in_jeru)

        taz_demo_pls['current_pop_pre']=taz_demo_pls['current_pop']/taz_demo_pls['current_pop'].sum().item()
        taz_demo_pls['add_pop_{}_from_jeru'.format(y)]=taz_demo_pls['current_pop_pre']*pop_not_fit_in_jeru
        taz_demo_pls['current_pop']=taz_demo_pls['current_pop']*taz_demo_pls['precent_add_pop_{}'.format(y)]
        taz_demo_pls['current_pop']=taz_demo_pls['current_pop']+taz_demo_pls['add_pop_{}_from_jeru'.format(y)]
        taz_demo_pls['pop_{}'.format(y)]=taz_demo_pls['current_pop']
    else:
        print("pop_not_fit_in_taz<=pop_kibolet_left")

        taz['add_pop_kibolet_from_pre']=taz['pop_kibolet']*(pop_not_fit_in_taz/pop_kibolet_left)
        taz['add_pop_kibolet_from_pre_{}'.format(y)]=taz['add_pop_kibolet_from_pre']
        taz['current_pop']=taz['add_pop_kibolet_from_pre']+taz['current_pop']
        taz['pop_kibolet']=taz['pop_kibolet']-taz['add_pop_kibolet_from_pre']
        taz.loc[taz['add_pop_kibolet_from_pre']>0,'pop_{}_explanation'.format(y)]=taz['pop_{}_explanation'.format(y)]+' +add_pop_by_pre_of_kibolet_pre'

        taz_demo_pls['current_pop']=taz_demo_pls['current_pop']*taz_demo_pls['precent_add_pop_{}'.format(y)]
        taz_demo_pls['pop_{}'.format(y)]=taz_demo_pls['current_pop']        

    taz['pop_{}'.format(y)]=taz['current_pop']
    taz['add_pop_{}_{}'.format(y,str(x))]=taz['current_pop']-taz['pop_{}'.format(str(x))]
    taz.loc[(taz['add_pop_{}_{}'.format(y,str(x))]>0)&(taz['hh_size']<=0),'current_hh']=taz['current_hh']+taz['add_pop_{}_{}'.format(y,str(x))]/4.5

    taz.loc[(taz['add_pop_{}_{}'.format(y,str(x))]>0)&(taz['hh_size']>0),'current_hh']=taz['current_hh']+taz['add_pop_{}_{}'.format(y,str(x))]/4.5

    taz['hh_{}'.format(y)]=taz['current_hh']

    x=x+5
    col_current=['Taz_num','hh_{}'.format(y),'pop_{}'.format(y)]
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
     'pop_75up']

    df=taz.reset_index()[col_current].merge(taz_age,how='left',on='Taz_num')

    df=pd.concat([df,locals()['taz_out_jeru_{}'.format(y)]],axis=0)

    df1=df.loc[((df[col].sum(axis=1)==0)&(df['pop_{}'.format(y)]>0))]

    df1=df1[col_current]

    df1['join']=1

    age_dis['join']=1

    df1=df1.merge(age_dis,on='join',how='left').drop(columns='join')

    df=df.loc[~((df[col].sum(axis=1)==0)&(df['pop_{}'.format(y)]>0))]

    df=pd.concat([df,df1],axis=0)

    df=df.round(2)

    df[col]=df[col].div(df[col].sum(axis=1), axis=0)

    df[col] = df[col].apply(lambda x: x * df['pop_{}'.format(y)])

    df['pop_{}'.format(y)]=df[col].sum(axis=1)

    df=pd.concat([df,taz_demo_pls[['Taz_num','pop_{}'.format(y)]]],axis=0)  

    col=['Taz_num','hh_{}'.format(y),'pop_{}'.format(y),'pop_0',
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
         'pop_75up']

    df[col].to_excel(r'{}\Intermediates\taz_Arab_Palestinian_{}.xlsx'.format(cwd, y),index=False)

