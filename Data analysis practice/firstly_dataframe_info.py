def dataframe_info(df):
    print(df.head(5))
    print(df.info()) 
    print(df.describe()) 
    print(df.isnull().sum())
    print(df.duplicated().sum())