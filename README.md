# Proyecto-Final---Big-Data-en-AWS-Lakehouse-Iceberg-y-Bedrock-

Clasificación de Incidencias con AWS Lambda + Bedrock
1. Descripción del Proyecto

Este proyecto implementa una solución serverless en AWS para la clasificación automática de incidencias a partir de archivos CSV. Utiliza servicios gestionados como Amazon S3, AWS Lambda, Amazon Bedrock y Amazon Athena para construir un pipeline escalable, automatizado y eficiente.

El flujo permite procesar tickets de incidencias, analizar su contenido mediante modelos de lenguaje (LLM) y generar resultados estructurados listos para análisis.


2. Objetivos
   
- Automatizar la clasificación de incidencias.
- Reducir el trabajo manual en el análisis de tickets.
- Implementar una arquitectura escalable y sin servidores.
- Facilitar el análisis de datos mediante consultas SQL (Athena).


3. Tecnologías Utilizadas
   
- AWS Lambda
- Amazon S3
- Amazon Bedrock
- Amazon Athena
- Python (procesamiento y lógica)


4. Arquitectura del Proyecto

La solución sigue una arquitectura basada en eventos (event-driven) donde cada componente cumple una función específica dentro del pipeline de datos:

- Amazon S3 (Raw): Almacena los archivos CSV originales con los tickets.
- AWS Lambda: Procesa los archivos y orquesta la comunicación con Bedrock.
- Amazon Bedrock: Realiza la clasificación de texto utilizando modelos de IA.
- Amazon S3 (Curated): Guarda los resultados procesados en formato JSON.
- Amazon Athena: Permite consultar y analizar los resultados.


5. Flujo del Procesamiento 
El funcionamiento del sistema se describe en los siguientes pasos:

- El usuario carga un archivo CSV con los tickets en el bucket S3 Raw.
- S3 genera automáticamente un evento que activa una función Lambda.
- Lambda procesa el archivo CSV y extrae los datos relevantes.
- Se realiza una selección de registros para su análisis.
- Lambda envía solicitudes (prompts) al modelo en Bedrock.
- Bedrock analiza los textos y devuelve la clasificación correspondiente.
- Lambda construye un archivo JSON con los resultados obtenidos.
- El JSON es almacenado en el bucket S3 Curated.
- Athena permite consultar y analizar los resultados almacenados.

