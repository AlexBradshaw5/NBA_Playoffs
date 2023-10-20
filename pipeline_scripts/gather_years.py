import numpy as np
import os
import pandas as pd
import re


def list_dir(path):
    # lists all public files in directory (hides files starting with '.')
    files = os.listdir(path)
    return [string for string in files if not string.startswith('.')]


def year2szn(year):
    # changes an integer year into a string for that year's season
    # example: 2022 -> '2021-22'
    return f"{str(year-1)}-{str(year)[-2:]}"


def combine_csvs(data_folder):
    ''' Group all csvs by team
        CSVs included are:
        - szn_totals.csv
        - advanced.csv
        - shooting.csv
        - per100poss.csv
        - standing.csv
        - szn_totals_against.csv'''
    dfs = []
    file_names = ['szn_totals.csv', 'szn_totals_against.csv', 'advanced.csv',
                  'shooting.csv', 'shooting_against.csv',
                  'szn_per100poss.csv', 'szn_per100poss_against.csv', 'standings.csv'
                  ]
    merge_column = 'Team'

    for subfolder in list_dir(data_folder):
        # concat data folder path with subfolder path
        folderpath = os.path.join(data_folder, subfolder)
        if os.path.isdir(folderpath):  # check if directory
            # concat subfolder path with csv path
            csv_path = os.path.join(folderpath, file_names[0])
            # Check if csv file exists in the current subfolder
            if os.path.exists(csv_path):
                # Read the CSV file into a pandas DataFrame, use as base file
                merged_df = pd.read_csv(csv_path)

                # remove any asterisks from team names
                merged_df[merge_column] = [
                    x.strip('*') for x in merged_df[merge_column]]

                # loop through rest of files
                # skips original file, only looks at files in file_names list
                for file_name in file_names[1:]:
                    # Read the current file
                    current_csv_path = os.path.join(folderpath, file_name)
                    if os.path.exists(current_csv_path):
                        # read CSV into pandas DataFrame
                        current_df = pd.read_csv(current_csv_path)
                        # if dataframe has Team as an entry in first row
                        if 'Team' in current_df.iloc[0].values:
                            # then it's a row of column names so assign
                            current_df.columns = current_df.iloc[0]
                            # drop original first row of cols
                            current_df.drop(current_df.index[0], inplace=True)
                        # Merge the current DataFrame with the merged DataFrame
                        if (subfolder == '2022-23') & (file_name == 'standings.csv'):  # weird edge case
                            # only this year each team name for example is Warriors&edgh
                            current_df[merge_column] = [x[:-5]
                                                        for x in current_df[merge_column]]
                        # stripping any asterisks from team names
                        current_df[merge_column] = [
                            x.strip('*') for x in current_df[merge_column]]
                        merged_df = pd.merge(merged_df, current_df, on=merge_column, how='outer', suffixes=(
                            '', '_'+file_name[:-4]))
                # all files from year in one dataframe now

                # add a new column with the year
                merged_df['Year'] = subfolder
                # remove unnamed/fake index column
                merged_df = merged_df.drop(merged_df.columns[0], axis=1)
                
                # Remove NAN columns
                merged_df = merged_df.loc[:, merged_df.columns.notna()]
                #merged_df = merged_df.drop(
                 #   merged_df.columns[merged_df.columns.str.contains('^Unnamed:')], axis=1)
                dupes = np.where([[merged_df.columns.duplicated()]])[2]
                i=1
                while len(dupes)>0:
                    listed = np.array(merged_df.columns)
                    listed[dupes] = merged_df.columns[dupes]+f'_{i}'
                    i+=1
                    merged_df.columns = listed
                    dupes = np.where([[merged_df.columns.duplicated()]])[2]
                merged_df = merged_df.reset_index(drop=True, inplace=False)
                
                
                # Append the modified DataFrame to the list
                dfs.append(merged_df)

    # Concatenate all the DataFrames in the list
    concatenated_df = pd.concat(dfs, ignore_index=True)
    concatenated_df = concatenated_df.sort_values(
        ['Year', 'Rk']).reset_index(drop=True)
    concatenated_df.to_csv('./yearly_stats.csv')
    return concatenated_df

if __name__ == "__main__":
    combine_csvs('./data')
