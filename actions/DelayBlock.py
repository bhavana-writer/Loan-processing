import time
import logging
from writer.blocks.base_block import WorkflowBlock
from writer.ss_types import AbstractTemplate
from writer.abstract import register_abstract_template

logger = logging.getLogger(__name__)

class DelayBlock(WorkflowBlock):
    """Block that introduces a delay in workflow execution."""

    @classmethod
    def register(cls, type: str):
        """Register the block and define its interface."""
        super(DelayBlock, cls).register(type)
        register_abstract_template(type, AbstractTemplate(
            baseType="workflows_node",
            writer={
                "name": "Delay",
                "description": "Pauses workflow execution for a specified duration",
                "category": "Other",
                "fields": {
                    "duration": {
                        "name": "Duration (seconds)",
                        "type": "Text",
                        "control": "Text",
                        "desc": "Duration to pause execution in seconds",
                        "required": True,
                        "default": 5
                    },
                    "max_duration": {
                        "name": "Maximum Duration (seconds)",
                        "type": "Text", 
                        "control": "Text",
                        "desc": "Maximum allowed delay duration in seconds",
                        "required": False,
                        "default": 300
                    }
                },
                "outs": {
                    "success": {
                        "name": "Success",
                        "description": "Delay completed successfully",
                        "style": "success"
                    },
                    "error": {
                        "name": "Error",
                        "description": "Error occurred during delay",
                        "style": "error"
                    }
                }
            }
        ))

    def run(self):
        """Execute the delay block."""
        try:
            # Get duration with validation
            duration = self._get_field("duration", required=True)
            max_duration = self._get_field("max_duration") or 300

            # Convert string inputs to numbers
            try:
                duration = float(duration)
                max_duration = float(max_duration)
            except (ValueError, TypeError):
                raise ValueError("Duration and max_duration must be valid numbers")

            # Validate duration
            if not isinstance(duration, (int, float)) or duration <= 0:
                raise ValueError("Duration must be a positive number")
            
            if duration > max_duration:
                raise ValueError(f"Duration ({duration}s) exceeds maximum allowed duration ({max_duration}s)")

            logger.info(f"Starting delay for {duration} seconds")
            time.sleep(duration)
            logger.info("Delay completed successfully")

            self.result = {
                "duration": duration,
                "status": "Delay completed successfully"
            }
            self.outcome = "success"

        except Exception as e:
            logger.error(f"Error in DelayBlock: {str(e)}")
            self.outcome = "error"
            self.result = {"error": str(e)} 