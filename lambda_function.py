import json
import boto3
import csv

s3 = boto3.client('s3')

bedrock = boto3.client(
    service_name='bedrock-runtime',
    region_name='us-east-1'
)

def classify_ticket(message):
    prompt = f"""
    Clasifica el siguiente ticket de soporte.

    Ticket:
    "{message}"

    Devuelve:
    - categoria
    - prioridad
    - recomendacion
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
        sample_tickets = tickets[:10]

        print("CLASIFICACION DE TICKETS")

        for ticket in sample_tickets:
            message = ticket['customer_message']
            result = classify_ticket(message)

            print("--------------------------------")
            print("TICKET:")
            print(message)

            print("RESULTADO:")
            print(result)

        return {
            'statusCode': 200,
            'body': json.dumps('Clasificacion completada')
        }

    except Exception as e:
        print("ERROR:", str(e))

        return {
            'statusCode': 500,
            'body': json.dumps(f"Error: {str(e)}")
        }