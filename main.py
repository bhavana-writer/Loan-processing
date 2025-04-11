import writer as wf
import writer.ai
import os
from dotenv import load_dotenv
from pathlib import Path
import importlib.util
import inspect
import json
import glob
import pandas as pd
import time
from writerai import Writer
import requests
import instructor
from pydantic import BaseModel, Field
from typing import List

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




# Welcome to Writer Framework! 
# This template is a starting point for your AI apps.
# More documentation is available at https://dev.writer.com/framework

# Load environment variables
load_dotenv(dotenv_path='config/.env.dev')  # Default to dev environment
os.environ["WRITER_API_KEY"] = os.getenv("WRITER_API_KEY", "")
os.environ["WRITER_SECRET_KEY"] = os.getenv("WRITER_SECRET_KEY", "")

# Enable Writer Framework features
wf.Config.feature_flags = [
    'workflows',
    'custom_block_icons', 
    'dataframeEditor'
]

# Register the action with other actions
def register_actions():
    """Register custom actions"""
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



# Create initial state with DataFrame
initial_state = {
    "my_app": {
        "title": f"{os.getenv('APP_NAME')}",
        "environment": os.getenv("ENV", "development")
    },
    "message_status": "Displaying PDF file from data directory",
    "File": {"Name": "polaris-10k.pdf", "file_path": "data/polaris-10k.pdf"},  # Initialize with default file
    "file_uploaded": True,  # Set to True initially
    "text_packed_file": wf.pack_file("data/polaris-10k.pdf", "application/pdf")  # Pack the file right in the initial state
}


# Initialize state
wf.init_state(initial_state)

# No additional code needed - the PDF viewer will automatically display the file defined in initial_state


