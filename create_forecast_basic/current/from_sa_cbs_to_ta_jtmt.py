#!/usr/bin/env python
# coding: utf-8

# ## קוד מבוא
# 

# ### ספריות
# 

# In[1]:


import os
import sys
import pandas as pd
import geopandas as gpd


# In[2]:


pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)


# ### העלאת משתנים להרצת הקוד
# 

# In[3]:


cwd = os.getcwd()

create_forecast_basic_folder_path = os.path.dirname(cwd)

sys.path.append(create_forecast_basic_folder_path)


# ## פונקציות
# 

# In[ ]:


from global_functions import get_newest_date_file, make_point, up_load_gdb, up_load_shp, up_load_df


# ### העלאת מידע
# 

# In[ ]:


stat=up_load_shp(r'{}\background_files\stat_11_cbs_2020_with_jtmt_fix.shp'.format(cwd))


# In[ ]:


stat_in_taz=stat.loc[stat['type_stat']=='in_taz']


# In[ ]:


stat=stat.loc[stat['type_stat']!='in_taz']


# In[ ]:


taz=up_load_shp(r'{}'.format(new_layer_path))


# In[ ]:


path=r'{}\background_files\BNTL_2022.gdb'.format(cwd)
bld=up_load_gdb(path,'BLDG_Clip')


# In[ ]:


path=r'{}\background_files\BNTL_2022.gdb'.format(cwd)
bld_poi=up_load_gdb(path,'POI_BLDG_Clip')


# In[ ]:


taz_not_relevant=up_load_df(r'{}\background_files'.format(cwd),'taz_not_relevant_for_pop_2020')


# In[ ]:


taz_not_relevant=list(taz_not_relevant.Taz_num)


# ### שכבת בניינים
# 

# In[ ]:


bld=bld.merge(bld_poi[[ 'FCODE', 'USG_GROUP', 'USG_CODE','USG_SP_NM_LTN','BLDG_ID']],how='left',left_on='UNIQ_ID',right_on='BLDG_ID')


# In[ ]:


bld=bld.loc[(bld['FCODE_y'].isna())|(bld['USG_CODE']==7600)] #זה קוד לבניינים מעורב שימושים אני מניח שעדיף לשים בניינים מיותרים מאשר הפוך


# In[ ]:


bld['bld_area']=bld.area


# In[ ]:


bld_point=make_point(bld).fillna(0)


# In[ ]:


bld_point.loc[bld_point['HEIGHT']<=0,'HEIGHT']=bld_point['HI_PNT_Z']-bld_point['HT_LAND']


# In[ ]:


ceiling_height=3


# In[ ]:


bld_point['bld_m3']=(bld_point['HEIGHT']/ceiling_height).astype(int)*bld_point['bld_area'].astype(int)


# In[ ]:


bld_point.loc[(bld_point['HEIGHT']-ceiling_height)<=0,'bld_m3']=bld_point['bld_area']


# ### הורדת מבנים לא רלוונטים
# 

# In[ ]:


bld_point=gpd.sjoin(bld_point,taz.loc[(~taz['Taz_num'].isin(taz_not_relevant))&(taz['main_secto']!="Palestinian")])


# In[ ]:


col=['bld_m3','centroid','Taz_num']


# In[ ]:


bld_point=bld_point[col]


# In[ ]:


bld_point=gpd.sjoin(bld_point,stat[['STAT','geometry']])


# In[ ]:


bld_point['bld_m3']=bld_point['bld_m3'].astype(int)


# ### יצירת מאה אחוז לכל א"ס
# 

# In[ ]:


sum_bld_m3=pd.pivot_table(bld_point.drop(columns='centroid'),index=['Taz_num','STAT'],aggfunc=sum)[['bld_m3']].reset_index()


# In[ ]:


sum_bld_m3_by_stat=sum_bld_m3.pivot_table(index='STAT',aggfunc=sum)[['bld_m3']].rename(columns={'bld_m3':'bld_m3_stat'}).reset_index()


# In[ ]:


sum_bld_m3=sum_bld_m3.merge(sum_bld_m3_by_stat,on='STAT')


# In[ ]:


sum_bld_m3['precent_of_stat_data']=sum_bld_m3['bld_m3']/sum_bld_m3['bld_m3_stat']


# In[ ]:


sum_bld_m3=sum_bld_m3.loc[(sum_bld_m3['precent_of_stat_data']>0.01)|(sum_bld_m3['Taz_num']==2001)]


# In[ ]:


sum_bld_m3_by_stat=sum_bld_m3.pivot_table(index='STAT',aggfunc=sum)[['bld_m3']].rename(columns={'bld_m3':'bld_m3_stat_new'}).reset_index()


# In[ ]:


sum_bld_m3=sum_bld_m3.merge(sum_bld_m3_by_stat,on='STAT')


# In[ ]:


sum_bld_m3['precent_of_stat_data']=sum_bld_m3['bld_m3']/sum_bld_m3['bld_m3_stat_new']


# ### א"ס ללא פוליגון
# 

# In[ ]:


stat_in_taz=make_point(stat_in_taz).sjoin(taz[['Taz_num','geometry']])[['STAT','Taz_num']]


# In[ ]:


stat_in_taz['precent_of_stat_data']=1


# ### איחוד לטבלה אחת
# 

# In[ ]:


col=['Taz_num', 'STAT',  'precent_of_stat_data']


# In[ ]:


precent_of_stat_data=pd.concat([sum_bld_m3[col], stat_in_taz])


# In[ ]:


file_date=pd.Timestamp.today().strftime('%y%m%d')

precent_of_stat_data.to_excel(r'{}\Monitoring\{}_precent_of_stat_data.xlsx'.format(cwd, file_date),index=False)


# ### יצירת מידע ברמת אזור תנועה
# 

# In[ ]:


stat_cbs_jtmt_2020_date = get_newest_date_file(r'{}\Intermediates'.format(cwd), 'stat_cbs_jtmt_2020')

stat=up_load_df(r'{}\Intermediates'.format(cwd), r'{}_stat_cbs_jtmt_2020'.format(stat_cbs_jtmt_2020_date))


# In[ ]:


col=['pop_0',
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
 'pop_75up']


# In[ ]:


stat[col]=stat[col].multiply(stat['pop'], axis="index")


# In[ ]:


stat['pop_hardi']=stat['pop']*(stat['pre_hardi']/100)


# In[ ]:


taz_stat_conver=precent_of_stat_data


# In[ ]:


col=['STAT',
 'aprt_20',
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
 'pop',
 'pop_hardi']


# בשכבת האזורי תנועה יהיו רק אזורי תנועה שמפצלים את המידע של למס
# 

# In[ ]:


taz=pd.merge(taz_stat_conver,stat[col],on='STAT',how='left')


# In[ ]:


col=['aprt_20',
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
 'pop',
 'pop_hardi']


# In[ ]:


taz[col]=taz[col].multiply(taz['precent_of_stat_data'], axis="index")


# In[ ]:


taz=pd.pivot_table(taz,index='Taz_num',aggfunc=sum)


# In[ ]:


taz['pre_hardi']=taz['pop_hardi']/taz['pop']


# In[ ]:


taz['hh_size']=taz['pop']/taz['aprt_20']


# In[ ]:


save_taz_path=r'{}\Intermediates'.format(cwd)


# In[ ]:


file_date=pd.Timestamp.today().strftime('%y%m%d')


# In[ ]:


taz.to_excel(r'{}\taz_with_pop_info.xlsx'.format(save_taz_path,file_date))

