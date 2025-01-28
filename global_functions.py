import os
import fiona
import geopandas as gpd
import pandas as pd

def up_load_gdb(path, layer_name):
    path='{}'.format(path)
    layer_list=fiona.listlayers(path)
    gpd_layer=gpd.read_file(path, layer=layer_list.index(layer_name))
    return gpd_layer

def make_point(df):
    df_point=df.copy()
    df_point['centroid'] = df_point.representative_point()
    df_point=df_point.set_geometry('centroid')
    df_point=df_point.drop(columns=['geometry'],axis=1)
    return df_point

def up_load_shp(path):
    path='{}'.format(path)
    gpd_layer=gpd.read_file(path)
    return gpd_layer

def up_load_df(folder_path,file_name):
    path_df=r'{}\{}.xlsx'.format(folder_path,file_name)
    df=pd.read_excel(path_df)
    df=df.dropna(how='all')

    return df

def split_index_by_taz(index,taz,min_prec,col_name_to_split):
    index['index_area']=index.area
    
    taz['taz_area']=taz.area

    index_taz=index.overlay(taz[['Taz_num','taz_area','geometry']], keep_geom_type=False)

    index_taz['small_area']=index_taz.area

    index_taz['precent_from_big_index']=index_taz['small_area']/index_taz['index_area']
    
    index_taz['precent_from_big_taz']=index_taz['small_area']/index_taz['taz_area']

    index_taz=index_taz.loc[(index_taz['precent_from_big_index']>min_prec)|(index_taz['precent_from_big_taz']>0.9)]
    
    index_taz=index_taz[['id','Taz_num','precent_from_big_index']]

    new_big=index_taz.groupby(['id']).sum()

    index=index.set_index('id')
    index['new_big']=new_big['precent_from_big_index']

    index=pd.merge(index.reset_index(),index_taz,on='id')

    for c in col_name_to_split:
        index['{}'.format(c)]=index['{}'.format(c)]*(index['precent_from_big_index']/index['new_big'])
        
        
    return index


def delete_and_add_by_TAZ(forecast,df):
    lst_of_taz=list(forecast.TAZ)
    #מחיקה של אזורי תנועה החדשים למנוע כפילות
    df=df.loc[~(df['TAZ'].isin(lst_of_taz))]
    #הוספה של האזורי תנועה החדשים
    return pd.concat([df, forecast[list(df)]], axis=0)

def change_Muni_Heb_to_Muni_Eng(software_data_folder_location, forecast):
    muni_english = pd.read_excel(r'{}\background_files\english_names.xlsx'.format(software_data_folder_location))
    muni_heb_mapping = muni_english.set_index('Muni_Heb')

    forecast = forecast.merge(muni_heb_mapping, how='left', left_on='Muni_Heb', right_index=True)
    forecast.dropna(subset=['Muni_Heb'], inplace=True)

    return forecast

def find_files_with_pattern(folder_path, pattern):
    """
    Find files in a directory that match a certain pattern.
    
    Args:
    - directory (str): The directory path.
    - pattern (str): The pattern to search for in file names.
    
    Returns:
    - List of file paths matching the pattern.
    """
    files = []
    for root, _, filenames in os.walk(folder_path):
        for filename in filenames:
            if pattern in filename:
                files.append(os.path.join(root, filename))
    return files

def find_geographic_layers(folder_path, pattern, suffix):
    """
    מוצא קבצים בתיקייה עם תבנית מסוימת וסיומת.
    """
    return [
        os.path.join(folder_path, file) 
        for file in os.listdir(folder_path) 
        if pattern in file and file.endswith(suffix)
    ]