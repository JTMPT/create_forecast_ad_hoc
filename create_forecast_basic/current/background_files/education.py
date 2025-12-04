#!/usr/bin/env python
# coding: utf-8

# ## סדר פעולות:
# 
# העלאת טבלאות
# 
# סידור שמות השדות באנגלית
# טבלת מוסדות אחודה- ID, src
# בקרה על כפילויות מאותו מקור
# סימון בתי ספר עם הפרשים גדולים בין המקורות
# מחיקת רשומות ממקור לא מועדף
# בניית מקדם מספר כיתות מתוך תלמידים.
# החלת המקדם על כל בתי הספר, עיגול מספר התלמידים
# 
# מיקום
# דאטה גוב
# ירושלים- עירייה
# בית שמש- עירייה בעזרת סקריפט גאוקודינג
# גוגל בעזרת כלים אוטומטיים
# יצירת רשימת מוסדות ללא מיקום
# חיבור נתונים בעזרת merge
# ייצוא לעיגון ידני
# העלאת שכבת מוסדות מעיגון ידני
# חיבור שכבת העיגון הידני לשאר המוסדות
# הוספת שם השכונה
# 
# בונוס- תעסוקה
# יצירת מקדם מועסקים לפי נתוני למס מעיבוד מיוחד
# החלת המקדם, עיגול מספר המועסקים
# 
# ייצוא
# שכבת נקודות
# שכבת אזורי תנועה
# סטטיסטיקות מעניינות
# טבלת מוסדות עם פער גדול בנתונים

# ## ייבוא

# In[283]:


import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Point
import os
import math
import warnings
from geopy.geocoders import Nominatim
import pyproj

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', lambda x: '%.2f' % x)




# In[284]:


out_shp = r'W:\Data\GIS\Data Collection\חנוך\education.shp'


# ## העלאת טבלאות 

# In[285]:


#removing spaces from name of columns
def remove_spaces_in_columns(df):
    for i in df.columns:
        i = str(i)
        if ' ' in i:
            df.rename(columns = {i:i.replace(' ','_')}, inplace = True)
        if "'" in i:
            df.rename(columns = {i:i.replace("'",'')}, inplace = True)
        if '"' in i:
            df.rename(columns = {i:i.replace('"','')}, inplace = True)

    return df


# In[286]:


#בתי ספר וגנים מעיריית בית שמש
BShemesh = remove_spaces_in_columns(pd.read_excel(
    r'\\file-srv\Jtmt\projections_team\GIS_backround\INFO\עיריית בית שמש\חינוך\מצבת מוסדות חינוך תשפג משרדי.xlsx')).dropna(how='all')


# In[287]:


#בתי ספר וגנים מעיריית ירושלים
JLM = remove_spaces_in_columns(pd.read_excel(
    r'\\file-srv\Jtmt\projections_team\GIS_backround\INFO\עיריית ירושלים\חינוך\מוסדות בירושלים 2020.xlsx')).dropna(how='all')


# In[288]:


GKgarden=remove_spaces_in_columns(pd.read_excel(
    r'\\file-srv\Jtmt\projections_team\GIS_backround\INFO\משרד החינוך\מוסדות\kgarden_2023.xlsx')).dropna(how='all')


# In[289]:


#בתי ספר ממשרד החינוך בכל הארץ
Gschool=remove_spaces_in_columns(pd.read_excel(
    r'\\file-srv\Jtmt\projections_team\GIS_backround\INFO\משרד החינוך\מוסדות\schools_2023.xlsx')).dropna(how='all')


# In[290]:


#יישובים בשטח צתאל שם וקוד יישוב
JTMT_setls=remove_spaces_in_columns(pd.read_excel(
    r'//file-srv/Jtmt/projections_team/GIS_backround/INFO/צתאל/210615_גבול_אחריות_צתאל/210615_מקוצר_רשימת_יישובים_באחריות_צתאל.xlsx')).dropna(how='all')


# In[291]:


#קאורדינטות של מוסדות חינוך בכל הארץ ממשרד החינוך
GXY=remove_spaces_in_columns(pd.read_excel(
    r'\\file-srv\Jtmt\projections_team\GIS_backround\INFO\משרד החינוך\מוסדות\moe_mosdot_coordinates_2022.xlsx')).dropna(how='all')


# In[292]:


#מספרי מוסדות, כיתות, ותלמידים בכל רשות מתוך קובץ יישובים של למ"ס
CBS_setl = remove_spaces_in_columns(pd.read_excel(
    r'\\file-srv\Jtmt\projections_team\GIS_backround\INFO\למ_ס\חינוך\CBS_EDU_yishuv_2021.xlsx')).dropna(how='all')


# ### not in use yet

# In[293]:


EastJlm = remove_spaces_in_columns(pd.read_excel(
    r'\\file-srv\Jtmt\projections_team\GIS_backround\INFO\מכון ירושלים\מוסדות_חינוך_פרטיים_מזרח_העיר\_חינוך_פרטי_2021.xlsx')).dropna(how='all')


# In[294]:


dormsJLM = remove_spaces_in_columns(pd.read_excel(
    r'\\file-srv\Jtmt\projections_team\GIS_backround\INFO\עיריית ירושלים\חינוך\פנימיות מוכרות עיריית ירושלים.xlsx')).dropna(how='all')


# In[ ]:





# ## שדות

# ID
# address
# sector
# kgarden_stu
# ele_stu
# mid_stu
# high_stu
# kgarden_class
# ele_class
# mid_class
# high_class
# 'x'
# 'y'
# src

# #### פונקציות

# In[295]:


def age_distribute(df):
    #ages definition
    ages = {'kgarden':[3, 4, 5],'ele':['א', 'ב', 'ג', 'ד','ה','ו'],'mid':['ז', 'ח', 'ט'], 'high':['י', 'יא', 'יב', 'יג', 'יד']}
    ages_number ={'גן':1,'א': 1,'ב': 2,'ג': 3,'ד': 4,'ה': 5,'ו': 6,'ז': 7,
        'ח': 8,'ט': 9,'יד': 12.5,'יג': 12.3,'יב': 12,'יא': 11,'י': 10}
    for i in ages_number:
        df.loc[df['bottom_age']==i,'b_age_num']=ages_number[i]
        df.loc[df['top_age']==i,'t_age_num']=ages_number[i]

    ##calculate new columns

    #kgarden student
    df.loc[df['top_age'].isin(ages['kgarden']),'kgarden_stu'] = df['students_total']
    if not len(df.loc[df['bottom_age'].isin(ages['kgarden']) & ~df['top_age'].isin(ages['kgarden'])])==0:
        print('need to write code for situation of kgarden and school in the same institution')

    #high school fixing where it's 0. 
    #assumes that every age has equal number of student (exept of 13 and 14 class which 0.3 and 0.2 of the other classes)

    #all ages are high school
    df.loc[(df['b_age_num']>9) & (df['high_stu']==0),'high_stu'] =df['students_total'].round()

    #ages are middle and high school and there is a middle school students
    df.loc[(df['t_age_num']>9) &(df['b_age_num']>6) & (df['high_stu']==0)& (df['mid_stu']!=0),'high_stu'] =\
    (df['students_total']- df['mid_stu'])

    #ages are elementary, middle and high school and there is a middle school ages
    df.loc[(df['t_age_num']>9) &(df['b_age_num']<7) & (df['high_stu']==0)& (df['mid_stu']!=0),'high_stu'] =\
    ((df['students_total']- df['mid_stu'])*((df['t_age_num']-9)/(df['t_age_num']-df['b_age_num']-2))).round()

    #ages are middle and high school or diverse all school ages
    df.loc[(df['t_age_num']>9) &(df['b_age_num']<10) & (df['high_stu']==0)& (df['mid_stu']==0),'high_stu'] =\
    (df['students_total']*((df['t_age_num']-9)/(df['t_age_num']-df['b_age_num']+1))).round()



    #middle school fix where it's 0. 
    #assumes that every age has equal number of student (exept of 13 and 14 class which 0.3 and 0.2 of the other classes)

    #all ages are middle school
    df.loc[(df['t_age_num']<10) & (df['b_age_num']>6) & (df['mid_stu']==0),'mid_stu'] =df['students_total'].round()

    #ages are middle and high school
    df.loc[(df['b_age_num']<10) &(df['b_age_num']>6) & (df['mid_stu']==0),'mid_stu'] =\
    (df['students_total']- df['high_stu'])

    #ages are middle and elementary school
    df.loc[(df['t_age_num']>6) &(df['t_age_num']<10) & (df['mid_stu']==0),'mid_stu'] =\
    df['students_total']*((df['t_age_num']-6)/(df['t_age_num']-df['b_age_num']+1)).round()

    #diverse all school ages
    df.loc[(df['t_age_num']>6) &(df['b_age_num']<7) & (df['mid_stu']==0),'mid_stu'] =\
    df['students_total']*(3/(df['t_age_num']-df['b_age_num']+1)).round()

    #calculate elementary student
    df.loc[(df['b_age_num']<7),'ele_stu']=df['students_total']-df['high_stu']-df['mid_stu'].round()

    #checking student numbers
    if len(df.loc[df['students_total']!=df['high_stu']+df['mid_stu']+df['ele_stu']+df['kgarden_stu']]):
        warnings.warn(f"Warning: there is a problem with age distribution. total studens is different fof sum of them")

    return df


# #### עיריית בית שמש

# In[296]:


#change hebrew
BShemesh.columns = ['sector', 'name', 'ID', 'neighbourhood', 'address', 'b2', 'a1',
       'a5', 'a8', 'a7', 'a6', 'a4', 'a3',
       'a9', 'a11', 'a10', 'Kgarden4', 'Kgarden5',
       'SpeKgarden', 'Kgarden_total', '1_1', '1_2', '1_3', '1_4', '1_5', '1_', '2_1', '2_2', '2_3', '2_4', '2_', '3_1', '3_2', '3_3', '3_4', '3_', '4_1', '4_2', '4_3', '4_4', '4_', '5_1', '5_2', '5_3', '5_4', '5_', '6_1', '6_2', '6_3', '6_4', '6_', 'a20', '7_1', '7_2', '7_3', '7_4', '7_', '8_1', '8_2', '8_3', '8_4', '8_', '', '9_1', '9_2', '9_3', '9_', '10_1', '10_2', '10_3', '10_', '11_1', '11_2', '11_3', '11_', '12_1', '12_2', '12_3', '12_', 'a22', 'a21']

#calculate columns
#student number
BShemesh['kgarden_stu'] = BShemesh['Kgarden_total'] 
BShemesh['ele_stu'] = BShemesh[['1_1', '1_2', '1_3', '1_4', '1_5',
                            '2_1', '2_2', '2_3', '2_4',
                            '3_1', '3_2', '3_3', '3_4',
                            '4_1', '4_2', '4_3', '4_4',
                            '5_1', '5_2', '5_3', '5_4',
                            '6_1', '6_2', '6_3', '6_4',
                            '1_', '2_', '3_', '4_','5_', '6_']].sum(axis=1)

BShemesh['mid_stu'] = BShemesh[['6_1', '6_2', '6_3', '6_4',
                            '7_1', '7_2', '7_3', '7_4',
                            '8_1', '8_2', '8_3', '8_4',
                            '9_1', '9_2', '9_3',
                            '7_', '8_','9_']].sum(axis=1)
BShemesh['high_stu'] = BShemesh[['10_1', '10_2', '10_3',
                            '11_1', '11_2', '11_3',
                            '12_1', '12_2', '12_3',
                            '10_', '11_', '12_']].sum(axis=1)

BShemesh['kgarden_class'] = BShemesh[['Kgarden4', 'Kgarden5']].count(axis=1)
#classes
BShemesh['ele_class'] = BShemesh[['1_1', '1_2', '1_3', '1_4', '1_5',
                            '2_1', '2_2', '2_3', '2_4',
                            '3_1', '3_2', '3_3', '3_4',
                            '4_1', '4_2', '4_3', '4_4',
                            '5_1', '5_2', '5_3', '5_4',
                            '6_1', '6_2', '6_3', '6_4',
                            '1_', '2_', '3_', '4_','5_', '6_']].count(axis=1)

BShemesh['mid_class'] = BShemesh[['6_1', '6_2', '6_3', '6_4',
                            '7_1', '7_2', '7_3', '7_4',
                            '8_1', '8_2', '8_3', '8_4',
                            '9_1', '9_2', '9_3',
                            '7_', '8_','9_']].count(axis=1)
BShemesh['high_class'] = BShemesh[['10_1', '10_2', '10_3',
                            '11_1', '11_2', '11_3',
                            '12_1', '12_2', '12_3',
                            '10_', '11_', '12_']].count(axis=1)
#sector
BShemesh.loc[BShemesh['sector']=='חרדי','sector'] = 2
BShemesh.loc[BShemesh['sector']=='ממ"ח','sector'] = 2
BShemesh.loc[BShemesh['sector']=='ממ"ד','sector'] = 3
BShemesh.loc[BShemesh['sector']=='מ"מ','sector'] = 3
BShemesh.loc[BShemesh['sector']=='עירוני','sector'] = 3

#adding another columns
BShemesh['settlement'] = 'בית שמש'
BShemesh[['x', 'y']] = 0

#src
BShemesh['src'] = 'Beit Shemesh muni'

#erase Irelevant columns
BShemesh = BShemesh[['ID','name','sector','address','settlement','x', 'y','kgarden_stu','ele_stu','mid_stu','high_stu',
                     'kgarden_class','ele_class','mid_class','high_class','src']]


# #### עיריית ירושלים

# In[297]:


#change hebrew
JLM.columns = ['muni_ID', 'ID', 'name', 'sector', 'פיקוח', 'שלב_חינוך',
       'is_speciel', 'מעמד_משפטי', 'bottom_age', 'top_age', 'classes_total',
       'mid_stu', 'high_stu', 'students_total',
       'קוד_אזור_סטיסטי', 'תאור_אזור_סטטיסטי', 'x', 'y',
       'Unnamed:_18', 'Unnamed:_19'] 

#adding new columns
JLM['settlement'] = 'ירושלים'
JLM[['address','kgarden_stu','ele_stu','kgarden_class', 'ele_class', 'mid_class', 'high_class']] = 0
JLM[['kgarden_stu','high_stu','mid_stu']] = JLM[['kgarden_stu','high_stu','mid_stu']].fillna(0)

#calculate student number
JLM = age_distribute(JLM)

#classes by age
JLM['stu_to_class'] = JLM['students_total']/JLM['classes_total']
for age in ['kgarden','ele','mid','high']:
    JLM[age+'_class'] = (JLM[age+'_stu'] / JLM['stu_to_class']).round()

average_student_to_class_in_jlm = JLM['students_total'].sum()/JLM['classes_total'].sum()

#sector
JLM.loc[JLM['sector']=='ערבי','sector'] = 1
JLM.loc[JLM['sector']=='חרדי','sector'] = 2
JLM.loc[JLM['sector']=='כללי','sector'] = 3

#src
JLM['src'] = 'Jerusalem muni'

#erase Irelevant columns
JLM = JLM[['ID','name','sector','address','settlement','x', 'y','kgarden_stu','ele_stu','mid_stu','high_stu',
                     'kgarden_class','ele_class','mid_class','high_class','src']]


# #### משרד החינוך

# In[298]:


#change hebrew
GKgarden.columns = ['ID', 'name', 'settlement', 'address','a','phone','type','legal_status',
       'supervision_type', 'sector', 'יחידת_דיווח', 'age', 'kgarden_stu']
Gschool.columns = ['ID', 'name', 'settlement', 'address','כתובת חט"ב', 'טלפון', 'דוא"ל_מזכירות',
       'סוג_חינוך', 'legal_status','supervision_type', 'sector', 'יחידת_דיווח', 'ages', 'students_total']

#take only in JTMT settlements
setls = list(JTMT_setls['שם_יישוב'])
GKgarden = GKgarden.loc[GKgarden['settlement'].isin(setls)]

Gschool = Gschool.loc[Gschool['settlement'].isin(setls)]

#calculate columns
GKgarden[['ele_stu','mid_stu','high_stu','ele_class','mid_class','high_class','x','y']] = 0
GKgarden['kgarden_class'] = 1

Gschool[['bottom_age', 'top_age']] = Gschool['ages'].str.split(' - ',  expand=True)
Gschool['students_total'] = Gschool['students_total'].fillna(0)
Gschool[['kgarden_stu','ele_stu','mid_stu','high_stu','kgarden_class','ele_class','mid_class','high_class','x','y']] = 0

Gschool = age_distribute(Gschool)

#classes
#classes by age from the average in jerusalem
for age in ['kgarden','ele','mid','high']:
    Gschool[age+'_class'] = (Gschool[age+'_stu'] / average_student_to_class_in_jlm).apply(lambda x: math.ceil(x))

#sector
Gschool.loc[Gschool['sector']!='יהודי','sector'] = 1
Gschool.loc[Gschool['sector']=='יהודי','sector'] = 3
Gschool.loc[Gschool['supervision_type']=='חרדי','sector'] = 2

GKgarden.loc[GKgarden['sector']!='יהודי','sector'] = 1
GKgarden.loc[GKgarden['sector']=='יהודי','sector'] = 3
GKgarden.loc[GKgarden['supervision_type']=='חרדי','sector'] = 2

#src
Gschool['src'] = 'education ministry'
GKgarden['src'] = 'education ministry'

#erase Irelevant columns
Gschool = Gschool[['ID','name','sector','address','settlement','x', 'y','kgarden_stu','ele_stu','mid_stu','high_stu',
                     'kgarden_class','ele_class','mid_class','high_class','src']]
GKgarden = GKgarden[['ID','name','sector','address','settlement','x', 'y','kgarden_stu','ele_stu','mid_stu','high_stu',
                     'kgarden_class','ele_class','mid_class','high_class','src']]


# #### למס

# In[299]:


CBS_setl.columns = ['set_ID', 'settlement',
       'kgarden_stu',
       'ילדים_בגנים_של_משרד_החינוך_גיל_3_תשפ"א_2020/21',
       'ילדים_בגנים_של_משרד_החינוך_גיל_4_תשפ"א_2020/21',
       'ילדים_בגנים_של_משרד_החינוך_גיל_5_תשפ"א_2020/21',
       'ילדים_בגנים_של_משרד_החינוך_גיל_6_תשפ"א_2020/21',
       'schools',
       'ele_schools',
       'בתי_ספר_על-יסודיים_תשפ"א_2020/21',
       'mid_school', 'high_school',
       'כיתות_סה"כ_תשפ"א_2020/21', 'ele_class',
       'כיתות_בבתי_ספר_על-יסודיים_תשפ"א_2020/21',
       'mid_class',
       'high_class', 'תלמידים_סה"כ_תשפ"א_2020/21',
       'ele_stu',
       'תלמידים_בבתי_ספר_על-יסודיים_תשפ"א_2020/21',
       'mid_stu',
       'high_stu',
       'ממוצע_תלמידים_לכיתה_בבתי_ספר_יסודיים_תשפ"א_2020/21',
       'אחוז_תלמידים_נושרים_סה"כ_תשפ"א_2020/21',
       'אחוז_תלמידים_נושרים_בנים_תשפ"א_2020/21',
       'אחוז_תלמידים_נושרים_בנות_תשפ"א_2020/21',
       'אחוז_זכאים_לתעודת_בגרות_מבין_תלמידי_כיתות_יב_תשפ"א_2020/21',
       'אחוז_זכאים_לתעודת_בגרות_שעמדו_בדרישות_הסף_של_האוניברסיטאות_מבין_תלמידי_כיתות_יב_תשפ"א_2020/21',
       'השכלה_גבוהה_אחוז_בעלי_תארים_מישראל_מתוך_אוכלוסיית_בני_55-35_תשפ"ב_2021/22',
       'השכלה_גבוהה_אחוז_הנכנסים_להשכלה_גבוהה_בתוך_8_שנים_בקרב_תלמידי_יב_תשפ"ב_2021/22',
       'השכלה_גבוהה_אחוז_סטודנטים_מתוך_אוכלוסיית_בני_25-20_תשפ"ב_2021/22',
       'השכלה_גבוהה_אחוז_סטודנטים_מתוך_כלל_האוכלוסייה_תשפ"ב_2021/22',
       'עובדי_הוראה_מספר_עובדי_הוראה', 'עובדי_הוראה_ממוצע_שעות_עבודה_לשבוע',
       'עובדי_הוראה_אחוז_עובדי_הוראה_חדשים',
       'עובדי_הוראה_אחוז_שעות_היעדרות_מסך_שעות_עבודה_שנתיות',
       'עובדי_הוראה_ממוצע_שנות_ותק_מוכרות_בהוראה',
       'עובדי_הוראה_אחוז_בעלי_דרגת_שכר_תואר_שני_ומעלה',
       'עובדי_הוראה_אחוז_עובדי_הוראה_משתלמים_מכלל_עובדי_הוראה',
       'teacher_by_stu',
       'עובדי_הוראה_ממוצע_שעות_עבודה_שבועיות_לתלמיד']

CBS_setl = CBS_setl[['set_ID', 'settlement',
       'kgarden_stu',
       'schools',
       'ele_class',
       'mid_class',
       'high_class', 
       'ele_stu',
       'mid_stu',
       'high_stu']]

CBS_setl.replace('-', 0.001, inplace=True)


# ## טבלת מוסדות אחודה- ID, src

# In[300]:


rows = pd.concat([BShemesh,Gschool,GKgarden,JLM]) #JLM is 2020, the others are 2023


# In[301]:


inst = rows.groupby('ID').agg('first').reset_index()


# ## מיקום
# 

# #### datagov from education ministry

# In[302]:


inst_xy = inst.merge(GXY[['SEMEL_MOSAD','ITM_X', 'ITM_Y']],how='left',left_on = 'ID', right_on='SEMEL_MOSAD')

inst_xy.loc[inst_xy['ITM_X'].notna(),'x'] = inst_xy['ITM_X']

inst_xy.loc[inst_xy['ITM_Y'].notna(),'y'] = inst_xy['ITM_Y']

inst = inst_xy[['ID','name','sector','address','settlement','x', 'y','kgarden_stu','ele_stu','mid_stu','high_stu',
                     'kgarden_class','ele_class','mid_class','high_class','src']]


# #### OSM geocoding

# In[31]:


def OSMgeocoding(df):
    geolocator = Nominatim(user_agent="my_geocoder")
    itm = pyproj.Proj(init='epsg:2039')
    for i in df['ID']:
        location = geolocator.geocode(str(df.loc[df['ID'] == i]['f_address'])[4:-31])
        if location:
            x, y = pyproj.transform(pyproj.Proj(init='epsg:4326'), itm, location.longitude, location.latitude) #to ITM
            df.loc[df['ID']==i,'x_osm'] = x
            df.loc[df['ID']==i,'y_osm'] = y
    return df.loc[df['x_osm'].notna()]


# In[304]:


no_xy = inst.loc[(inst['x']==0) | (inst['x'].isna())][['ID','address','settlement']]
# full address
no_xy['f_address'] = no_xy['address'].astype(str).str.cat(no_xy['settlement'], sep=', ').apply(lambda x: f"{x}, ישראל")

#search on OSM
if input('take a lot of time, enter y for do it!\n')=='y':
    inst_xy_osm = OSMgeocoding(no_xy)


# In[305]:


#merge to main inst dataframe
inst_xy = inst.merge(inst_xy_osm[['ID','x_osm','y_osm']],how='left',on = 'ID')
inst_xy.loc[(inst['x']==0)| (inst['x'].isna()),'x'] = inst_xy['x_osm']
inst_xy.loc[(inst['y']==0)| (inst['y'].isna()),'y'] = inst_xy['y_osm']
inst = inst_xy[['ID','name','sector','address','settlement','x', 'y','kgarden_stu','ele_stu','mid_stu','high_stu',
                     'kgarden_class','ele_class','mid_class','high_class','src']]


# ~בית שמש- עירייה בעזרת סקריפט גאוקודינג- 89
# ~- 298 גוגל בעזרת כלים אוטומטיים
# יצירת רשימת מוסדות ללא מיקום

# ### יצירת GDF

# In[306]:


geometry = [Point(xy) for xy in zip(inst['x'], inst['y'])]


# In[307]:


inst = gpd.GeoDataFrame(inst, geometry=geometry,crs='EPSG:2039')


# ## בקרה

# ### פונקציות

# In[257]:


def compare_rows(df1, df2, ID_field, cmp_fields, threshold=0.2):
    ratio_fields = [f+'_ratio' for f in cmp_fields]

    # Merge the two DataFrames on a common index or key
    merged_df = pd.merge(df1, df2, on=ID_field, how='inner', suffixes=('_1', '_2'))
    merged_df['isdifferent'] = False
    #calculate ratio to a new column
    for c in cmp_fields:
        merged_df[c+'_ratio'] = merged_df[c+'_1'] / merged_df[c+'_2']
        merged_df.loc[abs(merged_df[c+'_ratio']-1) > threshold,'isdifferent'] = True

    return merged_df.loc[merged_df['isdifferent']]


# ### השוואה ברמת  מוסד

# #### בית שמש - משרד החינוך

# In[279]:


#fields to compare
cmp_setl = ['kgarden_stu',
       'ele_class','mid_class','high_class', 
       'ele_stu','mid_stu','high_stu']
#how much different
threshold = 0.3
dif = compare_rows(BShemesh, GKgarden,'ID',cmp_setl, threshold=threshold)
len(dif)


# In[280]:


#fields to compare
cmp_setl = ['kgarden_stu',
       'ele_class','mid_class','high_class', 
       'ele_stu','mid_stu','high_stu']
#how much different
threshold = 0.
dif = compare_rows(BShemesh, GKgarden,'ID',cmp_setl, threshold=threshold)
len(dif)


# In[281]:


#fields to compare
cmp_setl = ['kgarden_stu',
       'ele_class','mid_class','high_class', 
       'ele_stu','mid_stu','high_stu']
#how much different
threshold = 0.3
dif = compare_rows(BShemesh, Gschool,'ID',cmp_setl, threshold=threshold)
len(dif)


# In[282]:


#fields to compare
cmp_setl = ['kgarden_stu',
       'ele_class','mid_class','high_class', 
       'ele_stu','mid_stu','high_stu']
#how much different
threshold = 0
dif = compare_rows(BShemesh, GKgarden,'ID',cmp_setl, threshold=threshold)
len(dif)


# #### ירושלים- משרד החינוך

# In[273]:


#fields to compare
cmp_setl = ['kgarden_stu',
       'ele_class','mid_class','high_class', 
       'ele_stu','mid_stu','high_stu']
#how much different
threshold = 0.3
dif = compare_rows(JLM, GKgarden,'ID',cmp_setl, threshold=threshold)
len(dif)


# In[278]:


#fields to compare
cmp_setl = ['kgarden_stu',
       'ele_class','mid_class','high_class', 
       'ele_stu','mid_stu','high_stu']
#how much different
threshold = 0
dif = compare_rows(JLM, GKgarden,'ID',cmp_setl, threshold=threshold)
len(dif)


# In[276]:


#fields to compare
cmp_setl = ['kgarden_stu',
       'ele_class','mid_class','high_class', 
       'ele_stu','mid_stu','high_stu']
#how much different
threshold = 0.3
dif = compare_rows(JLM, Gschool,'ID',cmp_setl, threshold=threshold)
len(dif)


# In[277]:


#fields to compare
cmp_setl = ['kgarden_stu',
       'ele_class','mid_class','high_class', 
       'ele_stu','mid_stu','high_stu']
#how much different
threshold = 0
dif = compare_rows(JLM, Gschool,'ID',cmp_setl, threshold=threshold)
len(dif)


# ### השוואה ברמת  יישוב אל מול נתוני למס

# In[309]:


#sum by settiemnt
settlement = inst.groupby('settlement').agg({'ID':'count', 'kgarden_stu':'sum', 'ele_stu':'sum', 'mid_stu':'sum',
                                'high_stu':'sum', 'kgarden_class':'sum', 'ele_class':'sum',
                                'mid_class':'sum', 'high_class':'sum'}).reset_index()
settlement['schools'] = settlement['ID'] - settlement['kgarden_class']
settlement.replace(0, 0.001, inplace=True)

#fields to compare
cmp_setl = ['kgarden_stu','schools', #<inst_count> - <kgarden_class> 
       'ele_class','mid_class','high_class', 
       'ele_stu','mid_stu','high_stu']
#how much different
threshold = 0.3

different_settlements = compare_rows(settlement, CBS_setl,'settlement',cmp_setl, threshold=threshold)

different_settlements


# בקרה על מספר המוסדות - שלא איבדנו מוסד.
# בקרה על מספר התלמידים והכיתות הכולל
# 
# ~סימון בתי ספר עם הפרשים גדולים בין המקורות

# ## ייצוא

# In[308]:


inst.to_file(out_shp,encoding='utf-8')


# In[ ]:




