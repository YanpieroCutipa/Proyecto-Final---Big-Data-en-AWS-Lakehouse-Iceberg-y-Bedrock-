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
    try:  
        bucket_name = 'tickets-bedrock-mayron-2026'
        file_key = 'raw/tickets.csv'

        response = s3.get_object(
            Bucket=bucket_name,
            Key=file_key
        )

        content = response['Body'].read().decode('utf-8-sig')
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