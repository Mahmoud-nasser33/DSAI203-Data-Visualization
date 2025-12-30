import pandas as pd


df = pd.read_csv("loan_data.csv")


# Numerical Columns: Fill with Median

df["Income"] = df["Income"].fillna(df["Income"].median())
df["Insured_Income"] = df["Insured_Income"].fillna(df["Insured_Income"].median())

# Categorical Columns: Fill with Mode (Most Frequent Value)

df["Education"] = df["Education"].fillna("Graduate")       
df["Credit_History"] = df["Credit_History"].fillna("Good") 


# Converting 
df["Credit_History"] = df["Credit_History"].astype("category")
df["Loan_Status"] = df["Loan_Status"].astype("category")
df["Gender"] = df["Gender"].astype("category")


df.to_csv("clean_loan_data.csv", index=False)


