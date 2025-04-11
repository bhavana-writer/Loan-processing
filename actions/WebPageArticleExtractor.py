import requests
from bs4 import BeautifulSoup
import logging
from writer.abstract import register_abstract_template
from writer.blocks.base_block import WorkflowBlock
from writer.ss_types import AbstractTemplate

logger = logging.getLogger(__name__)

class WebPageArticleExtractor(WorkflowBlock):
    """Extracts the title and main article text from a webpage using BeautifulSoup."""

    @classmethod
    def register(cls, type: str):
        """Register the block and define the fields for the visual tool."""
        super(WebPageArticleExtractor, cls).register(type)
        register_abstract_template(type, AbstractTemplate(
            baseType="workflows_node",
            writer={
                "name": "Web Page Article Extractor",
                "description": "Fetches a webpage and extracts the article content.",
                "category": "Other",
                "fields": {
                    "url": {
                        "name": "Website URL",
                        "type": "Text",
                        "control": "Text",
                        "desc": "Enter the URL of the article to extract.",
                        "required": True
                    },
                },
                "outs": {
                    "success": {
                        "name": "Success",
                        "description": "Extracted article data successfully.",
                        "style": "success",
                    },
                    "error": {
                        "name": "Error",
                        "description": "An error occurred during extraction.",
                        "style": "error",
                    },
                },
            }
        ))

    def extract_article(self, url: str) -> dict:
        """Fetches a webpage and extracts the title and article content."""
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers)

            if response.status_code != 200:
                raise Exception(f"Failed to fetch page. Status code: {response.status_code}")

            soup = BeautifulSoup(response.text, "html.parser")

            # Extract the title
            title = soup.find("title").text.strip() if soup.find("title") else "No Title Found"

            # Extract article text (from <p> tags)
            article_sections = soup.find_all("p")
            article_text = "\n\n".join([p.text.strip() for p in article_sections if p.text.strip()])

            return {"title": title, "article": article_text}
        except Exception as e:
            logger.error(f"Error extracting article: {e}")
            return {"error": str(e)}

    def run(self):
        """Execute the block's workflow."""
        try:
            url = self._get_field("url", required=True)
            self.result = self.extract_article(url)
            self.outcome = "success" if "error" not in self.result else "error"
        except Exception as e:
            self.outcome = "error"
            logger.error(f"Error running WebPageArticleExtractor: {e}")
            raise e  # Re-raise for debugging
