import numpy as np
import joblib
import os
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Input, Dropout

# Configuración: Dónde guardar los modelos
MODEL_DIR = "app/models"
os.makedirs(MODEL_DIR, exist_ok=True)

print(f"🏭 Iniciando fábrica de modelos con TensorFlow {tf.__version__}...")

# ---------------------------------------------------------
# 1. GENERAR DATOS SINTÉTICOS (Simulamos un sensor normal)
# ---------------------------------------------------------
# 2000 puntos. Media 50.0, Desviación 5.0.
# Esto enseña a los modelos que "lo normal" es oscilar alrededor de 50.
data = np.random.normal(loc=50.0, scale=5.0, size=(2000, 1))
print(f"📊 Datos generados: {data.shape}")

# ---------------------------------------------------------
# 2. ESCALADO (Scaler) - CRÍTICO
# ---------------------------------------------------------
print("⚖️  Entrenando Scaler...")
scaler = StandardScaler()
data_scaled = scaler.fit_transform(data)
joblib.dump(scaler, f"{MODEL_DIR}/scaler.joblib")

# ---------------------------------------------------------
# 3. MODELO 1: ISOLATION FOREST (Estadístico)
# ---------------------------------------------------------
print("🌲 Entrenando Isolation Forest...")
iso_forest = IsolationForest(contamination=0.01, random_state=42)
iso_forest.fit(data_scaled)
joblib.dump(iso_forest, f"{MODEL_DIR}/isolation_forest.joblib")

# ---------------------------------------------------------
# 4. MODELO 2: AUTOENCODER (Reconstrucción de Patrón)
# ---------------------------------------------------------
print("🧠 Entrenando Autoencoder...")
# El AE comprime el dato a 2 neuronas y trata de expandirlo. 
# Si entra basura (anomalía), el error de reconstrucción será alto.
ae_model = Sequential([
    Input(shape=(1,)),
    Dense(8, activation='relu'),
    Dense(2, activation='relu'), # Cuello de botella
    Dense(8, activation='relu'),
    Dense(1, activation='linear')
])
ae_model.compile(optimizer='adam', loss='mse')
ae_model.fit(data_scaled, data_scaled, epochs=10, batch_size=32, verbose=0)
ae_model.save(f"{MODEL_DIR}/autoencoder_model.h5")

# ---------------------------------------------------------
# 5. MODELO 3: LSTM (Secuencial)
# ---------------------------------------------------------
print("⏳ Entrenando LSTM...")
# Reshape para LSTM: [Samples, TimeSteps, Features] -> [2000, 1, 1]
X_lstm = data_scaled.reshape((data_scaled.shape[0], 1, 1))

lstm_model = Sequential([
    Input(shape=(1, 1)),
    LSTM(16, activation='relu', return_sequences=False),
    Dropout(0.1),
    Dense(1)
])
lstm_model.compile(optimizer='adam', loss='mse')
# Entrenamos para que aprenda la secuencia (aquí simplificada a reconstrucción)
lstm_model.fit(X_lstm, data_scaled, epochs=10, batch_size=32, verbose=0)
lstm_model.save(f"{MODEL_DIR}/lstm_model.h5")

print(f"\n✅ ¡ÉXITO! 4 Artefactos generados en '{MODEL_DIR}':")
print("   1. scaler.joblib")
print("   2. isolation_forest.joblib")
print("   3. autoencoder_model.h5")
print("   4. lstm_model.h5")