#!/usr/bin/env python
# coding: utf-8

# ### קוד מבוא
# 

# In[ ]:


print(output_folder_path)
print(new_layer_path)


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
pd.options.display.float_format = '{:.4f}'.format
pd.set_option('display.float_format',  '{:,.2f}'.format)


# ### העלת משתנים להרצת הקוד
# 

# In[3]:


cwd = os.getcwd()

create_forecast_basic_folder_path = os.path.dirname(cwd)

sys.path.append(create_forecast_basic_folder_path)


# ### פונקציות
# 

# In[4]:


from global_functions import up_load_shp, up_load_df, drop_geo, up_load_gdb, make_point


# ### העלת טבלת המרה בין למס מרכזי למשני
# 

# In[5]:


stat_join_from_main_to_secondary=up_load_df(
        r'{}\background_files'.format(cwd),'stat_join_from_main_to_secondary')


# ### העלת טבלת יח*ד למ*ס
# 

# In[6]:


folder_path=r'{}\background_files'.format(cwd)
file_name='מספר דירות לפי אזורים סטטיסטיים'

path_df=r'{}\{}.xlsx'.format(folder_path,file_name)
df=pd.read_excel(path_df)
df=df.dropna(how='all')

stat_aprt=df


# In[7]:


col=['STAT', 'aprt_20']


# In[8]:


stat_aprt=stat_aprt[col]


# ### שכבת אזורים סטטיסטים
# 

# In[9]:


path=r'{}\background_files\statisticalareas_2020_demography.gdb'.format(cwd)
layer_list=fiona.listlayers(path)

layer_name='statisticalareas_2020_demography_jtmt_area'

gpd_layer=gpd.read_file(path, layer=layer_list.index(layer_name)).fillna(0)

stat=gpd_layer.rename(columns={'YISHUV_STAT11':'STAT'})


# In[10]:


col_name=['STAT','geometry']
stat=stat[col_name]


# In[11]:


stat=pd.merge(stat,stat_aprt,on='STAT',how='left').merge(stat_join_from_main_to_secondary,left_on='STAT',right_on='secondary_stat',how='left')


# In[12]:


stat.loc[stat['precent_of_stat_data'].isna(),'main_stat']=stat['STAT']


# In[13]:


stat.loc[stat['precent_of_stat_data'].isna(),'secondary_stat']=stat['STAT']


# In[14]:


stat.loc[stat['precent_of_stat_data'].isna(),'precent_of_stat_data']=1


# ### מידע ברמת רשות
# 

# In[15]:


stat_point=make_point(stat[['STAT', 'geometry']])


# In[16]:


muni_under_JTMT_ITM=up_load_gdb(r'{}\background_files\MUNI_border.gdb'.format(cwd),'muni_under_JTMT_ITM')


# In[17]:


muni_under_JTMT_ITM=muni_under_JTMT_ITM[['CR_PNIM','geometry']]


# In[18]:


stat=stat.set_index('STAT')


# In[19]:


stat['CR_PNIM']=stat_point.sjoin(muni_under_JTMT_ITM)[['STAT','CR_PNIM']].set_index('STAT')


# In[20]:


stat=stat.reset_index()


# ### העלת מידע אוכלוסייה
# 

# In[21]:


folder_path=r'{}\background_files'.format(cwd)
file_name='cbs_2020_with_age_distribution_type'

path_df=r'{}\{}.xlsx'.format(folder_path,file_name)
df=pd.read_excel(path_df,sheet_name='classification')
df=df.dropna(how='all')

classification=df


# In[22]:


col_name=['main_stat','classification_name']
classification=classification[col_name]


# In[23]:


classification=classification.drop_duplicates(subset='main_stat',keep='first')


# In[24]:


stat=pd.merge(stat,classification,on='main_stat',how='left')


# In[25]:


folder_path=r'{}\background_files'.format(cwd)
file_name='cbs_2020_with_age_distribution_type'

path_df=r'{}\{}.xlsx'.format(folder_path,file_name)
df=pd.read_excel(path_df,sheet_name='hh_size')
df=df.dropna(how='all')

hh_size=df


# In[26]:


stat=pd.merge(stat,hh_size,on='classification_name',how='left')


# In[27]:


folder_path=r'{}\background_files'.format(cwd)
file_name='cbs_2020_with_age_distribution_type'

path_df=r'{}\{}.xlsx'.format(folder_path,file_name)
df=pd.read_excel(path_df,sheet_name='types')
df=df.dropna(how='all')

age_des_types=df


# age*des_types.pivot_table(columns='age_name',index='classification_name',aggfunc=sum,values='perc').to_excel(r'\\FILE-SRV\Jtmt\projections_team\כללי\פעולות\יצירת*מצב*קיים*למס\חומר גלם\התפלגות*גילים*קטלוג\age_des_types_230719.xlsx')
# 

# In[28]:


folder_path=r'{}\background_files'.format(cwd)
file_name='cbs_2020_with_age_distribution_type'

path_df=r'{}\{}.xlsx'.format(folder_path,file_name)
df=pd.read_excel(path_df,sheet_name='absolute_numbers')
df=df.dropna(how='all').fillna(0)


cbs_pop=df


# In[29]:


cbs_pop['pop']=cbs_pop.iloc[:,3:].sum(axis=1)


# In[30]:


age=['0','5','10','15','20','25','30','35','40','45','50','55','60','65','70','75','80','85']


# In[31]:


for x in age:
    cbs_pop['pop_{}'.format(x)]= cbs_pop['female_{}'.format(x)]+cbs_pop['male_{}'.format(x)]


# In[32]:


cbs_pop['pop_75up']= cbs_pop[['pop_75', 'pop_80', 'pop_85']].sum(axis=1)


# In[33]:


col=[ 'main_stat', 'pop', 'pop_0', 'pop_5', 'pop_10', 'pop_15', 'pop_20', 'pop_25', 'pop_30', 'pop_35', 'pop_40', 'pop_45', 'pop_50',
 'pop_55',
 'pop_60',
 'pop_65',
 'pop_70',
 'pop_75up']


# In[34]:


cbs_pop=cbs_pop[col]


# יצירת טבלת התפלגות גילים באחוזים לטובת המשך הקוד כאשר יש שינויים בסך הכל אוכלוסיה אבל מעוניינים עדיין בהתפלגות גילים המקורית
# 

# In[35]:


cbs_pop_pre=cbs_pop.copy()


# In[36]:


col=list(cbs_pop_pre.iloc[:,1:])


# In[37]:


cbs_pop_pre.loc[:, col] = cbs_pop_pre.loc[:, col].div(cbs_pop_pre['pop'], axis=0)


# In[38]:


cbs_pop_pre=cbs_pop_pre.fillna(0)


# In[39]:


cbs_pop_pre=cbs_pop_pre.rename(columns={'pop':'pop_pre'})


# In[40]:


cbs_pop_pre=cbs_pop_pre.merge(cbs_pop[['main_stat', 'pop']],on='main_stat',how='left')


# In[41]:


stat=pd.merge(stat,cbs_pop_pre,on='main_stat',how='left')


# In[42]:


stat['pop']=stat['pop']*stat['precent_of_stat_data']


# ### אחוז חרדים מכלל א"ס
# 

# In[43]:


folder_path=r'{}\background_files'.format(cwd)
file_name='אוכלוסייה חרדית לפי מחוז, יישוב, ואזור סטטיסטי - 2020'

path_df=r'{}\{}.xlsx'.format(folder_path,file_name)
df=pd.read_excel(path_df)
df=df.dropna(how='all')

stat_hardi=df


# In[44]:


stat_hardi=stat_hardi[['pre_hardi','main_stat']].set_index('main_stat')


# In[45]:


stat=stat.set_index('main_stat')


# In[46]:


stat['pre_hardi']=stat_hardi['pre_hardi']


# In[47]:


stat['pre_hardi']=stat['pre_hardi'].fillna(0)


# ### תיקון שלב א ערבי ירושלים
# 

# In[48]:


path=r'{}\background_files\statisticalareas_2020_demography.gdb'.format(cwd)
layer_name='statisticalareas_2020_demography_arab_jtmt'

stat_arab=up_load_gdb(path,layer_name)


# In[49]:


col=['STAT', 'group_name']


# In[50]:


stat_arab=stat_arab[col]


# In[51]:


stat_arab=stat_arab.merge(cbs_pop_pre,left_on='STAT',right_on='main_stat',how='left')


# In[52]:


stat_arab=stat_arab.set_index('group_name')


# In[53]:


group_pop=stat_arab.groupby(by='group_name').sum()[['pop']]


# In[54]:


stat_arab['group_pop']=group_pop['pop']


# In[55]:


stat_arab['pre_from_group_pop']=stat_arab['pop']/stat_arab['group_pop']


# In[56]:


data = [['akev', 55000], ['Shuafat', 75000],['east_jeru_left',0]]


# In[57]:


group_pop_jtmt = pd.DataFrame(data, columns=['group_name', 'pop']).set_index('group_name')


# In[58]:


group_pop_delta=group_pop-group_pop_jtmt


# In[59]:


group_pop_delta=group_pop_delta.loc['east_jeru_left']+(group_pop_delta.loc['Shuafat']+group_pop_delta.loc['akev'])*0.8#בגלל שהדלתא מוסבר עי הגירה מיוש ולא רק מהעיר ירושלים 


# In[60]:


group_pop_jtmt.loc['east_jeru_left','pop']=group_pop_delta.item()


# In[61]:


stat_arab['group_pop_jtmt']=group_pop_jtmt['pop']


# In[62]:


stat_arab['pop']=stat_arab['pre_from_group_pop']*stat_arab['group_pop_jtmt']


# ### הטמעת תיקון שלב א
# 

# In[63]:


stat_arab=stat_arab.set_index('main_stat')


# In[64]:


stat['pop_cbs']=stat['pop']


# In[65]:


stat.loc[list(stat_arab.index),'pop']=stat_arab['pop']


# In[66]:


stat['change_from_cbs']=''


# In[67]:


stat.loc[list(stat_arab.index),'change_from_cbs']='| general_arab_change |'


# ### העלת א"ס בעייתי לתיקון שלב ב
# 

# In[68]:


path=r'{}\background_files\jtmt_fix_for_cbs_data_2020.shp'.format(cwd)

jtmt_fix_stat=up_load_shp(path)


# In[69]:


col=['STAT',
 'fix_pop',
 'fix_aprt',
 'fix_class']


# In[70]:


jtmt_fix_stat=jtmt_fix_stat[col].set_index('STAT')


# In[71]:


stat=stat.set_index('STAT')


# In[72]:


stat=stat.join(jtmt_fix_stat, how='left')


# ### יצירת גמ לפי קטלוג
# 

# In[73]:


cbs_not_lie_lst=list(stat.query('fix_pop.isna() & fix_aprt.isna() & fix_class.isna() ').index)


# In[74]:


stat['count']=1


# In[75]:


stat=stat.reset_index()


# In[76]:


stat.loc[stat['STAT'].isin(cbs_not_lie_lst),['fix_pop','fix_aprt','fix_class']]=1


# In[77]:


# hh_size_by_classification=stat.loc[(stat['aprt_20']>0)&(stat['STAT'].isin(cbs_not_lie_lst))].pivot_table(index='classification_name',aggfunc=sum)[['aprt_20','pop','count']]
hh_size_by_classification=drop_geo(stat).loc[(stat['aprt_20']>0)&(stat['STAT'].isin(cbs_not_lie_lst))].pivot_table(index='classification_name',aggfunc=sum)[['aprt_20','pop','count']]


# In[78]:


hh_size_by_classification['hh_size']=hh_size_by_classification['pop']/hh_size_by_classification['aprt_20']


# In[79]:


hh_size_by_classification=hh_size_by_classification[['hh_size','count']]


# In[80]:


hh_size=hh_size.merge(hh_size_by_classification.reset_index(),how='left',on='classification_name',suffixes=('','_cbs'))


# ### תיקון שלב ב
# 

# In[81]:


stat.loc[(stat['fix_pop']==0)&(stat['fix_aprt']==1)&(stat['fix_class']==1),'pop']=stat['aprt_20']*stat['hh_size']


# In[82]:


stat.loc[(stat['fix_pop']==0)&(stat['fix_aprt']==1)&(stat['fix_class']==1),'change_from_cbs']=stat['change_from_cbs']+'| pop_created_from_cbs_aprt |'


# In[83]:


stat.loc[(stat['fix_pop']==0)&(stat['fix_aprt']==0)&(stat['fix_class']==0),'pop']=0


# In[84]:


stat.loc[(stat['fix_pop']==0)&(stat['fix_aprt']==0)&(stat['fix_class']==0),'change_from_cbs']=stat['change_from_cbs']+'| cbs_pop_deleted |'


# In[85]:


stat['aprt_20_cbs']=stat['aprt_20']


# In[86]:


stat.loc[(stat['fix_pop']==0)&(stat['fix_aprt']==0)&(stat['fix_class']==0),'aprt_20']=0


# In[87]:


stat.loc[(stat['fix_pop']==0)&(stat['fix_aprt']==0)&(stat['fix_class']==0),'change_from_cbs']=stat['change_from_cbs']+'| cbs_aprt_deleted |'


# In[88]:


stat.loc[(stat['fix_pop']==1)&(stat['fix_aprt']==0)&(stat['fix_class']==1),'aprt_20']=stat['pop']/stat['hh_size']


# In[89]:


stat.loc[(stat['fix_pop']==1)&(stat['fix_aprt']==0)&(stat['fix_class']==1),'change_from_cbs']=stat['change_from_cbs']+'| aprt_created_from_pop |'


# כאן מתקנים מספר דירות לפי גודל משק בית באזורים ערביים שהגודל משק בית יותר או פחות 20% ממה שאנחנו חושבים שצריך להיות שם
# 

# In[90]:


stat.loc[(stat['classification_name'].str.contains("ערבי")==True)&(((stat['pop']/stat['aprt_20'])/stat['hh_size']>1.2)|((stat['pop']/stat['aprt_20'])/stat['hh_size']<0.8)),'aprt_20']=stat['pop']/stat['hh_size']


# In[91]:


stat.loc[(stat['classification_name'].str.contains("ערבי")==True)&(((stat['pop']/stat['aprt_20'])/stat['hh_size']>1.2)|((stat['pop']/stat['aprt_20'])/stat['hh_size']<0.8)),'change_from_cbs']=stat['change_from_cbs']+'| aprt_created_from_pop_because_hh_size_not_in_range |'


# ### יצירת דירות לפי גודל משק בית
# 

# In[92]:


stat.loc[((stat['aprt_20'].isna())|(stat['aprt_20']==0))&(stat['pop']>0),'change_from_cbs']=stat['change_from_cbs']+'| aprt_created_from_pop_because_no_cbs_data |'


# In[93]:


stat.loc[((stat['aprt_20'].isna())|(stat['aprt_20']==0))&(stat['pop']>0),'aprt_20']=round(stat['pop']/stat['hh_size'])


# ### בקרת מידע למס ברמה של רשות
# 

# In[94]:


pop_2020_cbs_muni=up_load_df(r'{}\background_files'.format(cwd),'pop_2020_cbs_muni')


# In[95]:


stat['CR_PNIM']=stat['CR_PNIM'].fillna(0).astype(int)


# In[96]:


# stat_by_muni_sum=stat.pivot_table(index='CR_PNIM',aggfunc=sum)[['pop_cbs','pop']]
stat_by_muni_sum=drop_geo(stat).pivot_table(index='CR_PNIM',aggfunc=sum)[['pop_cbs','pop']]


# In[97]:


pop_2020_cbs_muni=pop_2020_cbs_muni.set_index('CR_PNIM')


# In[98]:


pop_2020_cbs_muni.join(stat_by_muni_sum,how='inner')


# ### ייצא מידע ברמת אזור סטט עם השינוים שלנו
# 

# In[99]:


stat=stat.fillna(0)


# In[100]:


stat['pop_delta']=stat['pop']-stat['pop_cbs']


# In[101]:


stat['aprt_20_delta']=stat['aprt_20']-stat['aprt_20_cbs']


# In[102]:


col=['STAT','precent_of_stat_data','classification_name','pop','pop_cbs','aprt_20','aprt_20_cbs','pop_delta','aprt_20_delta','change_from_cbs']


# In[ ]:


file_date=pd.Timestamp.today().strftime('%y%m%d')


# In[110]:


stat[col].query('STAT!=5526 & STAT!=9975').to_excel(r'{}\Monitoring\{}_stat_cbs_jtmt_2020_short.xlsx'.format(cwd, file_date),index=False)


# In[111]:


stat.query('STAT!=5526 & STAT!=9975').to_excel(r'{}\Intermediates\{}_stat_cbs_jtmt_2020.xlsx'.format(cwd, file_date),index=False)


# path=r'\\FILE-SRV\Jtmt\projections*team\GIS_backround\INFO\למ*ס\אזורים סטטיסטים\statisticalareas_2020_demography.gdb'
# layer_list=fiona.listlayers(path)
# 
# layer_name='statisticalareas_2020_demography_jtmt_area'
# 
# gpd_layer=gpd.read_file(path, layer=layer_list.index(layer_name)).fillna(0)
# 
# stat_border=gpd_layer.rename(columns={'YISHUV_STAT11':'STAT'})
# 
# stat*border[['geometry','STAT']].merge(stat[col],on='STAT',how='right').query('STAT!=5526 & STAT!=9975').to_file(r'\\FILE-SRV\Jtmt\projections_team\כללי\פעולות\יצירת*מצב*קיים*למס\output\stat_cbs_jtmt_2020.shp',encoding='utf-8')
# 
