import os
import argparse
import logging
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from azure.identity import InteractiveBrowserCredential, ClientSecretCredential, DefaultAzureCredential
from .sentinel_client import SentinelClient

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('SentinelMCP')

# Load environment variables
load_dotenv()

class SentinelServer:
    def __init__(self):
        self.mcp = FastMCP('MicrosoftSentinel-server')
        self.sentinel_client = None
        self._setup_tools()

    def _setup_tools(self):
        """Set up the MCP tools"""
        @self.mcp.tool()
        def sentinel_run_query(query: str) -> str:
            """ Run a query against Sentinel.
            Args:
                query: The Kusto Query Language (KQL) query to run.
            Returns:
                Results from the query
            """
            return self.sentinel_client.run_query(query)
            
        @self.mcp.tool()
        def sentinel_get_tables() -> str:
            """ Get all available tables in Azure Sentinel workspace.
            This tool does not use KQL queries and directly uses Azure APIs.
            
            Returns:
                A dictionary containing a list of all available tables in the Sentinel workspace
                with their metadata.
            """
            return self.sentinel_client.get_all_sentinel_tables()
            
        @self.mcp.tool()
        def sentinel_get_table_schema(table_name: str) -> str:
            """ Get schema for a specified table in Azure Sentinel workspace.
            This tool retrieves detailed column information for a specific table.
            
            Args:
                table_name: The name of the table to get schema for
                
            Returns:
                A dictionary containing table metadata and column information including 
                name, type, and description for each column.
            """
            return self.sentinel_client.get_table_schema(table_name)
            
        @self.mcp.tool()
        def sentinel_get_table_by_name(table_name: str) -> str:
            """ Get information for a specific table by name in Azure Sentinel workspace.
            This tool retrieves targeted information about a specific table using the Tables GET endpoint.
            
            Args:
                table_name: The name of the table to retrieve information for
                
            Returns:
                A dictionary containing structured table information including basic properties,
                retention settings, and schema details with columns.
            """
            return self.sentinel_client.get_table_by_name(table_name)

    def auth(self, auth_type):
        """  
        Authenticate with Azure using different credential types based on the provided auth_type.  
        """  
        logger.info(f"Starting authentication process using {auth_type}")
        if auth_type == "interactive":
            credential = InteractiveBrowserCredential()
            logger.info("Interactive browser credential created, waiting for login...")
        elif auth_type == "client_secret":
            credential = ClientSecretCredential(
                tenant_id=os.getenv('AZURE_TENANT_ID'),
                client_id=os.getenv('AZURE_CLIENT_ID'),
                client_secret=os.getenv('AZURE_CLIENT_SECRET')
            )
            logger.info("Client secret credential created")
        else:
            # Default credential for managed identities
            credential = DefaultAzureCredential()
            logger.info("Default Azure credential created")
        
        # Force authentication to make the user login  
        try:  
            logger.info("Requesting token to trigger authentication...")
            credential.get_token("https://management.azure.com/.default")
            logger.info("Authentication completed successfully")
        except Exception as e:  
            logger.error(f"Authentication failed: {e}")  
            logger.warning("Only unauthenticated tools can be used")
        
        return credential

    def create_clients(self, auth_credential):
        """  
        Create clients to external platforms using environment variables.  
        """  
        logger.info("Creating Sentinel client...")
        subscriptionId = os.getenv('SENTINEL_SUBSCRIPTION_ID')
        resourceGroupName = os.getenv('SENTINEL_RESOURCE_GROUP')
        workspaceName = os.getenv('SENTINEL_WORKSPACE_NAME')
        workspace_id = os.getenv('SENTINEL_WORKSPACE_ID')
        self.sentinel_client = SentinelClient(auth_credential, subscriptionId, resourceGroupName, workspaceName, workspace_id)
        logger.info("Sentinel client created successfully")
        return self.sentinel_client

    def run_tests(self):
        """Run test queries to verify functionality."""
        logger.info("Running Sentinel Test")
        sentinel_result = self.sentinel_client.run_query("Usage |project DataType | take 10")
        if sentinel_result["status"] == "success":
            logger.info("Sentinel Test executed successfully")
            return True
        else:
            logger.error("Sentinel Test failed")
            return False

    def run_server(self, run_tests=False):
        """Run the MCP server"""
        # Create clients and authenticate before starting the server
        auth_type = os.getenv('AUTHENTICATION_TYPE', 'interactive')
        
        # Complete auth and client creation before starting MCP server
        logger.info(f"Authenticating using {auth_type}")
        auth_credential = self.auth(auth_type)
        logger.info("Authentication completed, creating clients...")
        self.create_clients(auth_credential)
        logger.info("Clients created successfully")
        
        # Run tools test only if specified
        if run_tests:
            logger.info("Running tests...")
            self.run_tests()
        
        # Run MCP server with stdio or sse transport after authentication is complete
        logger.info("Starting MCP server...")
        self.mcp.run(transport="stdio")

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Sentinel MCP Server")
    parser.add_argument("--run-tests", action="store_true", help="Run tests before starting the server")
    args = parser.parse_args()
    
    server = SentinelServer()
    server.run_server(run_tests=args.run_tests)

if __name__ == "__main__":
    main()
