from locust import HttpUser, task, between
import random

class UsuarioDeCarga(HttpUser):
    """Simula usuarios enviando solicitudes al endpoint /predict de la API."""
    
    wait_time = between(1, 2.5)  # Tiempo de espera aleatorio entre peticiones
    
    @task
    def hacer_inferencia(self):
        """Envía una solicitud POST al endpoint /predict con datos simulados."""
        
        payload = {
            "Elevation": round(random.uniform(1000, 3000), 2),
            "Aspect": round(random.uniform(0, 360), 2),
            "Slope": round(random.uniform(0, 90), 2),
            "Horizontal_Distance_To_Hydrology": round(random.uniform(0, 2000), 2),
            "Vertical_Distance_To_Hydrology": round(random.uniform(-100, 100), 2),
            "Horizontal_Distance_To_Roadways": round(random.uniform(0, 5000), 2),
            "Hillshade_9am": round(random.uniform(0, 255), 2),
            "Hillshade_Noon": round(random.uniform(0, 255), 2),
            "Hillshade_3pm": round(random.uniform(0, 255), 2),
            "Horizontal_Distance_To_Fire_Points": round(random.uniform(0, 5000), 2),
        }
        
        response = self.client.post("/predict/", json=payload)
        
        # Validación opcional para verificar respuestas incorrectas
        if response.status_code != 200:
            print(f"❌ Error en la inferencia ({response.status_code}): {response.text}")