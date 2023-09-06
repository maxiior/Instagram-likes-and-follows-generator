import pandas as pd

df = pd.read_csv("./data/maxiior_users_data.csv")

print(len(df['followedback'][df['followedback'] == True]))