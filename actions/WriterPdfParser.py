from writer.abstract import register_abstract_template
from writer.blocks.base_block import WorkflowBlock
from writer.ss_types import AbstractTemplate


class WriterPdfParser(WorkflowBlock):
    @classmethod
    def register(cls, type: str):
        super(WriterPdfParser, cls).register(type)
        register_abstract_template(type, AbstractTemplate(
            baseType="workflows_node",
            writer={
                "name": "PDF Parser",
                "description": "Parse PDF files into text or markdown format.",
                "category": "Writer",
                "fields": {
                    "fileId": {
                        "name": "File ID",
                        "type": "Text",
                        "desc": "The unique identifier of the PDF file to parse.",
                        "validator": {
                            "type": "string",
                        },
                    },
                    "format": {
                        "name": "Output Format",
                        "type": "Text",
                        "desc": "The format to convert the PDF content into.",
                        "default": "text",
                        "options": {
                            "text": "Text",
                            "markdown": "Markdown"
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
            
            print("\n=== WriterPDFParser Execution Start ===")
            
            # Get file ID and format
            file_id = self._get_field("fileId", required=True)
            output_format = self._get_field("format", default_field_value="text")
            print(f"[WriterPDFParser] Processing file ID: {file_id}")
            print(f"[WriterPDFParser] Output format: {output_format}")
            
            print("[WriterPDFParser] Parsing PDF...")
            response = writer.ai.Tools.parse_pdf(
                file_id_or_file=file_id,
                format=output_format
            )
            print(f"[WriterPDFParser] Parsing complete, content length: {len(response)}")
            
            self.result = {
                "content": response,
                "format": output_format
            }
            self.outcome = "success"
            print("[WriterPDFParser] Execution completed successfully")
            
        except BaseException as e:
            self.outcome = "error"
            print(f"[WriterPDFParser] Error occurred: {str(e)}")
            print("=== WriterPDFParser Execution Failed ===\n")
            raise e
        
        print("=== WriterPDFParser Execution Complete ===\n") 
