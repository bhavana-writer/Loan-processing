import sys
import os
import logging
from fastapi import FastAPI, Request
import writer.serve
from dotenv import load_dotenv
from pathlib import Path

# ✅ Ensure actions are discoverable
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.append(str(PROJECT_ROOT))  # Make sure the app root is in sys.path

# Also add parent directory to path to find actions package
PARENT_DIR = PROJECT_ROOT.parent
sys.path.append(str(PARENT_DIR))

from actions.JSONToString import JSONToString
from actions.GongIntegration import GongIntegration
from actions.WriterQuestionToKG import WriterQuestionToKG
from actions.FileManagerBlock import FileManagerBlock
from actions.DelayBlock import DelayBlock
from actions.HTMLToMarkdown import HTMLToMarkdown
from actions.AirtableUpdater import AirtableUpdater
from actions.InstructorStructuredOutputBlock import InstructorStructuredOutputBlock
from actions.TavilyBlock import TavilyBlock
from actions.YFinanceBlock import YFinanceBlock
from actions.WebPageArticleExtractor import WebPageArticleExtractor
from actions.SlackCanvasBlock import SlackCanvasBlock
from actions.WriterPdfParser import WriterPdfParser
from actions.WriterListFiles import WriterListFiles




# Load environment variables
load_dotenv()


def register_actions():
    """Register custom actions dynamically"""
    JSONToString.register('workflows_jsontostring')
    GongIntegration.register('workflows_gongintegration')
    WriterQuestionToKG.register('workflows_writerquestiontokg')
    FileManagerBlock.register('workflows_filemanager')
    DelayBlock.register('workflows_delay')
    HTMLToMarkdown.register('workflows_htmltomarkdown')
    AirtableUpdater.register('workflows_airtableupdater')
    InstructorStructuredOutputBlock.register('workflows_instructorstructuredoutputblock')
    TavilyBlock.register('workflows_tavilyblock')
    YFinanceBlock.register('workflows_yfinanceblock')
    WebPageArticleExtractor.register('workflows_webpagearticleextractor')
    SlackCanvasBlock.register('workflows_slackcanvasblock')
    WriterPdfParser.register('workflows_writerpdfparser')
    WriterListFiles.register('workflows_writerlistfiles')

register_actions()


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# ✅ Access the FastAPI app provided by Writer
asgi_app: FastAPI = writer.serve.app

# ✅ Health Check
@asgi_app.get("/healthcheck")
async def health_check():
    return {"status": "ok"}

# Add your custom routes here
@asgi_app.get("/custom-route")
async def custom_route():
    return {"message": "Hello from custom route!"}
