import os
import json
import requests
from writer.blocks.base_block import WorkflowBlock
from writer.ss_types import AbstractTemplate
from writer.abstract import register_abstract_template

class WriterConfigurationError(Exception):
    """Raised when Writer API configuration is invalid."""
    pass

class TavilyBlock(WorkflowBlock):
    """Block for performing searches and content extraction using Tavily API."""
    
    TAVILY_API_URL = "https://api.tavily.com"
    
    @classmethod
    def register(cls, type: str):
        """Register the block and define the fields for the visual tool."""
        super(TavilyBlock, cls).register(type)
        register_abstract_template(type, AbstractTemplate(
            baseType="workflows_node",
            writer={
                "name": "Tavily Block",
                "description": "Performs searches and content extraction using Tavily API.",
                "category": "Other",
                "fields": {
                    "action_type": {
                        "name": "Action Type",
                        "type": "Text",
                        "options": {
                            "search": "Search",
                            "extract": "Extract Content"
                        },
                        "default": "search",
                        "validator": {
                            "type": "string",
                            "enum": ["search", "extract"]
                        },
                        "desc": "Choose between search or content extraction"
                    },
                    "query": {
                        "name": "Query/URLs",
                        "type": "Text",
                        "control": "Text",
                        "default": "",
                        "validator": {
                            "type": "string",
                            "minLength": 1
                        },
                        "desc": "Search query or URLs to extract (comma-separated for multiple URLs)"
                    },
                    "topic": {
                        "name": "Topic",
                        "type": "Text",
                        "options": {
                            "general": "General",
                            "news": "News"
                        },
                        "default": "general",
                        "validator": {
                            "type": "string",
                            "enum": ["general", "news"]
                        },
                        "desc": "Topic category for search"
                    },
                    "include_answer": {
                        "name": "Include Answer",
                        "type": "Text",
                        "options": {
                            "true": "Yes",
                            "false": "No"
                        },
                        "default": "false",
                        "validator": {
                            "type": "string",
                            "enum": ["true", "false"]
                        },
                        "desc": "Include an AI-generated answer in search results"
                    }
                },
                "outs": {
                    "success": {
                        "name": "Success",
                        "description": "The operation was successful.",
                        "style": "success",
                    },
                    "error": {
                        "name": "Error",
                        "description": "There was an error performing the operation.",
                        "style": "error",
                    },
                },
            }
        ))

    def _get_headers(self):
        """Get the headers for Tavily API requests."""
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise WriterConfigurationError("TAVILY_API_KEY environment variable not set")
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def search(self, query: str, topic: str = "general", include_answer: bool = False):
        """Perform a search using Tavily API."""
        try:
            payload = {
                "query": query,
                "topic": topic,
                "search_depth": "basic",
                "max_results": 5,
                "include_answer": include_answer,
                "include_raw_content": False,
                "include_images": False
            }
            
            response = requests.post(
                f"{self.TAVILY_API_URL}/search",
                json=payload,
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            raise WriterConfigurationError(f"Error performing search: {str(e)}")

    def extract(self, urls: str):
        """Extract content from URLs using Tavily API."""
        try:
            # Handle both single URL and comma-separated URLs
            url_list = [url.strip() for url in urls.split(",")]
            
            payload = {
                "urls": url_list if len(url_list) > 1 else url_list[0],
                "include_images": False,
                "extract_depth": "basic"
            }
            
            response = requests.post(
                f"{self.TAVILY_API_URL}/extract",
                json=payload,
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            raise WriterConfigurationError(f"Error extracting content: {str(e)}")

    def run(self):
        """Execute the block's workflow."""
        try:
            action_type = self._get_field("action_type", required=True)
            query = self._get_field("query", required=True)

            if action_type == "search":
                topic = self._get_field("topic", required=True)
                include_answer = self._get_field("include_answer", required=False)
                # Convert string "true"/"false" to boolean
                include_answer_bool = include_answer == "true" if include_answer else False
                self.result = self.search(query, topic, include_answer_bool)
                self.outcome = "success"
            elif action_type == "extract":
                self.result = self.extract(query)
                self.outcome = "success"
            else:
                raise WriterConfigurationError("Invalid action type selected.")

        except WriterConfigurationError as e:
            self.outcome = "error"
            self.result = {"error": str(e)}

        except Exception as e:
            self.outcome = "error"
            self.result = {"error": f"An unexpected error occurred: {str(e)}"} 