from writer.abstract import register_abstract_template
from writer.blocks.base_block import WorkflowBlock
from writer.ss_types import AbstractTemplate
from pydantic import BaseModel
from typing import List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simplified response models
class Source(BaseModel):
    file_id: str
    snippet: str

class SimpleKGResponse(BaseModel):
    answer: str
    sources: List[Source]

class WriterQuestionToKG(WorkflowBlock):
    @classmethod
    def register(cls, type: str):
        super(WriterQuestionToKG, cls).register(type)
        register_abstract_template(type, AbstractTemplate(
            baseType="workflows_node",
            writer={
                "name": "Question Knowledge Graph",
                "description": "Ask a question to the knowledge graph.",
                "category": "Writer",
                "fields": {
                    "graphId": {
                        "name": "Graph ids",
                        "type": "Text",
                        "desc": "The ids for existing knowledge graphs. For multiple graphs, provide comma-separated UUIDs (e.g., 123e4567-e89b-12d3-a456-426614174000, 550e8400-e29b-41d4-a716-446655440000)",
                        "validator": {
                            "type": "string",
                        },
                    },
                    "question": {
                        "name": "Question",
                        "type": "Text",
                        "desc": "The question to ask the knowledge graph.",
                    },
                    "subqueries": {
                        "name": "Subqueries",
                        "type": "Text",
                        "desc": "Specify whether to include subqueries.",
                        "default": "no",
                        "options": {
                            "yes": "Yes",
                            "no": "No"
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
            logger.info("Starting Knowledge Graph question processing")
            
            import writer.ai
            graph_ids_str = self._get_field("graphId", required=True)
            graph_ids = [id.strip() for id in graph_ids_str.split(',')]
            question = self._get_field("question", required=True)
            
            logger.info(f"Processing question for graph IDs: {graph_ids}")
            logger.info(f"Question: {question}")

            client = writer.ai.WriterAIManager.acquire_client()
            response = client.graphs.question(
                graph_ids=graph_ids,
                question=question,
                stream=False,
                subqueries=False  # Simplified to not handle subqueries
            )

            # Create simplified response
            simple_response = SimpleKGResponse(
                answer=response.answer,
                sources=[Source(
                    file_id=getattr(s, 'file_id', 'unknown'),
                    snippet=getattr(s, 'snippet', '')
                ) for s in response.sources]
            )

            logger.info("Successfully processed question")
            logger.debug(f"Response: {simple_response.model_dump()}")

            self.result = simple_response.model_dump()
            self.outcome = "success"

        except Exception as e:
            logger.error(f"Error processing question: {str(e)}", exc_info=True)
            self.outcome = "error"
            # Return a simplified error response
            self.result = {
                "answer": f"Error: {str(e)}",
                "sources": []
            }
            raise e
