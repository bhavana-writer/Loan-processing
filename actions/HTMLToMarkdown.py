import logging
import html2text
from writer.abstract import register_abstract_template
from writer.blocks.base_block import WorkflowBlock
from writer.ss_types import AbstractTemplate

logger = logging.getLogger(__name__)

class HTMLToMarkdown(WorkflowBlock):
    """Converts HTML input into Markdown format."""

    @classmethod
    def register(cls, type: str):
        """Register the block and define the fields for the visual tool."""
        super(HTMLToMarkdown, cls).register(type)
        register_abstract_template(type, AbstractTemplate(
            baseType="workflows_node",
            writer={
                "name": "HTML to Markdown Converter",
                "description": "Parses HTML input and converts it to Markdown format.",
                "category": "Other",
                "fields": {
                    "htmlInput": {
                        "name": "HTML Input",
                        "type": "Text",
                        "control": "Textarea",
                        "desc": "Enter the HTML content to convert into Markdown.",
                        "required": True
                    },
                },
                "outs": {
                    "success": {
                        "name": "Success",
                        "description": "Markdown conversion completed successfully.",
                        "style": "success",
                    },
                    "error": {
                        "name": "Error",
                        "description": "An error occurred during conversion.",
                        "style": "error",
                    },
                },
            }
        ))

    def convert_html_to_markdown(self, html_content: str) -> str:
        """Convert HTML content to Markdown."""
        try:
            markdown_converter = html2text.HTML2Text()
            markdown_converter.ignore_links = False  # Preserve links
            markdown_converter.ignore_images = False  # Preserve images
            markdown_converter.body_width = 0  # Prevent line wrapping
            markdown_output = markdown_converter.handle(html_content)
            return markdown_output
        except Exception as e:
            logger.error(f"Error converting HTML to Markdown: {e}")
            return f"Error: {str(e)}"

    def run(self):
        """Execute the block's workflow."""
        try:
            html_input = self._get_field("htmlInput", required=True)
            self.result = self.convert_html_to_markdown(html_input)
            self.outcome = "success" if "Error" not in self.result else "error"
        except Exception as e:
            self.outcome = "error"
            logger.error(f"Error running HTMLToMarkdown block: {e}")
            raise e
