import os
import pandas as pd
import requests
import numpy as np

def find_year(year: int) -> bool:
    # searches the data folder for specified year
    for file in os.listdir('./data'):
        if file.startswith(year2szn(year)): # must check for season formatted year
            return True
    return False


def year2szn(year: int) -> str:
    # changes an integer year into a string for that year's season
    # example: 2022 -> 2021-22'
    return f"{str(year-1)}-{str(year)[-2:]}"


def write_data(dfs: list, names: list, year: int) -> None:
    # Input: A list of DataFrames, a list of names, and a integer year
    # Function: Writes each dataframe to a csv with corresponding name for specified year
    
    dir_str = f'data/{year2szn(year)}/' # define directory string
    
    os.mkdir(dir_str) # create directory
    
    for i in range(len(dfs)):
        dfs[i].to_csv(dir_str+names[i]+'.csv') # concats year, name, and .csv as string


def html2csv(html_content, year: int):
    dfs = pd.read_html(html_content) # changes html file into dataframes
    
    # defines names for tables
    names = ['standings', 'per_game', 'per_game_against',
             'szn_totals', 'szn_totals_against',
             'szn_per100poss', 'szn_per100poss_against',
             'advanced', 'shooting', 'shooting_against']
    # 1971 separates east and west into separate tables
    if(year<=1970):
        first = dfs[0] # grabs first table, typically standings
        # finds western conference teams
        west_index = np.where(first['Team']=='Western Division')[0][0] 
        first.loc[:west_index, 'Conference'] = 'East' # Assigns everything under west conf as East
        first.loc[:west_index, 'Seed'] = range(west_index+1) # Assigns seed numbers to eastern teams
        first.loc[west_index:, 'Seed'] = range(len(first)-west_index) # assigns seed numbers to western teams
        first.loc[west_index:, 'Conference'] = 'West' # Assigns western teams respective conferences
        
        # remove random non-teams
        first = first[(first['Team']!='Eastern Division') & (first['Team']!='Western Division')]
        # call write_data function
        write_data([first]+dfs[1:], names[:-5]+['advanced'], year)
        return
    
    if(year < 2016): # 2016 introduced league wide table in addition to each conference
        # remove division names
        east = dfs[0][(dfs[0]['W'] != 'Atlantic Division') &
                      (dfs[0]['W'] != 'Central Division')].copy() 
        west = dfs[1][(dfs[1]['W'] != 'Midwest Division') &
                      (dfs[1]['W'] != 'Pacific Division')].copy()
        
        frames = dfs[2:] # get rest of dataframes
        
        # weird edge case managing
        if((year < 2000) & (year > 1996)):
            names = names[:-2]
            frames = frames[:-2]
        if(year <= 1973):
            names = names[:-3]+['advanced']
    else: # 2016-present
        east = dfs[0]
        west = dfs[1]
        frames = dfs[4:]
    # assigning conference and seeds
    east['Conference'] = 'East'
    west['Conference'] = 'West'
    east['Seed'] = range(1, len(east)+1)
    west['Seed'] = range(1, len(west)+1)
    # renaming conference to just team name
    west.rename(columns={'Western Conference': 'Team'}, inplace=True)
    east.rename(columns={'Eastern Conference': 'Team'}, inplace=True)
    # combine the east and west dataframes sorted by Number of Wins followed by conference seed number
    combined = pd.concat([east, west]).sort_values(by=['W', 'Seed'],
                                                   ascending=[False, True], ignore_index=True)
    # create list of dataframes for usage
    final_dfs = [combined]+frames
    
    #turn them into csv files
    write_data(final_dfs, names, year)


def download_schedule_table(): # MAIN
    # if imperfect airflow or weird pipeline errors, this for loop finds the year not yet registered
    for year in range(2023, 1950, -1):
        if(find_year(year) == False):
            break
        
    url = f"https://www.basketball-reference.com/leagues/NBA_{year}.html"
    response = requests.get(url) # grab html from url
    
    if response.status_code == 200: # found table
        html2csv(response.content, year) # call helper
        download_schedule_table() # recursive
    elif response.status_code == 429: # soft banned
        print('Hit request limit')
    else:
        print(f"{year} data does not exist or has been downloaded.")


if __name__ == "__main__":
    download_schedule_table()
    print('All done')
''' Side Notes:
<1972-73 no per 100 poss stats
2001> introduced accurate shooting stts
2015-16> conference'''






