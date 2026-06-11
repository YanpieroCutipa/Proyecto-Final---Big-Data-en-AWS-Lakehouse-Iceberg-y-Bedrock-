import json
import boto3
import csv
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('tickets_auditoria')

s3 = boto3.client('s3')

bedrock = boto3.client(
    service_name='bedrock-runtime',
    region_name='us-east-1'
)

def classify_ticket(message):

    prompt = f"""
    Clasifica el siguiente ticket.

    Ticket:
    "{message}"

    Responde ÚNICAMENTE en formato JSON válido.

    Ejemplo:

    {{
        "categoria": "Acceso",
        "prioridad": "Alta",
        "recomendacion": "Restablecer contraseña"
    }}

    No agregues explicaciones ni texto adicional.
    """

    body = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "inferenceConfig": {
            "max_new_tokens": 300
        }
    }

    response = bedrock.invoke_model(
        modelId="us.amazon.nova-2-lite-v1:0",
        body=json.dumps(body)
    )

    response_body = json.loads(response['body'].read())

    return response_body['output']['message']['content'][0]['text']


def lambda_handler(event, context):

    print("EVENTO RECIBIDO:")
    print(json.dumps(event))

    try:

        bucket_name = event['Records'][0]['s3']['bucket']['name']
        file_key = event['Records'][0]['s3']['object']['key']

        print(f"Archivo recibido: {file_key}")

        response = s3.get_object(
            Bucket=bucket_name,
            Key=file_key
        )

        file_content = response['Body'].read()

        try:
            content = file_content.decode('utf-8-sig')
        except UnicodeDecodeError:
            content = file_content.decode('latin-1')

        lines = content.splitlines()
        reader = csv.DictReader(lines, delimiter=';')

        tickets = list(reader)

        print(f"Tickets encontrados: {len(tickets)}")

        sample_tickets = tickets[:10]

        resultados = []

        for idx, ticket in enumerate(sample_tickets, start=1):

            if 'customer_message' not in ticket:
                print(f"Ticket {idx}: columna customer_message no encontrada")
                continue

            message = ticket['customer_message']

            if not message:
                print(f"Ticket {idx}: mensaje vacío")
                continue

            print("--------------------------------")
            print(f"Procesando ticket {idx}")

            result = classify_ticket(message)

            print("RESPUESTA BEDROCK:")
            print(result)

            result = result.strip()

            if result.startswith("```json"):
                result = result.replace("```json", "")
                result = result.replace("```", "")
                result = result.strip()

            clasificacion_json = json.loads(result)

            resultados.append({
                "ticket_id": idx,
                "mensaje": message,
                "categoria": clasificacion_json["categoria"],
                "prioridad": clasificacion_json["prioridad"],
                "recomendacion": clasificacion_json["recomendacion"]
            })

        json_resultados = "\n".join(
            json.dumps(item, ensure_ascii=False)
            for item in resultados
        )

        output_key = (
            file_key
            .replace("raw/", "curated/")
            .replace(".csv", "_clasificado.json")
        )

        s3.put_object(
            Bucket=bucket_name,
            Key=output_key,
            Body=json_resultados,
            ContentType='application/json'
        )

        table.put_item(
            Item={
                'archivo': file_key,
                'fecha_proceso': datetime.now().isoformat(),
                'tickets_procesados': len(resultados),
                'estado': 'COMPLETADO'
            }
        )

        print(f"Resultados guardados en: {output_key}")
        print(f"Auditoría guardada en DynamoDB para archivo: {file_key}")

        return {
            "statusCode": 200,
            "body": json.dumps({
                "mensaje": "Clasificación completada",
                "archivo_salida": output_key,
                "tickets_procesados": len(resultados)
            })
        }

    except Exception as e:

        print("ERROR:", str(e))

        return {
            "statusCode": 500,
            "body": json.dumps(
                f"Error: {str(e)}"
            )
        }