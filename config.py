# ... 现有代码 ...

# Azure OpenAI 配置
AZURE_CONFIG = {
    "api_type": "azure",
    "api_version": "2024-08-01-preview",
    "api_base": os.getenv('AZURE_OPENAI_ENDPOINT', 'https://ai-search-gpt4.openai.azure.com'),
    "api_key": os.getenv('AZURE_OPENAI_API_KEY'),
    "deployment_name": "gpt-4o"
}

# 使用 Azure OpenAI
os.environ["OPENAI_API_TYPE"] = AZURE_CONFIG["api_type"]
os.environ["OPENAI_API_VERSION"] = AZURE_CONFIG["api_version"]
os.environ["OPENAI_API_BASE"] = AZURE_CONFIG["api_base"]
os.environ["OPENAI_API_KEY"] = AZURE_CONFIG["api_key"]
os.environ["OPENAI_DEPLOYMENT_NAME"] = AZURE_CONFIG["deployment_name"]

# 导出配置
CONFIG = {**BASE_CONFIG, **AZURE_CONFIG}