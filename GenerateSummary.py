# Daychyi Ku
# 8 Dec 2022
# For Google classroom virtual classes attendance processing
# Input: Google classroom meeting data files in .csv with columns=['First name','Last name', 'Email', 'Duration', 'Time joined', 'Time exited']
# Output: Summary.csv
# Remark: use 'Email' as key

# Generate summary based on the Google meet csv files.
# Place this file in the same directory of the csv files, and a Summary.csv will be generated.
# Column names are the date from on the provided csv files.
# Value 1 is given when participant attended at least half(0.5) of the total time (Time exited-Time joined), 0 otherwise. Threshold is controlled by changing variable (attended_time).
# Entry without email is deleted from the record

import os
import numpy as np
import pandas as pd
from functools import reduce


def process_df(df,filename,scale):
    #df.reindex()
    df.drop_duplicates(inplace = True)
    df.drop(columns=["Last name","Duration"],axis=1, inplace=True)
    #drop rows without email
    df.dropna(subset=['Email'], inplace=True)
    
    df["Time joined"] = pd.to_datetime(df["Time joined"])
    df["Time exited"] = pd.to_datetime(df["Time exited"])
    #df["Time_diff"] = df["Time exited"] - df["Time joined"]

    # create a colume with timedelta as total minutes (float64)
    df["Duration_min"] = (df["Time exited"] - df["Time joined"]) / pd.Timedelta(minutes=1)
    #range of time_diff
    range = np.ptp(df["Duration_min"])
    
    #assign attendance based on time stamp
    attended_time = range * scale #duration in mins
    conditions = [(df["Duration_min"] >= attended_time), (df["Duration_min"] < attended_time) ]
    values = [1,0]
    df[filename] = np.select(conditions, values)
    #print("range: ", range)
    
    df.drop(columns=["Time joined","Time exited","Duration_min"],axis=1,inplace=True)
    


#list csv files only in current directory
files = [f for f in os.listdir('.') if os.path.isfile(f) if f.endswith('.csv')]
#print(files)

#split file names with whitespaces, names[][0]=date from file name
names = [n.split() for n in files]
#print( np.shape(names))
#print(names)

#read all the csv file into df list
dfa=[]
for f in files:
    df_t = pd.read_csv(f)
    dfa.append(df_t)
    
#for d in dfa:
#    print(d.head())
    
#for i in range(len(names)):
 #   print(names[i][0])
  #  print(dfa[i].head())

#process all df in the list
for i in range(len(names)):
    process_df(dfa[i],names[i][0], 0.5)

df_att = pd.DataFrame(columns=['Email','First name'])
for d in dfa:
    df_att = df_att.merge(d,on=['Email','First name'],how='outer').fillna(0)

#Create ID column from email
df_id = df_att["Email"].str.split('@',n=1,expand=True)
df_att.insert(1,'ID', df_id[0])

#Write summary to csv file
df_att.to_csv('Summary.csv')
