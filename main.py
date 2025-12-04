#!/usr/bin/env python
# coding: utf-8

# ### ספריות
# 

# In[1]:


import os
import sys
import pandas as pd


# In[2]:


pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)


# In[3]:


file_date=pd.Timestamp.today().strftime('%y%m%d')


# ### העלת משתנים להרצת הקוד
# 

# In[4]:


cwd = os.getcwd()

df_inputs_outputs = pd.read_excel(r'{}\inputs_outputs.xlsx'.format(cwd))

create_forecast_basic_location= r'{}\create_forecast_basic'.format(cwd)


# In[5]:


client_data_folder_location=df_inputs_outputs['location'][0]
forecast_version=df_inputs_outputs['location'][1]
v_date=df_inputs_outputs['location'][2]


# In[6]:


index_with_poten=df_inputs_outputs['location'][3]


# In[7]:


if index_with_poten==1:
    index_file_name='index_format_for_creating_forecast_jtmt_input_{}_{}_with_poten_jtmt'.format(forecast_version,v_date)
else:
    index_file_name='index_format_for_creating_forecast_jtmt_input_{}_{}'.format(forecast_version,v_date)   


# ### פונקציות גלובליות
# 

# In[8]:


import os

def remove_invisible_marks(directory="."):
    """
    מסיר את סימני הכיווניות הבלתי נראים (RLM ו-LRM) משמות כל הקבצים בתיקייה.

    Args:
        directory (str, optional): נתיב התיקייה שבה יש לבצע את השינוי. ברירת מחדל היא התיקייה הנוכחית.
    """
    for filename in os.listdir(directory):
        new_filename = filename.replace('\u200f', '').replace('\u200e', '')
        if new_filename != filename:
            old_path = os.path.join(directory, filename)
            new_path = os.path.join(directory, new_filename)
            try:
                os.rename(old_path, new_path)
                print(f"שם הקובץ '{filename}' שונה ל '{new_filename}'")
            except OSError as e:
                print(f"שגיאה בשינוי שם הקובץ '{filename}': {e}")

if __name__ == "__main__":
    remove_invisible_marks()
    print("\nסימני הכיווניות הוסרו משמות כל הקבצים בתיקייה הנוכחית (אם היו כאלה).")


# In[9]:


from global_functions import up_load_gdb, make_point, find_files_with_pattern, up_load_shp, up_load_df, split_index_by_taz, delete_and_add_by_TAZ, change_Muni_Heb_to_Muni_Eng, find_geographic_layers


# ### העלת אזורי תנועה לחישוב
# 

# In[10]:


folder_path=r'{}\For_approval\Reference_tabels\shp'.format(client_data_folder_location)

gpd_name='tochnit_check.gdb'

forecast = up_load_gdb(r'{}\{}'.format(folder_path,gpd_name),'TAZ_211028_V3_Published_with_client_changes')


# ### הוספת מאפיינים גיאוגרפים לאזורי תנועה
# 

# In[ ]:


forecast_point = make_point(forecast)

    # Load data layers
urban = up_load_shp(
        r'{}\background_files\urban.shp'.format(cwd))
SCHOOLDISTRICT = up_load_shp(
        r'{}\background_files\SCHOOLDISTRICT.shp'.format(cwd))
PUMA = up_load_shp(
        r'{}\background_files\poly_pumas_v1.shp'.format(cwd))


# In[12]:


jerusalem_city =  up_load_shp(
        r'{}\background_files\in_jeru.shp'.format(cwd))

subdistrict_il = up_load_gdb(
        r'{}\background_files\subdistrict2008.gdb'.format(cwd), 'subdistrict2008_ITM')
muni_JTMT = up_load_gdb(
        r'{}\background_files\MUNI_border.gdb'.format(cwd), 'muni_under_JTMT_ITM')

# מעלה את השכבה
jeru_metro_jtmt_border = up_load_shp(r'{}\background_files\jeru_metro_jtmt_border_240402.shp'.format(cwd))


# In[ ]:


# Geographical join between traffic zones and data layers
forecast_point_urban = forecast_point.sjoin(
        urban)[['Taz_num', 'Urban']]
forecast_point_SCHOOLDISTRICT = forecast_point.sjoin(
        SCHOOLDISTRICT)[['Taz_num', 'SCHOOLDIST']]
forecast_point_PUMA = forecast_point.sjoin(
        PUMA)[['Taz_num', 'poly_puma', 'F3', 'F2', 'F1']]
forecast_point_jerusalem_city = forecast_point.sjoin(
        jerusalem_city)[['Taz_num', 'in_jerusal']]
forecast_point_subdistrict_il = forecast_point.sjoin(
        subdistrict_il[['geometry', 'ENG_NAME_nafa']])[['Taz_num', 'ENG_NAME_nafa']]
forecast_point_muni_JTMT = forecast_point.query('main_sector!="Palestinian"').sjoin(
        muni_JTMT[['Muni_Heb', 'Sug_Muni', 'CR_PNIM', 'geometry']], how='left')[['Taz_num', 'Muni_Heb', 'Sug_Muni', 'CR_PNIM']]
forecast_point_jeru_metro_jtmt_border = forecast_point.sjoin(
        jeru_metro_jtmt_border)[['Taz_num', 'jeru_metro']]

# Merge tables into one table
forecast = (forecast
                .merge(forecast_point_subdistrict_il, on='Taz_num', how='left')
                .merge(forecast_point_muni_JTMT, on='Taz_num', how='left')
                .merge(forecast_point_jeru_metro_jtmt_border, on='Taz_num', how='left')
                .merge(forecast_point_urban, on='Taz_num', how='left')
                .merge(forecast_point_SCHOOLDISTRICT, on='Taz_num', how='left')
                .merge(forecast_point_PUMA, on='Taz_num', how='left')
                .merge(forecast_point_jerusalem_city, on='Taz_num', how='left'))

# Rename columns# Rename columns with flipped names
forecast.rename(columns={'ENG_NAME_nafa': 'zonetype'}, inplace=True)
forecast.rename(columns={'Urban': 'urban'}, inplace=True)
forecast.rename(columns={'SCHOOLDIST': 'SCHOOLDISTRICT'}, inplace=True)


# Data processing for feature columns
forecast.loc[forecast['main_sector'] == 'Palestinian', 'zonetype'] = 'Palestinian'
forecast['in_jerusalem_metropolin'] = 1
forecast.loc[forecast['jeru_metro'] == 0, 'in_jerusalem_metropolin'] = 0
forecast['yosh'] = 0
forecast.loc[forecast['zonetype'] == 'Judea and Samaria', 'yosh'] = 1
forecast.loc[forecast['in_jerusal'] == 'no', 'jerusalem_city'] = 0
forecast.loc[forecast['in_jerusal'] == 'yes', 'jerusalem_city'] = 1

# Add constant columns
forecast['REGION'] = 1
forecast['slope'] = 0


# In[14]:


forecast.loc[forecast['in_jerusal'].isna(), 'in_jerusal'] = 'no'


# In[15]:


forecast.loc[forecast['main_sector'] == 'U_Orthodox', 'PUMA'] = forecast['F2']
forecast.loc[forecast['main_sector'] == 'Jewish', 'PUMA'] = forecast['F3']
forecast.loc[forecast['main_sector'] == 'Arab', 'PUMA'] = forecast['F1']
forecast.loc[forecast['main_sector'] == 'arabs_behined_seperation_wall', 'PUMA'] = forecast['F1']


# In[16]:


forecast = forecast.set_index('Taz_num')
forecast['Taz_num'] = forecast.index


# ### שינוי עמודה Muni_Heb
# 

# In[17]:


forecast=change_Muni_Heb_to_Muni_Eng(cwd, forecast)#


# ### ייצוא שכבת אזורי תנועה לבקרת לקוח
# 

# In[18]:


save_shp_path=r'{}\For_approval\{}_taz_for_approval.shp'.format(client_data_folder_location,file_date)

col=['Taz_num','Name_hebre','Muni_Eng', 'main_sector', 'classification_name','Student_by_Classrooms','geometry']

forecast[col].to_file(save_shp_path,index=False,encoding='UTF-8')


# In[19]:


new_taz_made=df_inputs_outputs['location'][4]


# In[20]:


if new_taz_made==1:
    save_shp_path=r'{}\{}_new_taz_for_project.shp'.format(client_data_folder_location,file_date)

    col=['Taz_num','geometry']

    forecast[col].to_file(save_shp_path,index=False,encoding='UTF-8')


# ### מצב קיים לבקרה
# 

# In[21]:


# נתיב לתיקיית בסיס
output_folder_path = r'{}\For_approval\Reference_tabels'.format(client_data_folder_location)

# תבנית לחיפוש שכבות חדשות
pattern='TAZ_V'
matching_files = find_geographic_layers(r'{}\shp'.format(output_folder_path), pattern, '.shp')

forecast_2020=None


# In[22]:


from create_forecast_basic.run_basic import run_notebook  # ייבוא הפונקציה

notebook_path = r'{}\run_basic.ipynb'.format(create_forecast_basic_location)

# אם יש שכבות חדשות
if matching_files:
    print("Using Ad-Hoc Layers...")
    new_layer_path = matching_files[0]
    os.chdir(r'{}'.format(create_forecast_basic_location))

    # הרצת מחברת עם שכבות אד-הוק
    params = {"output_folder_path": output_folder_path, "new_layer_path": new_layer_path}
    execution_result = run_notebook(notebook_path, params)

    if execution_result:
        forecast_2020 = up_load_df(r'{}'.format(output_folder_path), 
                                       r'2020_jtmt_forcast_full_{}_with_taz_changes'.format(file_date))

        col=[]

        forecast_2020['student_toddlers']=0
        forecast_2020['student_gov']=forecast_2020['student']
        forecast_2020['cbs_muni_student_left_by_pre_of_demand_left']=forecast_2020['student']
        forecast_2020['uni_students']=forecast_2020['univ']
        forecast_2020['emp_from_uni_student']=forecast_2020['emp_uni']
        forecast_2020['student_yeshiva']=forecast_2020['student_yeshiva_and_kollim']

        col_20=['Taz_num','Taz_name',
                'main_secto',
                'aprt_20', 'pop_without_dorms_yeshiva',
                'student_toddlers',
                'student_gov',
                'cbs_muni_student_left_by_pre_of_demand_left',
                'uni_students', 'student_dorms',
                'emp_from_uni_student',
                'student_yeshiva',
                'emp_okev',
                'emp_not_okev','student']

        forecast_2020=pd.merge(forecast[col].reset_index(),forecast_2020[col_20],how='left',on='Taz_num').fillna(0)

        save_excel_path=r'{}\For_approval\{}_forecast_2020_For_approval.xlsx'.format(client_data_folder_location,file_date)

        forecast_2020[col_20].to_excel(save_excel_path,index=False)


# In[23]:


if not matching_files:
    forecast_2020=up_load_df(r'{}\background_files'.format(cwd),'2020_jtmt_forcast_full_230720')

    col=[]

    # forecast_2020['student_toddlers']=0
    # forecast_2020['student_gov']=forecast_2020['student']
    # forecast_2020['cbs_muni_student_left_by_pre_of_demand_left']=forecast_2020['student']
    # forecast_2020['uni_students']=forecast_2020['univ']
    # forecast_2020['emp_from_uni_student']=forecast_2020['emp_uni']
    # forecast_2020['student_yeshiva']=forecast_2020['student_yeshiva_and_kollim']

    col_20=['Taz_num','Taz_name',
        'main_secto',
        'aprt_20', 'pop_without_dorms_yeshiva',
        'student_toddlers',
        'student_gov',
        'cbs_muni_student_left_by_pre_of_demand_left',
        'uni_students', 'student_dorms',
        'emp_from_uni_student',
        'student_yeshiva',
        'emp_okev',
        'emp_not_okev','student']

    forecast_2020=pd.merge(forecast[col].reset_index(),forecast_2020[col_20],how='left',on='Taz_num').fillna(0)

    save_excel_path=r'{}\For_approval\{}_forecast_2020_For_approval.xlsx'.format(client_data_folder_location,file_date)

    forecast_2020[col_20].to_excel(save_excel_path,index=False)


# ### העלאת מרכיבי טבלת אינדקס
# 

# #### צריך להחליט האם להשתמש בגבול אינדקס או בעיבוד שכולל יצירת פוטנציאל
# 

# In[24]:


if index_with_poten==0:
    borders_index=up_load_shp(r'{}\For_approval\Reference_tabels\shp\gvul_index.shp'.format(client_data_folder_location))
    path_to_upload=r'{}\For_approval\Reference_tabels'.format(client_data_folder_location)
else:
    borders_index=up_load_shp(r'{}\For_approval\Reference_tabels\shp\gvul_index_with_ponten.shp'.format(client_data_folder_location))
    path_to_upload=r'{}\For_approval\Reference_tabels'.format(client_data_folder_location)


# In[25]:


remove_invisible_marks(path_to_upload)


# In[26]:


index=up_load_df(path_to_upload,index_file_name)
index=pd.merge(borders_index,index,on='id',how='right')


# ### חלוקה לאזורי תנועה של התכניות
# 

# In[27]:


col=['add_uni_dorms',
    'add_old_age_home',
    'add_aprt',
    'Commerce_m2',
    'Business_m2',
    'Tourism_m2',
    'Public_m2',
    'Industry_m2',
    'emp_Public',
    'emp_Education',
    'emp_Commerce',
    'emp_Business',
    'emp_Industry',
    'emp_Tourism',
    'Classrooms',
    'add_uni_students']

index=split_index_by_taz(index,forecast,0.05,col)


# ### שכבת אינדקס
# 

# In[28]:


index=index.fillna(0)

promoteres_df = pd.read_excel(r'{}\background_files\promoteres.xlsx'.format(cwd))

#מקדים לייצרת תעסוקה עוקב משקי בית
Industry_precent_per_hh=promoteres_df['value'][0]
Commerce_precent_per_hh=promoteres_df['value'][1]
Business_precent_per_hh=promoteres_df['value'][2]
Public_precent_per_hh=promoteres_df['value'][3]
Agriculture_precent_per_hh=promoteres_df['value'][4]
precent_emp_per_hh=promoteres_df['value'][5]

#מקדימים לייצרת מקומות עבודה מ"ר לפי ייעוד קרקע
m2_Industry_to_emp=promoteres_df['value'][6]
m2_Commerce_Hotel_to_emp=promoteres_df['value'][7]
m2_Business_to_emp=promoteres_df['value'][8]
m2_Public_to_emp=promoteres_df['value'][9]
m2_Agriculture_to_emp=promoteres_df['value'][10]
m2_Education_to_emp=promoteres_df['value'][11]
m2_Commerce_to_emp=m2_Commerce_Hotel_to_emp
m2_Tourism_to_emp=promoteres_df['value'][13]

#מילוי
old_age_home_fill=promoteres_df['value'][14]
uni_student_dorm_fill=promoteres_df['value'][15]

#מקדימי תעסוקה בעקבות חינוך
emp_education_per_student=promoteres_df['value'][16]
emp_Education_per_uni_student=promoteres_df['value'][17]
emp_Education_per_Yeshiva_student=promoteres_df['value'][18]


convert_dict={
'add_old_age_home': float,
'add_aprt': float,
'Commerce_m2': float,
'Business_m2': float,
'Tourism_m2': float,
'Public_m2': float,
'Industry_m2': float,
'emp_Public': float,
'emp_Education': float,
'emp_Commerce': float,
'emp_Business': float,
'emp_Industry': float,
'emp_Tourism': float,
'Classrooms': float,
'F2025': float,
'F2030': float,
'F2035': float,
'F2040': float,
'F2045': float,
'F2050': float,
'F2050_plus': float,
'Risk_factor': float,
'emp_fill_factor': float}

index = index.astype(convert_dict)

col_to_sum=['F2025',
'F2030',
'F2035',
'F2040']

index['precent_till_2040']=index[col_to_sum].sum(axis=1)

index['add_aprt_nominally']=index['add_aprt']

index['add_aprt']=index['add_aprt']*index['precent_till_2040']*index['Risk_factor']

index['Classrooms_nominally']=index['Classrooms']

index['Classrooms']=index['Classrooms']*index['precent_till_2040']*index['Risk_factor']

index['add_old_age_home_nominally']=index['add_old_age_home']

index['add_old_age_home']=index['add_old_age_home']*index['precent_till_2040']*index['Risk_factor']

index['add_uni_students_nominally']=index['add_uni_students']

index['add_uni_students']=index['add_uni_students']*index['precent_till_2040']*index['Risk_factor']

index['add_uni_dorms_nominally']=index['add_uni_dorms']

index['add_uni_dorms']=index['add_uni_dorms']*index['precent_till_2040']*index['Risk_factor']

list_category=['Commerce','Business','Industry','Tourism','Public']   #'Agriculture','Education','Public'
for c in list_category:
    index['{}_m2_nominally'.format(c)]=index['{}_m2'.format(c)]
    index['{}_m2'.format(c)]=index['{}_m2'.format(c)]*index['Risk_factor']*index['emp_fill_factor']*index['precent_till_2040']
    index['emp_{}_nominally'.format(c)]=index['emp_{}'.format(c)]
    index['emp_{}'.format(c)]=index['emp_{}'.format(c)]*index['precent_till_2040']*index['Risk_factor']*index['emp_fill_factor']
    index['add_emp_{}'.format(c)]=index['emp_{}'.format(c)]+index['{}_m2'.format(c)]/locals()['m2_{}_to_emp'.format(c)]




# ### ייצוא שכבת אינדקס לבקרת לקוח
# 

# In[29]:


index=index.drop(['geometry'], axis=1)


# In[30]:


col=['id',
'add_aprt',
'add_aprt_nominally',
'add_old_age_home',
'add_old_age_home_nominally',
'add_uni_dorms',
'add_uni_dorms_nominally',
'add_uni_students',
'add_uni_students_nominally',
'Classrooms','Classrooms_nominally',
'Commerce_m2',
'Commerce_m2_nominally',
'add_emp_Commerce',
'Tourism_m2',
'Tourism_m2_nominally',
'add_emp_Tourism',
'Business_m2',
'Business_m2_nominally',
'add_emp_Business',
'Public_m2',
'Public_m2_nominally',
'add_emp_Public',
'Industry_m2',
'Industry_m2_nominally',
'add_emp_Industry']

save_excel_path=r'{}\For_approval\Reference_tabels\{}_index_{}_For_approval.xlsx'.format(client_data_folder_location,file_date,forecast_version)
index.reset_index()[col].pivot_table(index='id',aggfunc=sum).to_excel(save_excel_path,index=True)


# In[31]:


col=['Taz_num','id',
    'add_aprt',
    'add_aprt_nominally',
    'add_old_age_home',
    'add_old_age_home_nominally',
    'add_uni_dorms',
    'add_uni_dorms_nominally',
    'add_uni_students',
    'add_uni_students_nominally',
    'Classrooms','Classrooms_nominally',
    'Commerce_m2',
    'Commerce_m2_nominally',
    'add_emp_Commerce',
    'Tourism_m2',
    'Tourism_m2_nominally',
    'add_emp_Tourism',
    'Business_m2',
    'Business_m2_nominally',
    'add_emp_Business',
    'Public_m2',
    'Public_m2_nominally',
    'add_emp_Public',
    'Industry_m2',
    'Industry_m2_nominally',
    'add_emp_Industry']
index=index[col].pivot_table(index='Taz_num', aggfunc='sum').fillna(0)


# In[32]:


col=[ 'add_aprt','add_uni_dorms', 'add_emp_Business',
'add_emp_Commerce',
    'add_emp_Industry',
    'add_emp_Public',
    'add_emp_Tourism','add_uni_students','add_old_age_home','Classrooms']

forecast=forecast.merge(index[col],left_index=True,right_index=True,how='left')

forecast=forecast.fillna(0)

col=['aprt_20','student','uni_students','student_dorms','student_yeshiva','emp_not_okev']

forecast_2020=forecast_2020.set_index('Taz_num')

forecast=forecast.merge(forecast_2020[col],left_index=True,right_index=True,how='left')

forecast=forecast.rename(columns={'student':'student_20','uni_students':'uni_students_20','student_dorms':'student_dorms_20','student_yeshiva':'student_yeshiva_and_kollim_20','emp_not_okev':'emp_not_okev_20'})

age_des_types=up_load_df(r'{}\background_files'.format(cwd),'age_des_types')

forecast=forecast.merge(age_des_types,on='classification_name',how='left').fillna(0)

#### יח"ד של השכונה ויצירת אנשים לפי קטלוג
forecast['aprt']=forecast['aprt_20']+forecast['add_aprt']

forecast['pop_without_dorms_yeshiva']=forecast['aprt']*forecast['hh_size']

#### תלמידים בעקבות האוכלוסיה
forecast['student_demand_pre']=forecast['pop_0']/5*2+forecast['pop_5']+forecast['pop_10']+forecast['pop_15']/5*3+forecast['pop_0']/5*3*0.5

forecast['student_demand']=forecast['student_demand_pre']*forecast['pop_without_dorms_yeshiva']

#### המרת התפלגות גילים מאחוזים למספרים מוחלטים
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

forecast[col]=forecast[col].multiply(forecast['pop_without_dorms_yeshiva'], axis="index")


# In[33]:


forecast['student_to_fill_demand']=forecast['student_demand']-forecast['student_20']

forecast.loc[forecast['student_to_fill_demand']<0,'student_to_fill_demand']=0


# In[34]:


forecast['student']=forecast['student_to_fill_demand']+forecast['student_20']

forecast.loc[forecast['Student_by_Classrooms']==1,'student']=forecast['Classrooms']*30

forecast.loc[forecast['Student_by_Classrooms']==1,'student']=forecast['Classrooms']*30

#### תעסוקה בעקבות תלמידים
forecast['emp_from_student']=forecast['student']/emp_education_per_student

#### סטודנטים
forecast['student_dorms']=forecast['add_uni_dorms']*uni_student_dorm_fill+forecast['student_dorms_20']

#### מספר הסטודנטים יהיה בהתאם לגודל של הקיים
forecast['uni_students']=forecast['uni_students_20']+forecast['add_uni_students']

#### תעסוקה בעקבות סטודנטים
forecast['emp_from_uni_student']=forecast['uni_students']*emp_Education_per_uni_student


# In[35]:


#### תלמידי ישיבה ותעסוקה מישיבה
forecast['student_yeshiva_and_kollim']=forecast['student_yeshiva_and_kollim_20']*1.15 #גידול מינורי


# In[36]:


kollim_factor=df_inputs_outputs['location'][5]


# In[37]:


#אופציה שנייה ליצירת אומדן לישיבות
if kollim_factor > 0:
    forecast['student_yeshiva_and_kollim'] = forecast['student_yeshiva_and_kollim_20'] +(
        forecast['pop_20'] * 0.8 +
        forecast['pop_25'] * 0.65 +
        forecast['pop_30'] * 0.30 +
        forecast['pop_35'] * 0.30 +
        forecast['pop_40'] * 0.30 +
        forecast['pop_45'] * 0.20 +
        forecast['pop_50'] * 0.20 +
        forecast['pop_55'] * 0.20 +
        forecast['pop_60'] * 0.20
    ) * 0.5 * kollim_factor



# In[38]:


forecast['emp_from_Yeshiva_student']=forecast['student_yeshiva_and_kollim']*emp_Education_per_Yeshiva_student

forecast['emp_Education']=forecast['emp_from_student']+forecast['emp_from_Yeshiva_student']+forecast['emp_from_uni_student']

#### תעסוקה לא עוקב
#### מקומות עבודה תעשייה

forecast['Indus']=forecast['add_emp_Industry']+forecast['emp_not_okev_20']*0.0 #חלוקת מצב הקיים הערכה 

#### מקומות עבודה מסחר ומלונאות
forecast['Com_hotel']=forecast['add_emp_Commerce']+forecast['add_emp_Tourism']+forecast['emp_not_okev_20']*0.5 #חלוקת מצב הקיים הערכה 

#### מקומות עבודה משרדים
forecast['Business']=forecast['add_emp_Business']+forecast['emp_not_okev_20']*0.5 #חלוקת מצב הקיים הערכה 

forecast['agri']=0

forecast['Public']=0

#### מקומות עבודה עוקב משקי בית 
forecast['emp_okev']=forecast['aprt']*precent_emp_per_hh

#### מקומות עבודה עוקב אוכלוסייה
list_category=[	'Com_hotel','Business','Indus','Public'] 
list_category_index=['Commerce','Business','Industry','Public'] 

for c,i in zip(list_category, list_category_index):
    forecast['{}'.format(c)]= forecast['{}'.format(c)].fillna(0)+forecast['emp_okev']*locals()['{}_precent_per_hh'.format(i)]

#### סך מקומות עבודה
col_to_sum_emp=['Indus',
'Com_hotel',
'Business',
'Public',
'emp_Education','agri']

forecast['total_emp']=forecast[col_to_sum_emp].sum(axis=1)

#### הוספת סטודנטים למשקי הבית, אוכלוסיה ותפלגות גילים
forecast['pop']=forecast['pop_without_dorms_yeshiva']+forecast['student_dorms']

forecast['pop_20']=forecast['pop_20']+forecast['student_dorms']*0.6

forecast['pop_25']=forecast['pop_25']+forecast['student_dorms']*0.4

forecast['hh']=forecast['aprt']+forecast['student_dorms']/uni_student_dorm_fill

#### הוספת דיור מוגן למשקי הבית, אוכלוסיה ותפלגות גילים
forecast['pop']=forecast['pop']+forecast['add_old_age_home']*old_age_home_fill

forecast['pop_75up']=forecast['pop_75up']+forecast['add_old_age_home']*old_age_home_fill

forecast['hh']=forecast['hh']+forecast['add_old_age_home']

#### יצירת עמודת יוצאים לעבודה מתוך האוכלוסייה שגרה
pre_woman=0.5

pre_man=1-pre_woman

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

forecast['work_age']=forecast[work_age].sum(axis=1)

forecast['under_work_age']=forecast[under_work_age].sum(axis=1)

forecast['over_work_age']=forecast[over_work_age].sum(axis=1)

sector='U_Orthodox'

forecast.loc[forecast['main_sector']==sector,'pop_emp']=forecast['work_age']*pre_woman*0.75+forecast['work_age']*pre_man*0.44
forecast.loc[forecast['main_sector']==sector,'pop_emp']=forecast['pop_emp']+forecast['under_work_age']*pre_woman*0.07+forecast['under_work_age']*pre_man*0.09
forecast.loc[forecast['main_sector']==sector,'pop_emp']=forecast['pop_emp']+forecast['over_work_age']*pre_woman*0.05+forecast['over_work_age']*pre_man*0.09

sector='Jewish'

forecast.loc[forecast['main_sector']==sector,'pop_emp']=forecast['work_age']*pre_woman*0.84+forecast['work_age']*pre_man*0.87
forecast.loc[forecast['main_sector']==sector,'pop_emp']=forecast['pop_emp']+forecast['under_work_age']*pre_woman*0.20+forecast['under_work_age']*pre_man*0.15
forecast.loc[forecast['main_sector']==sector,'pop_emp']=forecast['pop_emp']+forecast['over_work_age']*pre_woman*0.05+forecast['over_work_age']*pre_man*0.09

sector='Arab'

forecast.loc[forecast['main_sector']==sector,'pop_emp']=forecast['work_age']*pre_woman*0.23+forecast['work_age']*pre_man*0.78
forecast.loc[forecast['main_sector']==sector,'pop_emp']=forecast['pop_emp']+forecast['under_work_age']*pre_woman*0.2+forecast['under_work_age']*pre_man*0.15
forecast.loc[forecast['main_sector']==sector,'pop_emp']=forecast['pop_emp']+forecast['over_work_age']*pre_woman*0.05+forecast['over_work_age']*pre_man*0.09

sector='arabs_behined_seperation_wall'

forecast.loc[forecast['main_sector']==sector,'pop_emp']=forecast['work_age']*pre_woman*0.23+forecast['work_age']*pre_man*0.78
forecast.loc[forecast['main_sector']==sector,'pop_emp']=forecast['pop_emp']+forecast['under_work_age']*pre_woman*0.2+forecast['under_work_age']*pre_man*0.15
forecast.loc[forecast['main_sector']==sector,'pop_emp']=forecast['pop_emp']+forecast['over_work_age']*pre_woman*0.05+forecast['over_work_age']*pre_man*0.09

## חישוב אבטלה
forecast['pop_emp_employed']=0

forecast.loc[forecast['main_sector']=="U_Orthodox",'pop_emp_employed']=forecast['pop_emp']*0.95

forecast.loc[forecast['main_sector']=="Jewish",'pop_emp_employed']=forecast['pop_emp']*0.96

arab_sector=['arabs_behined_seperation_wall','Arab']

forecast.loc[forecast['main_sector'].isin(arab_sector),'pop_emp_employed']=forecast['pop_emp']*0.98


# In[39]:


#### הוספת תלמידי ישיבה  למשקי הבית, אוכלוסיה ותפלגות גילים
forecast['hh']=forecast['hh']+forecast['student_yeshiva_and_kollim']

forecast['pop']=forecast['pop']+forecast['student_yeshiva_and_kollim']

forecast['pop_15']=forecast['pop_15']+forecast['student_yeshiva_and_kollim']*0.7

forecast['pop_20']=forecast['pop_20']+forecast['student_yeshiva_and_kollim']*0.3


# Add District

# In[40]:


forecast['DISTRICT'] = 999
forecast.loc[(forecast['main_sector']=='arabs_behined_seperation_wall'),'DISTRICT']=1
forecast.loc[(forecast['main_sector']=='Arab'),'DISTRICT']=1
forecast.loc[(forecast['main_sector'] == 'Jewish') & (forecast['in_jerusal'] == 'no') & (forecast['jeru_metro'] == 1), 'DISTRICT'] = 5
forecast.loc[(forecast['main_sector'] == 'U_Orthodox') & (forecast['in_jerusal'] == 'no') & (forecast['jeru_metro'] == 1), 'DISTRICT'] = 6
forecast.loc[(forecast['main_sector'] == 'Jewish') & (forecast['in_jerusal'] == 'yes'), 'DISTRICT'] = 3
forecast.loc[(forecast['main_sector'] == 'U_Orthodox') & (forecast['in_jerusal'] == 'yes'), 'DISTRICT'] = 2
forecast.loc[(forecast['pop']==0),'DISTRICT']=999


# In[41]:


forecast.loc[forecast['PUMA']==0,'PUMA']=999
forecast.loc[forecast['pop']==0,'PUMA']=999
forecast.loc[forecast['main_sector']=='Palestinian','PUMA']=999
forecast.loc[forecast['jeru_metro']==0,'PUMA']=999


# ### ייצוא תוצאות
# 

# In[42]:


col = [
        'Taz_num', 
        'Name_hebre',
        'Muni_Eng', 
        'main_sector', 
        'classification_name', 
        'aprt_20', 
        'add_aprt', 
        'aprt', 
        'hh_size', 
        'pop_without_dorms_yeshiva', 
        'pop_emp_employed', 
        'student_20', 
        'student', 
        'uni_students_20', 
        'add_uni_students', 
        'uni_students', 
        'student_dorms_20', 
        'add_uni_dorms', 
        'student_dorms', 
        'student_yeshiva_and_kollim', 
        'add_old_age_home', 
        'emp_from_student', 
        'emp_from_uni_student', 
        'emp_from_Yeshiva_student', 
        'emp_Education', 
        'emp_okev', 
        'add_emp_Business', 
        'add_emp_Commerce', 
        'add_emp_Industry', 
        'add_emp_Public', 
        'add_emp_Tourism', 
        'total_emp'
    ]

save_excel_path = r'{}\For_approval\{}_forecast_{}_for_approval.xlsx'.format(client_data_folder_location, file_date, forecast_version)

forecast[col].to_excel(save_excel_path, index=False)




# In[43]:


BaseProjections2040 = pd.read_csv(r'{}\background_files\BaseProjections2040_241029_jtmt.csv'.format(cwd))
puma2040 = pd.read_csv(r'{}\background_files\puma2040_fixed.csv'.format(cwd))


BaseProjections2030 = pd.read_csv(r'{}\background_files\BaseProjections2030_241029_jtmt.csv'.format(cwd))
puma2030 = pd.read_csv(r'{}\background_files\puma2030_fixed.csv'.format(cwd))

BaseProjections2050 = pd.read_csv(r'{}\background_files\BaseProjections2050_241029_jtmt.csv'.format(cwd))
puma2050 = pd.read_csv(r'{}\background_files\puma2050_fixed.csv'.format(cwd))


# In[44]:


year = df_inputs_outputs['location'][6]

if year == 2040:
    base_proj = BaseProjections2040
    puma = puma2040
elif year == 2030:
    base_proj = BaseProjections2030
    puma = puma2030
elif year == 2050:
    base_proj = BaseProjections2050
    puma = puma2050
else:
    raise ValueError("Year must be 2030 or 2040 or 2050.")

# עדכון שם הקובץ לשמירה
save_excel_path = r'{}\{}_puma{}_V4ֹ_{}.csv'.format(client_data_folder_location, file_date, year, forecast_version)

forecast.loc[forecast['Taz_num'] < 7001, 'AGG_TAZ'] = forecast['Taz_num'] // 100
forecast.loc[forecast['Taz_num'] >= 7001, 'AGG_TAZ'] = forecast['Taz_num'] // 10

forecast.rename(columns={'Taz_num': 'TAZ'}, inplace=True)




# הפעלת הפונקציה עם הסט הנבחר
delete_and_add_by_TAZ(forecast, puma).to_csv(save_excel_path, index=False)


# In[45]:


forecast_col =[
         'TAZ', 
         'Muni_Eng',
         'yosh', 
         'in_jerusalem_metropolin', 
         'jerusalem_city', 
         'main_sector', 
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
         'uni_students',
         'student_yeshiva_and_kollim', 
         'pop_emp_employed', 
         'slope', 
         'urban'
      ] 

format_needed_col = [
      'TAZ', 
      'Muni_Eng',
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
      'slope', 
      'urban'
      ]



forecast_for_model = forecast[forecast_col]
forecast_for_model.columns = format_needed_col

# עדכון שם הקובץ לשמירה עבור base projections
save_excel_path = r'{}\{}_BaseProjections{}_V4_{}.csv'.format(client_data_folder_location, file_date, year, forecast_version)
delete_and_add_by_TAZ(forecast_for_model, base_proj).to_csv(save_excel_path, index=False)

