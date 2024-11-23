from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, Embedding, Flatten, Concatenate, Input

app = Flask(__name__)

# Загрузка и предобработка данных
df = pd.read_csv('movie_rental_dataset.csv')  # Файл с вашими данными

# Выделяем целевую переменную и входные признаки
target = 'rating'  # Оценка, которую модель будет предсказывать
categorical_cols = ['customer_id', 'city', 'district', 'category', 'title', 'last_name', 'name', 'address']
numerical_cols = ['amount', 'length', 'rental_period', 'release_year']

# Кодирование категориальных признаков
label_encoders = {}
for col in categorical_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    label_encoders[col] = le

# Масштабирование числовых признаков
scaler = MinMaxScaler()
df[numerical_cols] = scaler.fit_transform(df[numerical_cols])

# Разделение данных на тренировочные и тестовые
X = df[categorical_cols + numerical_cols]
y = df[target]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Построение нейронной сети
def build_model(categorical_sizes, numerical_input_dim, embedding_dim=50):
    # Категориальные входы
    categorical_inputs = []
    embeddings = []
    for size in categorical_sizes:
        input_layer = Input(shape=(1,))
        embedding = Embedding(size, embedding_dim)(input_layer)
        embedding = Flatten()(embedding)
        categorical_inputs.append(input_layer)
        embeddings.append(embedding)

    # Числовые входы
    numerical_input = Input(shape=(numerical_input_dim,))
    numerical_dense = Dense(64, activation='relu')(numerical_input)

    # Объединение
    concatenated = Concatenate()(embeddings + [numerical_dense])
    dense_1 = Dense(128, activation='relu')(concatenated)
    dense_2 = Dense(64, activation='relu')(dense_1)
    output = Dense(1, activation='linear')(dense_2)

    # Модель
    model = Model(inputs=categorical_inputs + [numerical_input], outputs=output)
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    return model

# Размеры категориальных признаков
categorical_sizes = [df[col].nunique() for col in categorical_cols]

model = build_model(categorical_sizes, len(numerical_cols))
model.summary()

# Обучение модели
X_train_cat = [X_train[col].values for col in categorical_cols]
X_train_num = X_train[numerical_cols].values
X_test_cat = [X_test[col].values for col in categorical_cols]
X_test_num = X_test[numerical_cols].values

model.fit(
    X_train_cat + [X_train_num],
    y_train,
    validation_data=(X_test_cat + [X_test_num], y_test),
    epochs=5,
    batch_size=64,
    verbose=1
)

# Flask API
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json

    # Обработка входных данных
    input_cat = [np.array([label_encoders[col].transform([data[col]])[0]]) for col in categorical_cols]
    input_num = np.array([[data[col] for col in numerical_cols]])

    # Предсказание
    prediction = model.predict(input_cat + [input_num])
    predicted_rating = prediction[0][0]

    # Выбор топ-5 фильмов по рейтингу
    recommendations = df.sort_values(by='rating', ascending=False)['title'].unique()[:5].tolist()

    return jsonify({'predicted_rating': predicted_rating, 'recommendations': recommendations})

if __name__ == '__main__':
    app.run(debug=True)
