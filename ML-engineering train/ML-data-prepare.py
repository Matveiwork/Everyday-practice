def ML_convert(df):
    from sklearn.preprocessing import StandardScaler
    from sklearn.preprocessing import OneHotEncoder
    
    df1 = df.dropna()
    numeric_cols = df1.select_dtypes(include=['int16', 'int32', 'int64', 'float16', 'float32', 'float64'])
    categorial_cols = df1.select_dtypes(include=['object'])
    sc = StandardScaler()
    dfsc = sc.fit_transform(numeric_cols)
    std_scaler_data = sc.transform(numeric_cols)
    df1[numeric_cols.columns] = std_scaler_data

    ohe = OneHotEncoder(sparse_output=False)
    ohe.fit(categorial_cols)
    ohe1 = ohe.transform(categorial_cols)
    df1[ohe.get_feature_names_out()] = ohe1
    
    
    print(df1.info())