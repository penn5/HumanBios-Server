import pandas as pd

col = ['city']
df = pd.read_csv('csv/cities.csv', usecols=col)
print(df['city'][100:140])
df.sample(n=2500).to_csv('csv/inform_loc_full.csv', index=False)
