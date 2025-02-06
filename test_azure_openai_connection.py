import openai

def test_azure_openai_connection(api_key, endpoint, model="text-davinci-003"):
    """
    Test connection to Azure OpenAI service.

    Parameters:
    - api_key (str): Azure OpenAI API key.
    - endpoint (str): Azure OpenAI endpoint.
    - model (str): Model to test (default is "text-davinci-003").

    Returns:
    - Response from the OpenAI API if successful.
    - Error message if connection fails.
    """
    openai.api_type = "azure"
    openai.api_base = endpoint
    openai.api_version = "2023-03-15-preview"  # Ensure this matches your Azure OpenAI version
    openai.api_key = api_key

    try:
        response = openai.Completion.create(
            engine=model,
            prompt="Hello, Azure OpenAI!",
            max_tokens=5
        )
        print("Connection successful! Response:")
        print(response)
    except Exception as e:
        print("Connection failed. Error:")
        print(e)

if __name__ == "__main__":
    # Replace these placeholders with actual credentials
    API_KEY = "your_api_key_here"
    ENDPOINT = "https://your-endpoint-here.openai.azure.com/"
    MODEL = "text-davinci-003"  # Change if needed

    test_azure_openai_connection(API_KEY, ENDPOINT, MODEL)