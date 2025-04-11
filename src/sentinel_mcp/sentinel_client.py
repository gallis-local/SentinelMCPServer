import pandas as pd 
from azure.monitor.query import LogsQueryClient, LogsQueryStatus
from azure.core.exceptions import HttpResponseError
import requests
import json

class SentinelClient:
    login_url = "https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    API_url = "https://management.azure.com/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.OperationalInsights/workspaces/{workspaceName}/providers/Microsoft.SecurityInsights/"
    API_query_url = "https://management.azure.com/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.OperationalInsights/workspaces/{workspaceName}/providers/Microsoft.Insights/"
    API_management_url = "https://management.azure.com"
    API_versionOLD = "2021-03-01-preview"
    API_version_incidents = "2021-04-01"
    API_version_rules = "2021-10-01"
    API_version_logs = "2018-08-01-preview"
    API_version_tables = "2021-12-01-preview"
    API_version_templates = "2023-02-01"
    scope = "https://management.azure.com/.default"

    def __init__(self, credential, subscriptionId, resourceGroupName, workspaceName, workspace_id):
        self.subscriptionId = subscriptionId
        self.resourceGroupName = resourceGroupName
        self.workspaceName = workspaceName
        self.workspace_id = workspace_id
        self.access_token_timestamp = 0
        self.credential = credential
        self.logs_client = LogsQueryClient(self.credential)

    def run_query(self, query, printresults=False):
        results_object = {}
        try:
            response = self.logs_client.query_workspace(
                workspace_id=self.workspace_id,
                query=query,
                timespan=None
                )
            if response.status == LogsQueryStatus.PARTIAL:
                error = response.partial_error
                data = response.partial_data
                print(error.message)
            elif response.status == LogsQueryStatus.SUCCESS:
                data = response.tables
            for table in data:
                df = pd.DataFrame(data=table.rows, columns=table.columns)
                if printresults:
                    print(df)
                results_object = {"status": "success", "result": df.to_dict(orient="records")}
        except HttpResponseError as err:
            results_object = {"status": "error", "result": str(err)}
        return results_object
        
    def get_all_sentinel_tables(self):
        """
        Get all available tables in Azure Sentinel workspace without using Kusto queries.
        Uses Azure REST API to fetch table information directly.
        
        Returns:
            dict: Dictionary containing status and result (list of tables with only name and displayName)
        """
        results_object = {}
        try:
            # Get access token from credential
            token = self.credential.get_token(self.scope).token
            
            # Construct the URL to get all tables in the workspace
            url = f"https://management.azure.com/subscriptions/{self.subscriptionId}/resourceGroups/{self.resourceGroupName}/providers/Microsoft.OperationalInsights/workspaces/{self.workspaceName}/tables?api-version={self.API_version_tables}"
            
            # Set up headers with the access token
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            # Make the request
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            # Process the response
            tables_data = response.json()
            
            # Extract only table names and display names
            tables = []
            if 'value' in tables_data:
                for table in tables_data['value']:
                    # Create a minimal table info object with just name 
                    table_info = {
                        'name': table.get('name', '')
                    }
                    
                    
                    tables.append(table_info)
            
            results_object = {"status": "success", "result": tables}
        except Exception as err:
            results_object = {"status": "error", "result": str(err)}
            
        return results_object
    
    def get_table_schema(self, table_name):
        """
        Get the schema for a specified table in Azure Sentinel workspace.
        
        Args:
            table_name (str): The name of the table to get schema for
            
        Returns:
            dict: Dictionary containing status and result (schema information)
        """
        results_object = {}
        try:
            # Get access token from credential
            token = self.credential.get_token(self.scope).token
            
            # Construct the URL to get the specific table schema
            url = f"https://management.azure.com/subscriptions/{self.subscriptionId}/resourceGroups/{self.resourceGroupName}/providers/Microsoft.OperationalInsights/workspaces/{self.workspaceName}/tables/{table_name}?api-version={self.API_version_tables}"
            
            # Set up headers with the access token
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            # Make the request
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            # Process the response
            table_data = response.json()
            
            
            results_object = {"status": "success", "result": table_data}
        except Exception as err:
            results_object = {"status": "error", "result": str(err)}
            
        return results_object
        
    def get_table_by_name(self, table_name):
        """
        Get information for a specific table by name in Azure Sentinel workspace.
        Uses the Tables GET endpoint from Azure Log Analytics API.
        Returns table metadata without columns information (which can be fetched separately).
        
        Args:
            table_name (str): The name of the table to retrieve
            
        Returns:
            dict: Dictionary containing status and result with table information
        """
        results_object = {}
        try:
            # Get access token from credential
            token = self.credential.get_token(self.scope).token
            
            # Construct the URL to get the specific table
            url = f"https://management.azure.com/subscriptions/{self.subscriptionId}/resourceGroups/{self.resourceGroupName}/providers/Microsoft.OperationalInsights/workspaces/{self.workspaceName}/tables/{table_name}?api-version={self.API_version_tables}"
            
            # Set up headers with the access token
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            # Make the request
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            # Process the response
            table_data = response.json()
            
            # Extract relevant table information
            table_info = {
                'name': table_data.get('name', ''),
                'id': table_data.get('id', ''),
                'type': table_data.get('type', ''),
            }
            
            # Add properties
            properties = table_data.get('properties', {})
            if properties:
                table_info['properties'] = {
                    'retentionInDays': properties.get('retentionInDays', 0),
                    'totalRetentionInDays': properties.get('totalRetentionInDays', 0),
                    'archiveRetentionInDays': properties.get('archiveRetentionInDays', 0),
                    'plan': properties.get('plan', ''),
                    'provisioningState': properties.get('provisioningState', '')
                }
            
            # Add schema metadata (excluding columns and standardColumns which are too verbose)
            schema = properties.get('schema', {})
            if schema:
                table_info['schema'] = {
                    'name': schema.get('name', ''),
                    'tableType': schema.get('tableType', ''),
                    'tableSubType': schema.get('tableSubType', ''),
                    'displayName': schema.get('displayName', ''),
                    'description': schema.get('description', '')
                    # columns and standardColumns are excluded as they're fetched by get_table_schema
                }
            
            results_object = {"status": "success", "result": table_info}
        except Exception as err:
            results_object = {"status": "error", "result": str(err)}
            
        return results_object
