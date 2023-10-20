import pandas as pd

def team_rank(year, new):
    # get html with playoff data
    dfs = pd.read_html(f'https://www.basketball-reference.com/playoffs/NBA_{year}.html')
    
    df = dfs[20]  # the third table in the page and remove the last row 
    df.columns = df.columns.droplevel() # remove outer column index
    
    # isolate playoff win/loss and team name
    if year==2023:
        df['Team']=df['Tm']
        df = df.loc[:,['Team','W','L']]
    else:
        df = df.loc[:,['Tm','W','L']]
        df['Team']=df['Tm']
        df = df.drop('Tm',axis=1)
        df.drop(16,inplace=True)
    
    # assign number to round finished
    # 5 Champions
    # 4 Lost in finals
    # 3 Lost in Conference Finals
    # 2 Lost in Second Round
    # 1 Lost in First Round
    # -1 Missed Playoffs
    if year>=2003:
        df["Round Finished"] = df.apply(lambda row: 5 if row["W"] == 16 else
                                 4 if row["W"] >= 12 else
                                 3 if 8 <= row["W"] < 12 else
                                 2 if 4 <= row["W"] < 8 else
                                 1 if row["W"] < 4 and row["L"]>0 else
                                 -1, axis=1)
    else:
        df["Round Finished"] = df.apply(lambda row: 5 if row["W"] == 15 else
                                 4 if row["W"] >= 11 else
                                 3 if 7 <= row["W"] < 11 else
                                 2 if 3 <= row["W"] < 7 else
                                 1 if row["W"] < 3 and row["L"]>0 else
                                 -1, axis=1)
    # drop win/loss
    df = df.drop(['W','L'],axis=1)
    # change team names if applicable
    df['Team'] = df['Team'].replace({'New Orleans/Oklahoma City Hornets': 'New Orleans Pelicans',
                'Vancouver Grizzlies': 'Memphis Grizzlies',
                'New Jersey Nets': 'Brooklyn Nets',
                'Seattle SuperSonics': 'Oklahoma City Thunder',
                'New Orleans Hornets': 'New Orleans Pelicans',
                'Charlotte Bobcats': 'Charlotte Hornets',
                })
    # get teams that missed playoffs and assign -1
    east = new[0] # eastern conf
    west = new[1] # western conf
    
    # cleaning name strings
    west = west["Western Conference"].apply(lambda x: x.split("*")[0].strip()).str.split("(", expand=True)[0].str.strip()
    east = east["Eastern Conference"].apply(lambda x: x.split("*")[0].strip()).str.split("(", expand=True)[0].str.strip()
    
    # get all team names
    teams = list(pd.concat([east,west]).reset_index(drop=True))
    
    for team in teams:
        if team not in df['Team'].values: # team missed playoffs
            # assign new row with team name and -1
            df.loc[len(df)] = { 'Team': team, 'Round Finished': -1}
    
    # sort by rpund finished
    df = df.sort_values('Round Finished',ascending = False).reset_index(drop = True)
    return df

if __name__ == "__main__":
    # for all team names
    new = pd.read_html('https://www.basketball-reference.com/leagues/NBA_2023_standings.html')
    
    result = pd.DataFrame()
    for i in range(1999,2024,1): # iter through years
        df = team_rank(i, new)
        df['Year']=i
        result = pd.concat([result,df], axis=0)
    result = result[result['Team'] != 'League Average']
    result.to_csv('playoff_ranks.csv', index=False)

