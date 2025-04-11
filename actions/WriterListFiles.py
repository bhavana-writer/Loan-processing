from writer.abstract import register_abstract_template
from writer.blocks.base_block import WorkflowBlock
from writer.ss_types import AbstractTemplate
import requests
import os


class WriterListFiles(WorkflowBlock):
    @classmethod
    def register(cls, type: str):
        super(WriterListFiles, cls).register(type)
        register_abstract_template(type, AbstractTemplate(
            baseType="workflows_node",
            writer={
                "name": "List Files (REST)",
                "description": "Lists all files using the Writer REST API directly.",
                "category": "Writer",
                "fields": {
                    "limit": {
                        "name": "Limit",
                        "type": "Number",
                        "desc": "The number of items to retrieve",
                        "default": "50",
                        "validator": {
                            "type": "number",
                            "minimum": 1,
                            "maximum": 100,
                        }
                    },
                    "order": {
                        "name": "Order",
                        "type": "Text",
                        "desc": "The order in which to retrieve items",
                        "default": "desc",
                        "options": {
                            "asc": "Ascending",
                            "desc": "Descending"
                        }
                    },
                    "status": {
                        "name": "Status",
                        "type": "Text",
                        "desc": "Filter files by processing status",
                        "default": "",
                        "options": {
                            "": "All",
                            "in_progress": "In Progress",
                            "completed": "Completed",
                            "failed": "Failed"
                        }
                    },
                    "graph_id": {
                        "name": "Graph ID",
                        "type": "Text",
                        "desc": "Filter files by graph ID",
                        "default": "",
                    },
                    "after": {
                        "name": "After Cursor",
                        "type": "Text",
                        "desc": "Return items after this file ID (e.g., 094b7358-5c50-4cc6-b5cf-6c87524e163f). Use this for getting the next page of results.",
                        "default": "",
                    },
                    "before": {
                        "name": "Before Cursor",
                        "type": "Text",
                        "desc": "Return items before this file ID (e.g., 094b7358-5c50-4cc6-b5cf-6c87524e163f). Use this for getting the previous page of results.",
                        "default": "",
                    },
                    "include_id_list": {
                        "name": "Include File ID List",
                        "type": "Text",
                        "desc": "Create an additional list of file IDs for easy access in workflows",
                        "default": "yes",
                        "options": {
                            "yes": "Yes - Create ID List",
                            "no": "No - Skip ID List"
                        }
                    }
                },
                "outs": {
                    "success": {
                        "name": "Success",
                        "description": "If the execution was successful.",
                        "style": "success",
                    },
                    "error": {
                        "name": "Error",
                        "description": "If the function raises an Exception.",
                        "style": "error",
                    },
                },
            }
        ))

    def run(self):
        try:
            import writer.ai
            
            print("\n=== WriterListFiles Execution Start ===")
            
            # Get API token from environment or configuration
            api_token = os.getenv("WRITER_API_KEY")
            if not api_token:
                raise ValueError("No API token found. Please set WRITER_API_KEY environment variable")
            
            print("[WriterListFiles] API token retrieved")
            
            # Build query parameters
            params = {}
            
            # Handle limit with validation
            try:
                limit = self._get_field("limit", default_field_value=50)
                if limit is not None and str(limit).strip():
                    limit_value = int(limit)
                    if 1 <= limit_value <= 100:
                        params["limit"] = limit_value
                        print(f"[WriterListFiles] Using limit: {params['limit']}")
                    else:
                        print(f"[WriterListFiles] Limit {limit_value} out of range, using default")
            except (ValueError, TypeError) as e:
                print(f"[WriterListFiles] Invalid limit value, using default: {e}")
            
            # Handle order
            order = self._get_field("order", default_field_value="desc")
            if order in ["asc", "desc"]:
                params["order"] = order
            
            # Handle status
            status = self._get_field("status", default_field_value="")
            if status in ["in_progress", "completed", "failed"]:
                params["status"] = status
                print(f"[WriterListFiles] Filtering by status: {status}")
            
            # Handle graph_id
            graph_id = self._get_field("graph_id", default_field_value="")
            if graph_id and str(graph_id).strip():
                params["graph_id"] = str(graph_id)
                print(f"[WriterListFiles] Filtering by graph_id: {graph_id}")
            
            # Handle pagination cursors
            after = self._get_field("after", default_field_value="")
            if after and str(after).strip():
                params["after"] = str(after)
            
            before = self._get_field("before", default_field_value="")
            if before and str(before).strip():
                params["before"] = str(before)
            
            print(f"[WriterListFiles] Query parameters: {params}")
            
            # Make REST API call
            headers = {
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                "https://api.writer.com/v1/files",
                params=params,
                headers=headers
            )
            
            print(f"[WriterListFiles] API Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                # Check if we should include the ID list
                include_ids = self._get_field("include_id_list", default_field_value="yes") == "yes"
                if include_ids:
                    # Extract file IDs from the data array
                    file_ids = [file["id"] for file in result.get("data", [])]
                    print(f"[WriterListFiles] Extracted {len(file_ids)} file IDs")
                    result["file_id_array"] = file_ids
                
                print(f"[WriterListFiles] Retrieved {len(result.get('data', []))} files")
                self.result = result
                self.outcome = "success"
            else:
                print(f"[WriterListFiles] API Error: {response.text}")
                raise Exception(f"API returned status code {response.status_code}")
            
            print("[WriterListFiles] Execution completed successfully")
            
        except Exception as e:
            self.outcome = "error"
            print(f"[WriterListFiles] Error occurred: {str(e)}")
            print("=== WriterListFiles Execution Failed ===\n")
            raise e
        
        print("=== WriterListFiles Execution Complete ===\n") 
