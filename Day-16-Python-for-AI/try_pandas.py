import pandas as pd

#Read from csv
df = pd.read_csv(r"Day-16-Python-for-AI\try.csv")
print(df)

print(df['Name'])
print(df.loc[1, "Name"])

data = {
    "Name":["Hari","Chand"],
    "Age":[22,24],
    "City":["lat","ktm"]
}
df = pd.DataFrame(data)

df.to_csv(
    r"Day-16-Python-for-AI\try.csv",
    index = False
)