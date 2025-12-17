import socket
import time
import logging
import numpy as np
import joblib
import os

# Importamos TensorFlow de forma segura
try:
    from tensorflow.keras.models import load_model
except ImportError:
    load_model = None

from app.repositories.measurement_repo import MeasurementRepository

logger = logging.getLogger("service")

class AnomalyService:
    def __init__(self, repo: MeasurementRepository):
        self.repo = repo
        self.hostname = socket.gethostname()
        self.model_loaded = False
        
        # Rutas absolutas dentro del contenedor (/code/app/models)
        # O relativas si estamos en local
        base_path = "/code/app/models" if os.path.exists("/code/app/models") else "app/models"
        
        self.SCALER_PATH = os.path.join(base_path, "scaler.joblib")
        self.ISO_PATH = os.path.join(base_path, "isolation_forest.joblib")
        self.AE_PATH = os.path.join(base_path, "autoencoder_model.h5")
        self.LSTM_PATH = os.path.join(base_path, "lstm_model.h5")
        
        # Umbrales de sensibilidad (Basados en tu entrenamiento)
        # Si el error de reconstrucción supera esto, es anomalía
        self.AE_THRESHOLD = 0.5  
        self.LSTM_THRESHOLD = 0.5
        
        self._load_models()

    def _load_models(self):
        try:
            logger.info("🔄 Cargando red neuronal y modelos estadísticos...")
            
            # 1. Cargar Scikit-Learn
            self.scaler = joblib.load(self.SCALER_PATH)
            self.isolation_model = joblib.load(self.ISO_PATH)
            
            # 2. Cargar TensorFlow
            if load_model:
                # compile=False hace que la carga sea más rápida y segura en producción
                self.autoencoder = load_model(self.AE_PATH, compile=False)
                self.lstm_model = load_model(self.LSTM_PATH, compile=False)
            else:
                raise ImportError("Librería TensorFlow no encontrada")

            self.model_loaded = True
            logger.info("✅ CEREBRO CARGADO: Sistema de Votación 4-Way listo.")
        except Exception as e:
            logger.error(f"⚠️ Error crítico cargando modelos IA: {e}. Activando modo fallback.")
            self.model_loaded = False

    def process_measurement(self, sensor_id: str, value: float) -> dict:
        # 1. Persistencia (Siempre guardar primero)
        timestamp_sec = self.repo.save(sensor_id, value)
        
        votos = 0
        detalles = {}
        es_anomalia = False
        
        if self.model_loaded:
            try:
                # A. Preprocesamiento (Escalar el dato)
                # La IA no entiende "50 grados", entiende "0.5 normalizado"
                raw_data = np.array([[value]])
                scaled_data = self.scaler.transform(raw_data)
                
                # Input para LSTM requiere 3 dimensiones [Samples, TimeSteps, Features]
                lstm_input = scaled_data.reshape((1, 1, 1))

                # --- B. LA VOTACIÓN (M-of-N) ---

                # VOTO 1: Regla Física (Seguridad Hard)
                if value > 100.0:
                    votos += 1
                    detalles['Regla_Fisica'] = 'CRITICO (>100)'

                # VOTO 2: Isolation Forest (Estadístico)
                pred_iso = self.isolation_model.predict(scaled_data)[0]
                if pred_iso == -1: # -1 significa anomalía
                    votos += 1
                    detalles['Isolation_Forest'] = 'Outlier detectado'

                # VOTO 3: Autoencoder (Patrón)
                # Si no puede reconstruir el dato, es que no lo ha visto antes
                reconstruccion = self.autoencoder.predict(scaled_data, verbose=0)
                mse_ae = np.mean(np.power(scaled_data - reconstruccion, 2))
                if mse_ae > self.AE_THRESHOLD:
                    votos += 1
                    detalles['Autoencoder'] = f'Error Patrón ({mse_ae:.2f})'

                # VOTO 4: LSTM (Secuencia)
                pred_lstm = self.lstm_model.predict(lstm_input, verbose=0)
                mse_lstm = np.mean(np.power(scaled_data - pred_lstm, 2))
                if mse_lstm > self.LSTM_THRESHOLD:
                    votos += 1
                    detalles['LSTM'] = f'Error Secuencia ({mse_lstm:.2f})'

                # --- C. VEREDICTO FINAL ---
                # Consenso Robusto: Necesitamos 3 de 4 votos para dar la alarma
                if votos >= 3:
                    es_anomalia = True
                
            except Exception as e:
                logger.error(f"Error durante inferencia IA: {e}")
                # Si falla la IA, usamos regla simple por seguridad
                es_anomalia = value > 100.0
        else:
            # Modo Fallback (Sin IA)
            es_anomalia = value > 100.0
            detalles['sistema'] = 'IA_OFFLINE'

        # Log solo si es anomalía (para no saturar)
        if es_anomalia:
            logger.warning(f"🚨 ANOMALÍA CONFIRMADA ({sensor_id}): Valor {value} | Votos: {votos}/4")

        return {
            "sensor_id": sensor_id,
            "valor": value,
            "timestamp": timestamp_sec,
            "es_anomalia": es_anomalia,
            "votos_consenso": votos,
            "detalles": detalles,
            "procesado_por": self.hostname
        }
    
    def get_history(self, sensor_id: str):
        raw = self.repo.get_all(sensor_id)
        return {
            "sensor_id": sensor_id,
            "total_records": len(raw),
            "measurements": [{"time": ts/1000, "value": val} for ts, val in raw]
        }
    
    def evaluate_measurement(self, sensor_id: str, value: float) -> dict:
        """Evalúa sin guardar en base de datos (Simulación)"""
        votos = 0
        detalles = {}
        es_anomalia = False
        timestamp_simulado = time.time() # Generamos timestamp al vuelo
        
        if self.model_loaded:
            try:
                # --- COPIA DE LA LÓGICA DE VOTACIÓN ---
                raw_data = np.array([[value]])
                scaled_data = self.scaler.transform(raw_data)
                lstm_input = scaled_data.reshape((1, 1, 1))

                # VOTO 1: Físico
                if value > 100.0:
                    votos += 1
                    detalles['VOTO_1_Fisico'] = 'CRITICO (>100)'

                # VOTO 2: Isolation Forest
                pred_iso = self.isolation_model.predict(scaled_data)[0]
                if pred_iso == -1: 
                    votos += 1
                    detalles['VOTO_2_ISO'] = 'Outlier detectado'

                # VOTO 3: Autoencoder
                reconstruccion = self.autoencoder.predict(scaled_data, verbose=0)
                mse_ae = np.mean(np.power(scaled_data - reconstruccion, 2))
                if mse_ae > self.AE_THRESHOLD:
                    votos += 1
                    detalles['VOTO_3_AE'] = f'Error Patrón ({mse_ae:.2f})'

                # VOTO 4: LSTM
                pred_lstm = self.lstm_model.predict(lstm_input, verbose=0)
                mse_lstm = np.mean(np.power(scaled_data - pred_lstm, 2))
                if mse_lstm > self.LSTM_THRESHOLD:
                    votos += 1
                    detalles['VOTO_4_LSTM'] = f'Error Secuencia ({mse_lstm:.2f})'

                # Consenso
                if votos >= 3:
                    es_anomalia = True
                
            except Exception as e:
                logger.error(f"Error IA simulada: {e}")
                es_anomalia = value > 100.0
                detalles['sistema'] = f'IA_ERROR'
        else:
            es_anomalia = value > 100.0
            detalles['sistema'] = 'IA_OFFLINE'

        return {
            "sensor_id": sensor_id,
            "valor": value,
            "timestamp": timestamp_simulado,
            "es_anomalia": es_anomalia,
            "votos_consenso": votos,
            "detalles": detalles,
            "procesado_por": self.hostname,
            "status": "simulacion"
        }