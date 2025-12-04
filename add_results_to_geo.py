#!/usr/bin/env python
# coding: utf-8

# ## הגדרות ומקדים

# ### ספריות

# In[22]:


import os
import sys
import pandas as pd
import geopandas as gpd
import fiona
import folium
import branca.colormap as cm


# In[2]:


pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', lambda x: '%.3f' % x)


# In[20]:


col=['Taz_num','pop_without_dorms_yeshiva']


# ### העלאת משתנים להרצת הקוד

# In[3]:


cwd = os.getcwd()

create_forecast_basic_folder_path = os.path.dirname(cwd)

sys.path.append(create_forecast_basic_folder_path)


# In[5]:


from global_functions import  up_load_shp, up_load_df


# ## פונקציות

# In[6]:


def add_col_comper(df,col,new,old):
    for c in col:
        df['{}_delta_{}_{}'.format(c,new,old)]=df['{}_{}'.format(c,new)]-df['{}_{}'.format(c,old)]
        df['{}_pre_{}_{}'.format(c,new,old)]=df['{}_{}'.format(c,new)]/df['{}_{}'.format(c,old)]
    return df



# ## העלת שכבות רלוונטים

# In[8]:


max_max=pd.read_excel(r"W:\Projects\תכניות מרחביות\141_רמות\קבצי עבודה\תחזיות_דמוגרפיות\For_approval\250326_forecast_2040_ramot_max_max_for_approval.xlsx")


# In[9]:


max=pd.read_excel(r"W:\Projects\תכניות מרחביות\141_רמות\קבצי עבודה\תחזיות_דמוגרפיות\For_approval\250326_forecast_2040_ramot_max_for_approval.xlsx")


# In[10]:


real=pd.read_excel(r"W:\Projects\תכניות מרחביות\141_רמות\קבצי עבודה\תחזיות_דמוגרפיות\For_approval\241216_forecast_2040_ramot_for_approval.xlsx")


# In[ ]:


taz=up_load_shp(r"W:\Projects\תכניות מרחביות\141_רמות\קבצי עבודה\תחזיות_דמוגרפיות\For_approval\241216_taz_for_approval.shp")


# In[15]:


col=['Taz_num','pop_without_dorms_yeshiva']


# In[17]:


joined=taz.merge(real[col],on='Taz_num',suffixes=('','_real')).merge(max[col],on='Taz_num',suffixes=('','_max')).merge(max_max[col],on='Taz_num',suffixes=('','_max^2'))


# In[23]:


list(joined)


# In[25]:


# המרה לרשת WGS 84 (EPSG:4326)
joined = joined.to_crs(epsg=4326)


# In[28]:


# רשימת העמודות שמהן נוצרים השכבות
columns = ["pop_without_dorms_yeshiva", "pop_without_dorms_yeshiva_max", "pop_without_dorms_yeshiva_max^2"]

# חישוב הטווח עבור כל הנתונים
vmin = joined[columns].min().min()
vmax = joined[columns].max().max()

# יצירת סקאלת צבעים אחידה
colormap = cm.LinearColormap(colors=["blue", "yellow", "red"], vmin=vmin, vmax=vmax)

# יצירת מפה
m = folium.Map(zoom_start=10)  # נתחיל בזום סביר ונעדכן בהמשך
m.fit_bounds([[joined.total_bounds[1], joined.total_bounds[0]],  # נקודה דרום-מערבית
              [joined.total_bounds[3], joined.total_bounds[2]]]) # נקודה צפון-מזרחית

# יצירת שכבות עבור כל עמודה
layers = []
for column in columns:
    fg = folium.FeatureGroup(name=column)

    for _, row in joined.iterrows():
        value = row[column]  # הערך המקורי

        # בדיקה אם הערך חסר (NaN)
        if pd.notna(value):
            formatted_value = f"{value:,.0f}"  # עיגול והוספת פסיקים
            color = colormap(value)  
        else:
            formatted_value = "N/A"
            color = "#CCCCCC"  # צבע ברירת מחדל לערכים חסרים

        folium.GeoJson(
            row["geometry"],
            style_function=lambda feature, color=color: {
                "fillColor": color, "color": "black", "weight": 1, "fillOpacity": 0.7
            },
            tooltip=f"{column}: {formatted_value}"  # הצגת הערך בפורמט מעוגל
        ).add_to(fg)

    fg.add_to(m)
    layers.append(fg)


# הוספת מקרא ו- LayerControl
colormap.caption = "Scale of values"
colormap.add_to(m)
folium.LayerControl().add_to(m)

# שמירת המפה ל-HTML
m.save("map.html")

