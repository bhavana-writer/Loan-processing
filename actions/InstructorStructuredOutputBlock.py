import os
import json
from typing import Type
from pydantic import BaseModel, create_model
from dotenv import load_dotenv
from writer.blocks.base_block import WorkflowBlock
from writer.ss_types import AbstractTemplate
import instructor
from writerai import Writer
from writer.abstract import register_abstract_template

# Load environment variables from the correct path
load_dotenv()

class WriterConfigurationError(Exception):
    """Raised when Writer API configuration is invalid."""
    pass

class InstructorStructuredOutputBlock(WorkflowBlock):
    """Block for extracting structured data using Instructor and Writer API."""

    @classmethod
    def register(cls, type: str):
        """Register the block and define the fields for the visual tool."""
        super(InstructorStructuredOutputBlock, cls).register(type)
        register_abstract_template(type, AbstractTemplate(
            baseType="workflows_node",
            writer={
                "name": "Writer Structured Output",
                "description": "Extracts structured data using Instructor and Writer API.",
                "category": "Other",
                "fields": {
                    "system_message": {
                        "name": "System Message",
                        "type": "Text",
                        "control": "Textarea",
                        "default": "",
                        "validator": {
                            "type": "string",
                        }
                    },
                    "user_message": {
                        "name": "User Message",
                        "type": "Text",
                        "control": "Textarea",
                        "default": "",
                        "validator": {
                            "type": "string",
                        }
                    },
                    "output_structure": {
                        "name": "Output Structure",
                        "type": "Key-Value",
                        "default": "{}",
                        "validator": {
                            "type": "object",
                        }
                    },
                    "stream": {
                        "name": "Stream",
                        "type": "Text",
                        "desc": "Specify whether to stream the response.",
                        "default": "no",
                        "options": {
                            "yes": "Yes",
                            "no": "No"
                        }
                    },
                },
                "outs": {
                    "success": {
                        "name": "Success",
                        "description": "The structured data was successfully extracted.",
                        "style": "success",
                    },
                    "error": {
                        "name": "Error",
                        "description": "There was an error during the extraction process.",
                        "style": "error",
                    },
                },
            }
        ))

    def extract_data(self, system_message: str, user_message: str, output_structure: dict, api_key: str) -> dict:
        """Extract structured data from the input text using Instructor and Writer."""
        try:
            # Initialize the Writer client dynamically at runtime
            if not api_key:
                raise WriterConfigurationError("Writer API key not found. Please add WRITER_API_KEY to your environment variables.")
            
            writer_client = Writer(api_key=api_key)
            client = instructor.from_writer(writer_client)

            # Convert string values to proper type annotations
            typed_structure = {
                field_name: (str, ...) for field_name, field_value in output_structure.items()
            }

            # Create a dynamic Pydantic model with proper type annotations
            dynamic_model = create_model('DynamicModel', **typed_structure)

            # Make the call to Writer's completions API with the provided input
            response = client.chat.completions.create(
                model="palmyra-x-004",  # Specify the model to use for extraction
                response_model=dynamic_model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ]
            )
            
            # Convert the response into a JSON object and return it
            return response.dict()
        except Exception as e:
            self.outcome = "error"
            self.result = {"error": str(e)}
            return self.result

    def run(self):
        """Execute the block's workflow."""
        try:
            # Get the system and user messages and output structure from the fields
            system_message = self._get_field("system_message", required=True)
            user_message = self._get_field("user_message", required=True)
            output_structure = self._get_field("output_structure", required=True)
            stream = self._get_field("stream", default_field_value="no") == "yes"
            
            # Get the API key from environment variables at runtime
            api_key = os.getenv("WRITER_API_KEY")

            # Parse the output structure (Key-Value pair) into a dictionary
            output_structure_dict = json.loads(output_structure)

            # Extract structured data using the provided system message, user message, output structure, and api_key
            self.result = self.extract_data(system_message, user_message, output_structure_dict, api_key)
            self.outcome = "success" if "error" not in self.result else "error"

        except Exception as e:
            self.outcome = "error"
            raise e  # Re-raise the exception to match WriterQuestionToKG pattern
