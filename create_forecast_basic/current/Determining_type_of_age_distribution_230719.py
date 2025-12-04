#!/usr/bin/env python
# coding: utf-8

# ### ספריות
# 

# In[1]:


import os
import sys
import pandas as pd
import geopandas as gpd
import numpy as np


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


# ### פונקציות
# 

# In[4]:


from global_functions import up_load_shp, find_files_with_pattern, get_newest_date_file, get_forecast_version_folder_location


# In[5]:


forecast_version_folder_location=get_forecast_version_folder_location(r'{}\background_files\forecast_version_folder_location.txt'.format(create_forecast_basic_folder_path))

forecast_version_folder_location=r'{}\BASE_YEAR'.format(forecast_version_folder_location)


# ### העלת שכבות רלוונטים
# 

# In[6]:


file_date = get_newest_date_file(forecast_version_folder_location, 'BaseProjections2020')


# In[7]:


prototypes_df=pd.read_excel(r"{}\background_files\age_des_types.xlsx".format(create_forecast_basic_folder_path))


# In[8]:


data_df = pd.read_excel(r'{}\BaseProjections2020_{}.xlsx'.format(forecast_version_folder_location, file_date))


# In[9]:


TAZ_V4_date = get_newest_date_file(create_forecast_basic_folder_path, 'with_geo_info')

sectors=gpd.read_file(r'{}\background_files\TAZ_V4_{}_with_geo_info.shp'.format(create_forecast_basic_folder_path, TAZ_V4_date))


# In[10]:


data_df=sectors[['Taz_num','Muni_Heb']].merge(data_df,left_on='Taz_num',right_on='TAZ',how='right')


# In[11]:


data_df['sector_for_age']=data_df['sector']


# In[12]:


data_df.loc[
    (data_df['yosh'] == 1) &
    (data_df['sector'] != 'U_Orthodox'),'sector_for_age'
]='hitnachlut'


# In[13]:


lst_muni=['מעלה אדומים',
 'גבעת זאב',
 'הר אדר',
 '0',
 'מעלה אפרים',
 'מגילות ים המלח\r\n',
 'קרני שומרון',
 'אלפי מנשה',
 'בית אריה-עופרים',
 'ערבות הירדן\r\n',
 'אריאל']


# In[14]:


data_df.loc[data_df['Muni_Heb'].isin(lst_muni),'sector_for_age'
]='Jewish'


# In[15]:


data_df.loc[
    (data_df['sector'] == 'arabs_behined_seperation_wall') |
    (data_df['sector'] == 'Arab'),'sector_for_age'
]='Arab'


# In[16]:


data_df=data_df.loc[
    (data_df['sector'] != 'Palestinian')
]


# In[17]:


col=[ 'age0_4',
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
 'age75up']


# In[18]:


# Convert counts to percentages
data_df_pre = data_df[col].apply(lambda x: x / x.sum(), axis=1)


# In[19]:


data_df=data_df.join(data_df_pre,lsuffix='', rsuffix='_prec')


# In[20]:


col_name_prototype=['pop_0','pop_5',
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


# In[21]:


col_name_row=['age0_4_prec',
 'age5_9_prec',
 'age10_14_prec',
 'age15_19_prec',
 'age20_24_prec',
 'age25_29_prec',
 'age30_34_prec',
 'age35_39_prec',
 'age40_44_prec',
 'age45_49_prec',
 'age50_54_prec',
 'age55_59_prec',
 'age60_64_prec',
 'age65_69_prec',
 'age70_74_prec',
 'age75up_prec']


# In[22]:


ls_sector=['U_Orthodox', 'Jewish', 'hitnachlut', 'Arab']


# In[23]:


for s in ls_sector:
    locals()['data_df_{}'.format(s)]=data_df.loc[data_df['sector_for_age']=='{}'.format(s)]
    locals()['prototypes_df_{}'.format(s)]=prototypes_df.loc[prototypes_df['sector']=='{}'.format(s)]


# In[24]:


for s in ls_sector:
    for index, row in locals()['data_df_{}'.format(s)].iterrows():
        # Step 3: Calculate similarity scores
        similarity_scores = []
        for _, prototype_row in locals()['prototypes_df_{}'.format(s)].iterrows():
            prototype_age_distributions = prototype_row[col_name_prototype].values 
            data_age_distributions = row[col_name_row].values         
            similarity_score = np.linalg.norm(prototype_age_distributions - data_age_distributions)
            similarity_scores.append(similarity_score)

        # Step 4: Determine closest prototype
        closest_index = np.argmin(similarity_scores)
        closest_prototype = locals()['prototypes_df_{}'.format(s)].iloc[closest_index]['classification_name']


        # Assign closest_prototype to the corresponding row in data_df or perform any desired action

        locals()['data_df_{}'.format(s)].at[index,'classification_name'] = closest_prototype



# In[25]:


data_df=pd.concat([data_df_U_Orthodox,data_df_Jewish,data_df_hitnachlut,data_df_Arab],axis=0)


# In[26]:


data_df[['Taz_num','sector_for_age','classification_name']].to_excel(r'{}\Intermediates\forecast_2020_{}_age_dis_type.xlsx'.format(cwd, file_date),index=False)

