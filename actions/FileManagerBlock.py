import os
import requests
import logging
import time
from writer.blocks.base_block import WorkflowBlock
from writer.ss_types import AbstractTemplate
from writer.abstract import register_abstract_template

logger = logging.getLogger(__name__)

class FileManagerBlock(WorkflowBlock):
    """Manages file operations (upload, retrieve, list, download) using the Writer API."""

    WRITER_API_BASE = "https://api.writer.com/v1"
    MAX_POLLING_ATTEMPTS = 30  # Maximum number of polling attempts
    POLLING_INTERVAL = 2  # Seconds between polling attempts

    @classmethod
    def register(cls, type: str):
        """Register the block and define the fields for the visual tool."""
        super(FileManagerBlock, cls).register(type)
        register_abstract_template(type, AbstractTemplate(
            baseType="workflows_node",
            writer={
                "name": "File Manager",
                "description": "Manages file operations using the Writer API",
                "category": "Other",
                "fields": {
                    "operation": {
                        "name": "Operation",
                        "type": "Text",
                        "options": {
                            "upload": "Upload File",
                            "retrieve": "Retrieve File",
                            "list": "List Files",
                            "download": "Download File"
                        },
                        "default": "upload",
                        "desc": "File operation to perform",
                        "required": True
                    },
                    "file_path": {
                        "name": "File Path",
                        "type": "Text",
                        "control": "Text",
                        "desc": "Path to the file (required for upload)",
                        "required": False
                    },
                    "file_id": {
                        "name": "File ID",
                        "type": "Text",
                        "control": "Text",
                        "desc": "File ID (required for retrieve/download)",
                        "required": False
                    },
                    "graph_id": {
                        "name": "Graph ID",
                        "type": "Text",
                        "control": "Text",
                        "desc": "Graph ID for filtering files",
                        "required": False
                    },
                    "status": {
                        "name": "Status Filter",
                        "type": "Text",
                        "options": {
                            "in_progress": "In Progress",
                            "completed": "Completed",
                            "failed": "Failed"
                        },
                        "desc": "Filter files by status",
                        "required": False
                    },
                    "limit": {
                        "name": "Limit",
                        "type": "Number",
                        "control": "Number",
                        "desc": "Maximum number of files to return (1-100)",
                        "required": False
                    },
                    "wait_for_processing": {
                        "name": "Wait for Processing",
                        "type": "Text",
                        "options": {
                            "true": "Yes",
                            "false": "No"
                        },
                        "default": "true",
                        "desc": "Wait for file processing to complete",
                        "required": False
                    },
                    "max_wait_time": {
                        "name": "Maximum Wait Time",
                        "type": "Number",
                        "control": "Number",
                        "desc": "Maximum time to wait for processing (seconds)",
                        "default": 60,
                        "required": False
                    }
                },
                "outs": {
                    "success": {
                        "name": "Success",
                        "description": "Operation completed successfully",
                        "style": "success"
                    },
                    "error": {
                        "name": "Error",
                        "description": "Operation failed",
                        "style": "error"
                    }
                }
            }
        ))

    def _get_headers(self):
        """Get headers for Writer API requests."""
        token = os.getenv("WRITER_API_KEY")
        if not token:
            raise ValueError("WRITER_API_KEY environment variable not set")
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }

    def upload_file(self, file_path, wait_for_processing=True, max_wait_time=60):
        """Upload a file to Writer and optionally wait for processing."""
        try:
            if not os.path.exists(file_path):
                raise ValueError(f"File not found: {file_path}")

            # Initial file upload
            filename = os.path.basename(file_path)
            mime_type = self._get_mime_type(filename)
            
            headers = self._get_headers()
            headers.update({
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Type": mime_type
            })

            with open(file_path, 'rb') as file:
                response = requests.post(
                    f"{self.WRITER_API_BASE}/files",
                    headers=headers,
                    data=file
                )

            self._check_response(response)
            result = response.json()
            file_id = result.get('id')

            if not wait_for_processing:
                return result

            # Poll for file processing completion
            attempts = min(max_wait_time // self.POLLING_INTERVAL, self.MAX_POLLING_ATTEMPTS)
            for attempt in range(attempts):
                file_status = self.retrieve_file(file_id)
                status = file_status.get('status', '').lower()
                
                logger.info(f"File {file_id} processing status: {status} (attempt {attempt + 1}/{attempts})")
                
                if status == 'completed':
                    logger.info(f"File {file_id} processing completed successfully")
                    return file_status
                elif status == 'failed':
                    error_msg = file_status.get('error', 'Unknown error')
                    logger.error(f"File {file_id} processing failed: {error_msg}")
                    raise ValueError(f"File processing failed: {error_msg}")
                elif status == 'in_progress':
                    logger.info(f"File {file_id} still processing, waiting {self.POLLING_INTERVAL} seconds...")
                    time.sleep(self.POLLING_INTERVAL)
                else:
                    logger.error(f"File {file_id} unknown status: {status}")
                    raise ValueError(f"Unknown file status: {status}")

            logger.error(f"File {file_id} processing timed out after {max_wait_time} seconds")
            raise ValueError(f"File processing timed out after {max_wait_time} seconds")

        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}")
            raise

    def retrieve_file(self, file_id):
        """Retrieve file metadata."""
        try:
            response = requests.get(
                f"{self.WRITER_API_BASE}/files/{file_id}",
                headers=self._get_headers()
            )
            self._check_response(response)
            return response.json()

        except Exception as e:
            logger.error(f"Error retrieving file: {str(e)}")
            raise

    def list_files(self, graph_id=None, status=None, limit=50):
        """List files with optional filters."""
        try:
            params = {
                "limit": min(max(1, limit), 100)
            }
            if graph_id:
                params["graph_id"] = graph_id
            if status:
                params["status"] = status

            response = requests.get(
                f"{self.WRITER_API_BASE}/files",
                headers=self._get_headers(),
                params=params
            )
            self._check_response(response)
            return response.json()

        except Exception as e:
            logger.error(f"Error listing files: {str(e)}")
            raise

    def download_file(self, file_id):
        """Download file content."""
        try:
            response = requests.get(
                f"{self.WRITER_API_BASE}/files/{file_id}/download",
                headers=self._get_headers()
            )
            self._check_response(response)
            return response.content

        except Exception as e:
            logger.error(f"Error downloading file: {str(e)}")
            raise

    def _get_mime_type(self, filename):
        """Get MIME type based on file extension."""
        ext = filename.lower().split('.')[-1]
        mime_types = {
            'txt': 'text/plain',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'pdf': 'application/pdf',
            'csv': 'text/csv',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'html': 'text/html'
        }
        return mime_types.get(ext, 'application/octet-stream')

    def _check_response(self, response):
        """Check response status and raise appropriate errors."""
        if not response.ok:
            error_msg = f"API error: {response.status_code}"
            try:
                error_data = response.json()
                error_msg = f"{error_msg} - {error_data.get('error', 'Unknown error')}"
            except:
                pass
            raise ValueError(error_msg)

    def run(self):
        """Execute the block's workflow."""
        try:
            operation = self._get_field("operation", required=True)
            
            if operation == "upload":
                file_path = self._get_field("file_path", required=True)
                wait_for_processing = self._get_field("wait_for_processing", "true") == "true"
                max_wait_time = int(self._get_field("max_wait_time") or 60)
                
                result = self.upload_file(
                    file_path, 
                    wait_for_processing=wait_for_processing,
                    max_wait_time=max_wait_time
                )
            
            elif operation == "retrieve":
                file_id = self._get_field("file_id", required=True)
                result = self.retrieve_file(file_id)
            
            elif operation == "list":
                graph_id = self._get_field("graph_id")
                status = self._get_field("status")
                limit = int(self._get_field("limit") or 50)
                result = self.list_files(graph_id, status, limit)
            
            elif operation == "download":
                file_id = self._get_field("file_id", required=True)
                result = self.download_file(file_id)
            
            else:
                raise ValueError(f"Invalid operation: {operation}")

            self.result = result
            self.outcome = "success"

        except Exception as e:
            self.outcome = "error"
            self.result = {"error": str(e)}
            logger.error(f"Error in FileManagerBlock: {str(e)}") 