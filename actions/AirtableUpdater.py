import logging
import requests
import os
from typing import Dict, Any
from writer.abstract import register_abstract_template
from writer.blocks.base_block import WorkflowBlock
from writer.ss_types import AbstractTemplate
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv(dotenv_path=Path(__file__).parent.parent / "config" / ".env.dev")

logger = logging.getLogger(__name__)

class AirtableUpdater(WorkflowBlock):
    """Updates records in Airtable with provided field values."""

    @classmethod
    def register(cls, type: str):
        """Register the block and define the fields for the visual tool."""
        super(AirtableUpdater, cls).register(type)
        register_abstract_template(type, AbstractTemplate(
            baseType="workflows_node",
            writer={
                "name": "Airtable Record Updater",
                "description": "Updates an Airtable record with provided field values.",
                "category": "Other",
                "fields": {
                    "base_id": {
                        "name": "Base ID",
                        "type": "Text",
                        "control": "Text",
                        "desc": "The Airtable Base ID",
                        "required": True,
                        "default": "appSdafB4RE4JDx6Q"
                    },
                    "table_id": {
                        "name": "Table ID",
                        "type": "Text",
                        "control": "Text",
                        "desc": "The Airtable Table ID",
                        "required": True,
                        "default": "tblQJKmcL6pLsVU7L"
                    },
                    "record_id": {
                        "name": "Record ID",
                        "type": "Text",
                        "control": "Text",
                        "desc": "The ID of the record to update",
                        "required": True
                    },
                    "fields": {
                        "name": "Fields",
                        "type": "Key-Value",
                        "default": {"Social Content": ""},
                        "validator": {
                            "type": "object",
                            "properties": {
                                "Social Content": {"type": "string"}
                            },
                            "additionalProperties": True
                        },
                        "desc": "Key-value pairs to update in Airtable. Must include 'Social Content' field."
                    }
                },
                "outs": {
                    "success": {
                        "name": "Success",
                        "description": "Record updated successfully",
                        "style": "success",
                    },
                    "error": {
                        "name": "Error",
                        "description": "Failed to update record",
                        "style": "error",
                    },
                },
            }
        ))

    def update_record(self, base_id: str, table_id: str, record_id: str, fields: Dict[str, Any]) -> dict:
        """Updates an Airtable record with the provided fields."""
        try:
            api_key = os.getenv('AIRTABLE_API_KEY')
            if not api_key:
                raise ValueError("AIRTABLE_API_KEY not found in environment variables")

            url = f"https://api.airtable.com/v0/{base_id}/{table_id}/{record_id}"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # Ensure fields is a dictionary
            if not isinstance(fields, dict):
                raise ValueError("Fields must be a dictionary of key-value pairs")
            
            # Prepare the payload
            payload = {"fields": fields}
            logger.info(f"Updating record {record_id} with fields: {fields}")
            
            response = requests.patch(url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Update successful: {result}")
            return {"success": True, "data": result}
            
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if hasattr(e, 'response') and e.response is not None:
                error_msg = f"{error_msg}: {e.response.text}"
            logger.error(f"Airtable API error: {error_msg}")
            return {"success": False, "error": error_msg}
        except Exception as e:
            logger.error(f"Error updating Airtable record: {e}")
            return {"success": False, "error": str(e)}

    def run(self):
        """Execute the block's workflow."""
        try:
            # Get required fields
            base_id = self._get_field("base_id", required=True)
            table_id = self._get_field("table_id", required=True)
            record_id = self._get_field("record_id", required=True)
            fields = self._get_field("fields", required=True)

            # Debug logging
            logger.info("=== AirtableUpdater Input ===")
            logger.info(f"Type of fields: {type(fields)}")
            logger.info(f"Raw fields value: {fields}")

            # Handle different input types
            if isinstance(fields, str):
                try:
                    # Try to parse if it's a JSON string
                    import json
                    fields = json.loads(fields)
                    logger.info("Successfully parsed JSON string to dict")
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON string: {e}")
                    # If it's a simple string, try to use it as the Social Content
                    fields = {"Social Content": fields}
                    logger.info("Using string value as Social Content")
            elif isinstance(fields, dict):
                logger.info("Fields is already a dictionary")
            else:
                logger.error(f"Unexpected fields type: {type(fields)}")
                raise ValueError(f"Fields must be a dictionary or JSON string, got {type(fields)}")

            # Ensure we have a valid dictionary
            if not isinstance(fields, dict):
                raise ValueError("Fields must be a dictionary of key-value pairs")

            # Ensure Social Content is present
            if "Social Content" not in fields:
                logger.warning("Social Content not found in fields, adding empty value")
                fields["Social Content"] = ""

            logger.info(f"Final fields to update: {fields}")

            # Update the record
            result = self.update_record(base_id, table_id, record_id, fields)
            
            if result["success"]:
                self.result = result["data"]
                self.outcome = "success"
            else:
                self.result = {"error": result["error"]}
                self.outcome = "error"

        except Exception as e:
            self.outcome = "error"
            logger.error(f"Error running AirtableUpdater: {e}")
            self.result = {"error": str(e)}
            raise e 