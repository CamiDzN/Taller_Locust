

# Taller Locust - Pruebas de Carga para API de Inferencia

Este proyecto desarrolla una API de inferencia utilizando **FastAPI**, conectada a un modelo gestionado con **MLflow**, y realiza pruebas de carga con **Locust** para evaluar el uso de recursos y la escalabilidad de la solución.

---

## Arquitectura del Proyecto

La solución está compuesta por los siguientes servicios orquestados con **Docker Compose** y conectados en la red `mlops_net`:

- **Airflow**: Orquesta el flujo del pipeline de ML.  
- **PostgreSQL**: Almacena los metadatos de Airflow.  
- **Redis**: Gestiona la cola de tareas.  
- **MySQL**: Backend de datos y MLflow.  
- **MinIO**: Almacenamiento de artefactos tipo S3.  
- **MLflow**: Gestor y servidor de modelos.  
- **FastAPI**: Servidor que expone el modelo para realizar inferencias.  
- **Locust**: Realiza pruebas de carga.  
- **Random Data API**: Genera datos simulados para pruebas.

![image](https://github.com/user-attachments/assets/1e6b786c-10cd-4fbd-8a26-f886c211a674)

---

## Estructura del Proyecto

```
Taller_Locust/
├── airflow/
├── dags/
├── Data/
├── fastapi/
│   ├── Dockerfile
│   ├── main.py
│   ├── requirements.txt
├── locust/
│   ├── Dockerfile.locust
│   ├── locustfile.py
│   ├── requirements-locust.txt
├── mlflow/
├── mysql-init/
├── random-data-api/
│   ├── Dockerfile
│   ├── main.py
│   ├── requirements.txt
├── .env
├── .gitattributes
├── docker-compose.yml
├── docker-compose.locust.yaml
├── README.md
```

---

## Publicación y Uso de DockerHub

La imagen de **FastAPI** que implementa la API de inferencia ha sido construida y publicada en **Docker Hub** para facilitar el despliegue.

---

## Despliegue del Servicio de Inferencia

La API de inferencia se despliega en **Docker Compose** con los siguientes parámetros para la imagen:

```yaml
fastapi:
  image: camidzn/mlops:api-inference
  container_name: fastapi_service
  ports:
    - "8081:8081"
  volumes:
    - models_volume:/opt/airflow/models
  depends_on:
    - mysql
  environment:
    - MLFLOW_S3_ENDPOINT_URL=http://minio:9000
    - AWS_ACCESS_KEY_ID=admin
    - AWS_SECRET_ACCESS_KEY=supersecret
  deploy:
    resources:
      limits:
        memory: 2000M
        cpus: "0.5"
  networks:
    - mlops_net
```

---

## Código del archivo `locustfile.py`

El código para realizar las pruebas de carga está en el archivo locustfile.py:

```python
from locust import HttpUser, task, between
import random

class UsuarioDeCarga(HttpUser):
    wait_time = between(1, 2.5)

    @task
    def hacer_inferencia(self):
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
        if response.status_code != 200:
            print(f"❌ Error en la inferencia ({response.status_code}): {response.text}")
```

---

## Configuración y Ejecución de Locust

Archivos de configuración de Locust  
Se ha creado la carpeta `locust/` con los siguientes archivos:

- `Dockerfile.locust`  
- `locustfile.py`  
- `requirements-locust.txt`

---

## Despliegue de Locust

En el archivo `docker-compose.locust.yaml` se configura el servicio de Locust:

```yaml
services:
  locust:
    build:
      context: ./locust
      dockerfile: Dockerfile.locust
    ports:
      - "8089:8089"
    environment:
      - LOCUST_HOST=http://fastapi:8081
    networks:
      - taller_locust_mlops_net

networks:
  taller_locust_mlops_net:
    external: true
```

---

## Comando de Ejecución

Para iniciar Locust, ejecuta el siguiente comando:

```bash
docker-compose -f docker-compose.locust.yaml up --build
```
![image](https://github.com/user-attachments/assets/479abfdb-bbaa-4a44-8ce3-dbe843556b1d)


---

## Resultados de las Pruebas de Carga

**Prueba de Carga #1**  

- CPU: 0.5  
- RAM: 2000 MB  


![image](https://github.com/user-attachments/assets/4f874708-4ebc-45cb-8769-f9a417bdb0c0)

No se generan fallos, sin embargo los tiempos de respuesta aumentan linealmente llegando por encima de los 500 segundos, lo cual se podría considerar como un comportamiento no aceptable para el rendimiento de la API de inferencia. En relación a las peticiones respondidas por segundo se encuentran alrededor de las 18 RPS.

Al revisar desde Docker Desktop las estadísticas del contenedor encontramos:

![image](https://github.com/user-attachments/assets/cdfe2d68-ca04-4972-9331-bd3a53289169)

Un consumo de memoria RAM promedio de 953MB y un uso de CPU máximo del 50% que se mantiene después de estabilizar el tiempo de respuesta en 600.000ms en locust.

**Prueba de Carga #2**  

Teniendo en cuenta los resultados previos, se reduce la RAM a 1000MB y se aumentan los Cores a 0.75
a.	CPU: 0.75
b.	RAM: 1000 MB

Se ejecuta  “docker-compose up -d --no-deps fastapi” para recrear el contenedor de fastapi sin afectar los demás contenedores

  
![image](https://github.com/user-attachments/assets/0b8c9ae2-5927-4ae9-ac1f-09a7329e6f68)

No se generan fallos, y en este caso los tiempos de respuesta se estabilizan en 400 segundos, lo cual se podría considerar como un comportamiento no aceptable para el rendimiento de la API de inferencia. En relación a las peticiones respondidas por segundo estas aumentan llegando aproximadamente a las 25 RPS.

Al revisar desde Docker Desktop las estadísticas del contenedor encontramos:


![image](https://github.com/user-attachments/assets/f141fdff-9437-426e-b2d1-b6f48a19d540)

Un consumo promedio del 75% de la CPU con un consumo de RAM constante de 997MB aproximadamente.


**Prueba de Carga #3**  

Teniendo en cuenta los resultados previos, se mantiene la RAM en 1000MB y se aumentan los Cores a 1.5
a.	CPU: 1.5
b.	RAM: 1000 MB

Se ejecuta  “docker-compose up -d --no-deps fastapi” para recrear el contenedor de fastapi sin afectar los demás contenedores


![image](https://github.com/user-attachments/assets/4bae93c0-708c-45a1-9270-76f9d4152c1b)

De igual manera No se generan fallos, y en este caso los tiempos de respuesta se estabilizan en 300 segundos, lo cual se podría considerar como un comportamiento aceptable para el rendimiento de la API de inferencia. En relación a las peticiones respondidas por segundo aumentan nuevamente llegando hasta 40 RPS.

Al revisar desde Docker Desktop las estadísticas del contenedor encontramos:

![image](https://github.com/user-attachments/assets/92628617-9f34-4ede-8dec-01faa20bf108)

Un consumo promedio del 100% de la CPU con un consumo de RAM constante de 997MB aproximadamente.

**Prueba de Carga #4**  

Buscando mejorar los tiempos de respuesta promedio y las peticiones por segundo, se mantiene la RAM en 1000MB y se aumentan los Cores a 2
a.	CPU: 2
b.	RAM: 1000 MB

Se ejecuta  “docker-compose up -d --no-deps fastapi” para recrear el contenedor de fastapi sin afectar los demás contenedores

  
![image](https://github.com/user-attachments/assets/cd8260d6-d3d2-4756-bdf3-cf8b5091172d)

A pesar del aumento de CPU a 2 Cores los tiempos de respuesta se estabilizan de igual manera en 300 segundos, y las peticiones por segundo se mantienen en 40RPS. Lo que nos permite concluir que a nivel de CPU los valores aceptables que permiten un rendimiento adecuado están alrededor de los 1.5 Cores.

Al revisar desde Docker Desktop las estadísticas del contenedor encontramos:


![image](https://github.com/user-attachments/assets/30800142-7220-4a31-a4cc-2b7ceb4f75a5)

Un consumo promedio del 117% de la CPU con un consumo de RAM constante de 997MB aproximadamente.

---

## Pruebas de Carga con 3 Réplicas
Teniendo como base los recursos mínimo en 1.5 CPUs y 1000 MB se definen estos recursos limites añadiendo 3 replicar a través del Docker Compose en donde se encuentra la API de Inferencia:

Para generar replicas se modifica el FQDN al que apunta Locust definiendo fastapi, adicionalmente se agregan las replicas, se elimina el container name y los puertos para evitar conflictos de puertos al levantar las replicas.

Configuración de Docker Compose con Réplicas:

```yaml
fastapi:
  image: camidzn/mlops:api-inference
  volumes:
    - models_volume:/opt/airflow/models
  depends_on:
    - mysql
  environment:
    - MLFLOW_S3_ENDPOINT_URL=http://minio:9000
    - AWS_ACCESS_KEY_ID=admin
    - AWS_SECRET_ACCESS_KEY=supersecret
  deploy:
    replicas: 3
    resources:
      limits:
        memory: 1000M
        cpus: "1.5"
  networks:
    - mlops_net
```
Docker compose de fastapi incluyendo las replicas:

```yaml
  ################################################################
  # FastAPI - Inferencia
  ################################################################
  fastapi:
    image: camidzn/mlops:api-inference
    volumes:
      - models_volume:/opt/airflow/models
    depends_on:
      - mysql
    environment:
      - MLFLOW_S3_ENDPOINT_URL=http://minio:9000
      - AWS_ACCESS_KEY_ID=admin
      - AWS_SECRET_ACCESS_KEY=supersecret
    deploy:
      replicas: 3 #Incrementa el número de replicas
      resources:
        limits:
          memory: 1000M
          cpus: "1.5"
    networks:
      - mlops_net

```



**Resultados con 3 Réplicas**  

![image](https://github.com/user-attachments/assets/32680e49-cf25-40b5-803d-28d47acab8c6)

A pesar de que se mantuvieron los recursos minimos, al incluir 3 replicas el rendimiento de la API de inferencia aumentó llegando hasta 60 RPS y manteniendo el tiempo de respuesta promedio en 180 segundos.

Por lo que se realiza una prueba adicional de carga reduciendo a 400MB y 0.5CPU, en donde se obtienen los siguiente resultados:


![image](https://github.com/user-attachments/assets/5654e930-37c6-479d-9ec0-6d90b638fa1e)

Generando múltiples errores
Por lo que se procede nuevamente a aumentar la memoria RAM a 1000MB

![image](https://github.com/user-attachments/assets/f7aa2227-5af3-4d28-92a6-f0d5d0a102bc)

Se evidencia que el generar 3 replicas, genera 3 contenedores en donde se balancean automáticamente las peticiones, lo que permite reducir los limites de recurso de  CPU a una tercera parte y la RAM únicamente hasta lo mínimo requerido por la aplicación.


---

## Conclusiones

- La API puede manejar muchas peticiones por segundo aumentando recursos.
- Con 3 réplicas mejora la escalabilidad y reduce los tiempos.
- La configuración óptima es 1.5 CPUs y 1000 MB de RAM por réplica.
