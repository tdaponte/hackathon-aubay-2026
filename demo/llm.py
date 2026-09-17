import boto3
import os
from dotenv import load_dotenv

from langchain_aws import ChatBedrockConverse

def init_llm():
    load_dotenv()

    # Set the API key as an environment variable
    api_key = os.getenv("AWS_BEDROCK_KEY")
    os.environ['AWS_BEARER_TOKEN_BEDROCK'] = api_key

    llm:ChatBedrockConverse = ChatBedrockConverse(
        model_id = "minimax.minimax-m2.5"
    )

    return llm

if __name__ == "__main__":
    llm = init_llm()
        
    messages = [
        (
            "system",
            "You are a helpful assistant that translates English to French. Translate the user sentence.",
        ),
        ("human", "I love programming."),
    ]

    response = llm.invoke(messages)
    print(response.content)
