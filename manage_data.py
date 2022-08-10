import json
import requests
from time import sleep
from tqdm import tqdm
import os
import pandas as pd

def download_jsons(destination : str, start_date : int, end_date : int, type : int):
    
    '''this function acces the UN comtrade
       dataset through the specific API and
       download the total export data for each
       country for the selected date. all the 
       files will be saved in the destination 
       folder'''
    


    if not os.path.isdir(destination):
        os.mkdir(destination)


    #create the progress bar
    with tqdm(total = (end_date - start_date +1), desc = 'downloading the data') as pbar:
        
        #get the cumulative amount of export/import
        #for each date
        for year in range(start_date, end_date+1):
            
            query = requests.get(f'https://comtrade.un.org/api/get?r=all&ps={year}&p=0&rg={type}&max=100000&type=S&freq=A')
            
            #save all the data as a JSON file
            with open(f'{destination}\data_{year}.json', 'w') as f:
                json.dump(json.loads(query.text), f, indent = 2)
            
            #wait 1 second before a new request
            #to avoid API limit of request per second
            sleep(1)
            
            pbar.update(1)



def create_df (folder : str):

    '''this function acces the folder passed
       as argument and convert the all files
       contained in it in a single data frame'''

    #get the list of files contained in the folder
    file_list = os.listdir(folder)

    #get category list
    with open('category_hash_map.json') as file:
        cat_list = json.load(file)['results']

    #take only the parent classes
    cat_dictionary = {}
    for i in cat_list:
        cat_dictionary[i['id']] = {
            'category' : i['text'].split(' ')[0],
            'description' : ' '.join(i['text'].split(' ')[1:]),
            'parent' : i['parent']
        }
    
    #save the category hash map
    with open('cat_dictionary.json', 'w') as f:
        json.dump(cat_dictionary, f, indent=3)

    parent_cat_list = []
    for i in cat_dictionary:
        if cat_dictionary[i]['parent'] == '200' or cat_dictionary[i]['parent'] == '999':
            parent_cat_list.append(i)

    #initialize the daset
    df = pd.DataFrame(columns=['country', 'year'] + [i for i in parent_cat_list])

    #create the progress bar
    with tqdm(total=len(file_list), desc= 'creating the dataframe') as pbar:
        #for each file concatenate the data for each 
        #country to the dataframe
        for file in file_list:
            
            with open(f'{folder}\{file}','r') as f:
                df_file = json.load(f)['dataset']

            try:
                pbar.set_description(f'processing year: {df_file[0]["yr"]}')
            except:
                pbar.set_description('empty query')
                
            countries_list = [i['rtTitle'] for i in df_file]

            df_dictionary = {}
            for country in countries_list:

                    df_dictionary[country] = {
                        'country' : country,
                        'year' : df_file[0]['yr'],
                    }

                    for p_calss in parent_cat_list:
                        df_dictionary[country][p_calss] = 0

            for obs in df_file:
                obs_parent = cat_dictionary[obs["cmdCode"]]["parent"]
                df_dictionary[obs["rtTitle"]][obs_parent] += obs['TradeValue']
            
            for i in df_dictionary:
                country_dictionary = pd.DataFrame(df_dictionary[i], index = [0])
                df = pd.concat([df, country_dictionary], ignore_index= True)

            pbar.update(1)

    #sort the dataset values according to
    #contry name and year
    df.sort_values(['country', 'year'], inplace = True, ignore_index = True)

    #return the dataframe and the hash map containing all the class desctriptions
    return df, cat_dictionary


