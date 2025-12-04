#!/usr/bin/env python
# coding: utf-8

# ### קוד מבוא

# In[1]:


import pandas as pd
import geopandas as gpd
import numpy as np
from shapely import wkt
from matplotlib import pyplot as plt 
import os
import sys

import folium
import fiona

from shapely.geometry import Point


# In[2]:


pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)


# In[3]:


pd.options.display.float_format = '{:.4f}'.format
pd.set_option('display.float_format',  '{:,.2f}'.format)


# ### פונקציות

# In[4]:


def double_taz_num(df):
    dup_taz_num=df.groupby(['Taz_num']).size().reset_index(name='count').query('count>1').Taz_num.to_list()
    return df.loc[df['Taz_num'].isin(dup_taz_num)]


# In[5]:


def make_point(df):
    df_point=df.copy()
    df_point['centroid'] = df_point.representative_point()
    df_point=df_point.set_geometry('centroid')
    df_point=df_point.drop(columns=['geometry'],axis=1)
    return df_point


# In[6]:


def up_load_gdb(path,layer_name):
    path='{}'.format(path)
    layer_list=fiona.listlayers(path)
    gpd_layer=gpd.read_file(path, layer=layer_list.index(layer_name))
    return gpd_layer


# In[7]:


def up_load_shp(path):
    path='{}'.format(path)
    gpd_layer=gpd.read_file(path)
    return gpd_layer


# In[8]:


def up_load_df(folder_path,file_name):

    path_df=r'{}\{}.xlsx'.format(folder_path,file_name)
    df=pd.read_excel(path_df)
    df=df.dropna(how='all')

    return df


# ### העלת קבצים

# In[9]:


path = os.getcwd()

software_root_folder = os.path.dirname(path)


# In[10]:


software_folder_location = r'{}\create_potential_aprt'.format(software_root_folder)


# In[18]:


df_inputs_outputs = pd.read_excel(r'{}\inputs_outputs.xlsx'.format(software_folder_location))


# ##### לייצר יח"ד קיים פר אזור תנועה

# In[12]:


forecast_2020=up_load_df(r'{}\background_files'.format(software_folder_location),'2020_jtmt_forcast_full_240226')


# In[13]:


x=r'{}\background_files\TAZ_V4_230518_Published.shp'.format(software_folder_location)


# In[14]:


taz=up_load_shp(x)


# In[15]:


taz=pd.merge(taz,forecast_2020[['Taz_num','aprt_20']].query('aprt_20>0'),on='Taz_num')


# In[16]:


path=r'{}\background_files\BNTL_2022.gdb'.format(software_folder_location)
bld=up_load_gdb(path,'BLDG_Clip')
bld_poi=up_load_gdb(path,'POI_BLDG_Clip')
bld=bld.merge(bld_poi[[ 'FCODE', 'USG_GROUP', 'USG_CODE','USG_SP_NM_LTN','BLDG_ID']],how='left',left_on='UNIQ_ID',right_on='BLDG_ID')
bld=bld.loc[bld['FCODE_y'].isna()]
bld['bld_area']=bld.area
bld_point=make_point(bld).fillna(0)
bld_point.loc[bld_point['HEIGHT']<=0,'HEIGHT']=bld_point['HI_PNT_Z']-bld_point['HT_LAND']
ceiling_height=3
bld_point['bld_m3']=(bld_point['HEIGHT']/ceiling_height).astype(int)*bld_point['bld_area'].astype(int)
bld_point.loc[(bld_point['HEIGHT']-ceiling_height)<=0,'bld_m3']=bld_point['bld_area']
bld_point=gpd.sjoin(bld_point,taz)
col=['bld_m3','centroid','Taz_num','aprt_20']
bld_point=bld_point[col]
bld_point['bld_m3']=bld_point['bld_m3'].astype(int)
sum_bld_m3=pd.pivot_table(bld_point.drop(columns='centroid'),index='Taz_num',aggfunc=sum)[['bld_m3']].reset_index().rename(columns={'bld_m3':'bld_m3_taz'})
bld_point=bld_point.merge(sum_bld_m3,on='Taz_num')
bld_point['aprt_in_bld_from_pre_of_taz']=bld_point['bld_m3']/bld_point['bld_m3_taz']*bld_point['aprt_20']
bld_point['aprt_in_bld_from_pre_of_taz']=bld_point['aprt_in_bld_from_pre_of_taz'].astype(int)


# עד כאן יש לי שכבה של כמות יח"ד בכל בניין

# עכשיו צריך להעלות את המקורות מידע שלנו

# תכניות אינדקס

# In[19]:


client_data_folder_location=df_inputs_outputs['location'][0]


# In[21]:


path_to_index_df=r'{}\For_approval\Reference_tabels'.format(client_data_folder_location)


# In[22]:


name_of_index_file=r'index_format_for_creating_forecast_jtmt_input_{}_{}'.format(df_inputs_outputs['location'][1],df_inputs_outputs['location'][2])


# השורה הבא מועדת לפורענות

# name_of_index_file=r'‏‏index_format_for_creating_forecast_jtmt_input_with_project_240923'

# In[23]:


plans_df=up_load_df(path_to_index_df,name_of_index_file)


# In[25]:


plans_shp=up_load_shp(r'{}\For_approval\Reference_tabels\shp\gvul_index.shp'.format(client_data_folder_location))


# להעלות את שכבת הרקל

# In[26]:


rakal=up_load_gdb(r'{}\For_approval\Reference_tabels\shp\tochnit_check.gdb'.format(client_data_folder_location),'lrt_policy')


# להוריד אזורים שכבר יש תכניות באינדקס

# In[27]:


plans_shp['type']='plans'


# In[28]:


col=['type','geometry']
rakal=rakal.overlay(plans_shp[col], how='union').query('type.isna()')


# לחלק לפי אזורי תנועה ורק אז לייצר את הקיבולת

# להעלות את שכבת האזורי תנועה הנדרשים לפרוייקט

# In[29]:


taz_for_proj=up_load_gdb(r'{}\For_approval\Reference_tabels\shp\tochnit_check.gdb'.format(client_data_folder_location),'TAZ_211028_V3_Published_with_client_changes')


# In[30]:


taz_for_proj['taz']=1


# In[31]:


rakal['rakal']=1


# In[32]:


rakal=rakal.overlay(taz_for_proj[['taz','geometry']], how='union').query('rakal==1 & taz==1')


# In[33]:


rakal['area']=rakal.area


# לייצר את תופסת יח"ד של רקל

# In[34]:


aprt_size=130


# In[35]:


rakal['potential_aprt']=rakal['area']*7.2*0.5/aprt_size


# In[36]:


#כמה יח"ד יש בכל אחד מהפוליגונים?
rakal['id']=rakal.index


# In[37]:


bld_point_for_plans_need_add_aprt=gpd.sjoin(bld_point,rakal)


# In[38]:


bld_point_for_plans_need_add_aprt=bld_point_for_plans_need_add_aprt.drop(columns='centroid').pivot_table(index='id',aggfunc=sum)[['aprt_in_bld_from_pre_of_taz']]


# In[39]:


rakal=rakal.set_index('id')


# In[40]:


rakal['aprt_20']=bld_point_for_plans_need_add_aprt['aprt_in_bld_from_pre_of_taz']


# In[41]:


rakal=rakal.fillna(0)


# In[42]:


rakal['add_potential_aprt']=rakal['potential_aprt']-rakal['aprt_20']


# In[43]:


rakal=rakal.loc[rakal['add_potential_aprt']>50]


# לייצר שימושים תעסוקה ברקל

# In[44]:


rakal['Business_m2']=rakal['area']*7.2*0.1


# In[45]:


rakal['Commerce_m2']=rakal['area']*7.2*0.1


# להעלות את שכבת בינוי חדש
# 

# In[47]:


new_bld=up_load_gdb(r'{}\For_approval\Reference_tabels\shp\tochnit_check.gdb'.format(client_data_folder_location),'new_bld')


# עכשיו צריך לחורר משכבת בינוי חדש את הפוליגונים של רקל ושל תכניות

# In[48]:


rakal['type']='lrt'


# In[49]:


col=['type','geometry']


# In[50]:


new_bld=new_bld.overlay(pd.concat([rakal[col],plans_shp[col]]), how='union').query('type.isna()')


# In[51]:


new_bld['new_bld']=1


# In[52]:


new_bld=new_bld.overlay(taz_for_proj[['taz','geometry']], how='union').query('new_bld==1')


# In[53]:


new_bld['add_potential_aprt']=new_bld['Shape_Area']*new_bld['prec_for_aprt']*new_bld['neto_dens']/1000


# In[54]:


new_bld=new_bld.loc[new_bld['add_potential_aprt']>50]


# להעלות את שכבת מכפיל

# In[55]:


machpil=up_load_gdb(r'{}\For_approval\Reference_tabels\shp\tochnit_check.gdb'.format(client_data_folder_location),'urban_density')


# עכשיו צריך לחורר משכבת מכפיל את הפוליגונים של רקל ושל תכניות

# In[56]:


col=['type','geometry']


# In[57]:


machpil=machpil.overlay(pd.concat([rakal[col],plans_shp[col],new_bld[col]]), how='union').query('type.isna()')


# In[58]:


machpil['machpil']=1


# In[59]:


machpil=machpil.overlay(taz_for_proj[['taz','geometry']], how='union').query('machpil==1')


# לייצר כמות יח"ד בשביל הכפלה

# In[60]:


#כמה יח"ד יש בכל אחד מהפוליגונים?
machpil['id']=machpil.index


# In[61]:


bld_point_for_plans_need_add_aprt=gpd.sjoin(bld_point,machpil)


# In[62]:


bld_point_for_plans_need_add_aprt=bld_point_for_plans_need_add_aprt.drop(columns='centroid').pivot_table(index='id',aggfunc=sum)[['aprt_in_bld_from_pre_of_taz']]


# In[63]:


machpil=machpil.set_index('id')


# In[64]:


machpil['aprt_20']=bld_point_for_plans_need_add_aprt['aprt_in_bld_from_pre_of_taz']


# In[65]:


machpil=machpil.fillna(0)


# In[66]:


machpil['add_potential_aprt']=machpil['aprt_20']*machpil['coefficient']


# In[67]:


machpil=machpil.loc[machpil['add_potential_aprt']>25]


# עכשיו שיש לי תופסת יח"ד ברקל בינוי חדש ומכפיל צריך לצרף את זה לאינדקס השכבה ולאקסל

# In[68]:


plans_shp.drop(columns='type',inplace=True)


# In[69]:


max_id =int(plans_shp['id'].max())
num_new_rows = int(len(machpil))

machpil.reset_index(inplace=True)


# In[70]:


machpil['id'] = range(max_id + 1, max_id + 1 + num_new_rows)


# In[71]:


machpil = machpil.rename(columns={'add_potential_aprt': 'add_aprt'})


# In[72]:


machpil['plan_name']='מכפיל'


# In[73]:


machpil['status']='פוטנציאל'


# In[74]:


machpil['emp_fill_factor']=1


# In[75]:


machpil['Risk_factor']=1


# In[76]:


joined_plans_shp=pd.concat([plans_shp,machpil[['id','geometry']]])
joined_plans_df=pd.concat([plans_df,machpil[['id','add_aprt','plan_name','status','Risk_factor','emp_fill_factor']]])


# הוספה של רקל לשכבה וטבלאות

# In[77]:


max_id =int(joined_plans_shp['id'].max())
num_new_rows = int(len(rakal))


# In[78]:


rakal.reset_index(inplace=True)


# In[79]:


rakal['id'] = range(max_id + 1, max_id + 1 + num_new_rows)


# In[80]:


rakal = rakal.rename(columns={'add_potential_aprt': 'add_aprt'})


# In[81]:


rakal['plan_name']='רקל'


# In[82]:


rakal['status']='פוטנציאל'


# In[83]:


rakal['emp_fill_factor']=1


# In[84]:


rakal['Risk_factor']=1


# In[85]:


joined_plans_shp=pd.concat([joined_plans_shp,rakal[['id','geometry']]])
joined_plans_df=pd.concat([joined_plans_df,rakal[['id','plan_name','status','add_aprt','Business_m2','Commerce_m2','Risk_factor','emp_fill_factor']]])


# הוספה של בינוי חדש לשכבה וטבלאות

# In[86]:


max_id =int(joined_plans_shp['id'].max())
num_new_rows = int(len(new_bld))


# In[87]:


new_bld.reset_index(inplace=True)


# In[88]:


new_bld['id'] = range(max_id + 1, max_id + 1 + num_new_rows)


# In[89]:


new_bld = new_bld.rename(columns={'add_potential_aprt': 'add_aprt'})


# In[90]:


new_bld['plan_name']='בינוי חדש'


# In[91]:


new_bld['status']='פוטנציאל'


# In[92]:


new_bld['emp_fill_factor']=1


# In[93]:


new_bld['Risk_factor']=1


# In[94]:


joined_plans_shp=pd.concat([joined_plans_shp,new_bld[['id','geometry']]])
joined_plans_df=pd.concat([joined_plans_df,new_bld[['id','plan_name','status','add_aprt','Risk_factor','emp_fill_factor']]])


# הוספה של מימושים

# In[95]:


mimoshim_jtmt=up_load_df(r'W:\Data\Forecast\Tools\create_forecast_ad_hoc\create_potential_aprt','mimoshim_jtmt')


# In[96]:


def update_f_value(df, status_value, mimoshim_df, column_name,x):
    df.loc[(df['status'] == status_value) & (df['add_aprt'] <= 250), 'F{}'.format(column_name)] = mimoshim_df.iloc[x][column_name]
    df.loc[(df['status'] == status_value) & (df['add_aprt'] > 250) & (df['add_aprt'] <= 500), 'F{}'.format(column_name)] = mimoshim_df.iloc[x+1][column_name]
    df.loc[(df['status'] == status_value) & (df['add_aprt'] > 500), 'F{}'.format(column_name)] = mimoshim_df.iloc[x+2][column_name]
    df.loc[(df['status'] == status_value) & (df['add_aprt'] ==0), 'F{}'.format(column_name)] = mimoshim_df.iloc[x+1][column_name]

    return df


# In[97]:


stat_lst=['מאושר','הליכים','פרה_רולינג','פוטנציאל','היתר']


# In[98]:


col_lst=['2030','2035','2040']


# In[99]:


x=0
for i in stat_lst:

    for c in col_lst:
        joined_plans_df=update_f_value(joined_plans_df, i, mimoshim_jtmt, c,x)

    print(x,'-',i)

    x=x+3


# In[100]:


col=['F2025',
 'F2030',
 'F2035',
 'F2040']


# In[101]:


joined_plans_df['add_aprt_till_2040']=joined_plans_df['add_aprt']*joined_plans_df[col].sum(axis=1)


# In[102]:


joined_plans_shp=joined_plans_shp.merge(joined_plans_df[['id','status']],on='id',how='left')


# In[103]:


joined_plans_shp = joined_plans_shp.set_crs("EPSG:2039", allow_override=True)


# In[104]:


joined_plans_shp.to_file(r'{}\For_approval\Reference_tabels\shp\gvul_index_with_ponten.shp'.format(client_data_folder_location),encoding='utf-8', engine = 'fiona')


# In[105]:


joined_plans_df.to_excel(r'{}\For_approval\Reference_tabels\index_format_for_creating_forecast_jtmt_input_{}_{}_with_poten_jtmt.xlsx'.format(client_data_folder_location,df_inputs_outputs['location'][1],df_inputs_outputs['location'][2]),index=False)

