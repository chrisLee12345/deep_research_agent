# ... 现有代码 ...

# Azure OpenAI 配置
AZURE_CONFIG = {
    "api_type": "azure",
    "api_version": "2024-08-01-preview",
    "api_base": "https://ai-search-gpt4.openai.azure.com",
    "api_key": "DuyZ0hHrPDcKN5FswiEyi43Reqqu2qLulqfQMglca8xDYA79URG3JQQJ99BAACYeBjFXJ3w3AAABACOGvlW6",
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