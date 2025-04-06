# Analysis service

## Development Environment

1. **Create Environment and Install Packages**

   ```shell
   conda create -n analysis_service python=3.10
   ```

   ```shell
   conda activate analysis_service
   ```

   ```shell
   pip install -r requirements.txt
   ```

2. **Configure OpenAI or Azure OpenAI**

   You have two options for using OpenAI API:

   **a. Standard OpenAI:**
   
   Create a `.env` file and add your OpenAI API key:
   ```
   OPENAI_API_KEY="your-openai-api-key"
   USE_AZURE_OPENAI="false"
   ```

   **b. Azure OpenAI:**
   
   Create a `.env` file with your Azure OpenAI configuration:
   ```
   USE_AZURE_OPENAI="true"
   AZURE_OPENAI_API_KEY="your-azure-openai-api-key"
   AZURE_OPENAI_API_VERSION="2023-05-15"
   AZURE_OPENAI_API_BASE="https://your-resource-name.openai.azure.com"
   AZURE_OPENAI_DEPLOYMENT="your-deployment-name"
   ```

   Note: When using Azure OpenAI, the deployment name is used instead of the model name specified in the config files.

3. **Run the Application**

   ```shell
   uvicorn app:app --port 7070
   ```
