def column_act(col):
    print(df[col].value_counts())
    df[col] = df[col].fillna('none')
    print(df[col].isnull().sum())