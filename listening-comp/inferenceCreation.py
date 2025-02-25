import boto3

bedrock_client = boto3.client('bedrock')

# You need to use the full ARN of the model, not just the model ID
response = bedrock_client.create_inference_profile(
    inferenceProfileName="MarathiListeningPracticeProfile",
    description="Inference profile for Marathi Listening Practice application",
    modelSource={
        "copyFrom": "arn:aws:bedrock:us-east-1::foundation-model/us.amazon.nova-lite-v1:0"
    },
    tags=[
        {
            "key": "application",
            "value": "MarathiListeningPractice"
        }
    ]
)

print("Created inference profile with ARN:", response.get('inferenceProfileArn'))


# import boto3

# bedrock_client = boto3.client('bedrock')
# response = bedrock_client.list_foundation_models()

# for model in response['modelSummaries']:
#     print(f"Model ID: {model['modelId']}")
#     print(f"Model ARN: {model['modelArn']}")
#     print("---")