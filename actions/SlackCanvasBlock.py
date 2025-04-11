import os
import json
import requests
import logging
from writer.blocks.base_block import WorkflowBlock
from writer.ss_types import AbstractTemplate
from writer.abstract import register_abstract_template

logger = logging.getLogger(__name__)

class SlackCanvasBlock(WorkflowBlock):
    """Creates a Slack canvas and sets access permissions for users or channels."""

    SLACK_API_BASE = "https://slack.com/api"

    @classmethod
    def register(cls, type: str):
        """Register the block and define the fields for the visual tool."""
        super(SlackCanvasBlock, cls).register(type)
        register_abstract_template(type, AbstractTemplate(
            baseType="workflows_node",
            writer={
                "name": "Slack Canvas Creator",
                "description": "Creates a Slack canvas and sets access permissions",
                "category": "Other",
                "fields": {
                    "title": {
                        "name": "Canvas Title",
                        "type": "Text",
                        "control": "Text",
                        "desc": "Title for the canvas",
                        "required": True
                    },
                    "content": {
                        "name": "Content",
                        "type": "Text",
                        "control": "Textarea",
                        "desc": ("Markdown content for the canvas. Supports headers (# to ###), bold, italic, lists, and links. "
                                "Note: Only heading levels 1-3 are supported (# to ###). Level 4+ headers (####) will be "
                                "automatically converted to level 3."),
                        "required": True
                    },
                    "access_level": {
                        "name": "Access Level",
                        "type": "Text",
                        "options": {
                            "read": "Read",
                            "write": "Write"
                        },
                        "default": "read",
                        "desc": "Access level for users/channels",
                        "required": True
                    },
                    "channel_ids": {
                        "name": "Channel IDs",
                        "type": "Text",
                        "control": "Text",
                        "desc": "Comma-separated channel IDs (e.g., C1234,C5678)",
                        "required": False
                    },
                    "user_ids": {
                        "name": "User IDs",
                        "type": "Text",
                        "control": "Text",
                        "desc": "Comma-separated user IDs (e.g., U1234,U5678)",
                        "required": False
                    },
                    "share_message": {
                        "name": "Share Message",
                        "type": "Text",
                        "control": "Textarea",
                        "desc": ("Message to accompany the canvas share. Supports Slack markdown formatting. "
                                "Default: 'New Canvas Shared 📝'"),
                        "required": False
                    },
                    "action_buttons": {
                        "name": "Action Buttons",
                        "type": "Text",
                        "control": "Textarea",
                        "desc": ("Add action buttons in JSON format. Example:\n"
                                '[{"id": "view_report", "label": "View Full Report"},\n'
                                ' {"id": "download", "label": "Download PDF"}]'),
                        "required": False
                    }
                },
                "outs": {
                    "success": {
                        "name": "Success",
                        "description": "Canvas created and shared successfully",
                        "style": "success",
                    },
                    "error": {
                        "name": "Error",
                        "description": "Failed to create or share canvas",
                        "style": "error",
                    },
                },
            }
        ))

    def _get_headers(self):
        """Get headers for Slack API requests."""
        token = os.getenv("SLACK_BOT_TOKEN")
        if not token:
            raise ValueError("SLACK_BOT_TOKEN environment variable not set")
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }

    def _convert_markdown_to_blocks(self, content: str) -> list:
        """Convert markdown content to Slack canvas blocks."""
        blocks = []
        sections = content.split('\n\n')
        
        for section in sections:
            if section.strip():
                if section.startswith('####'):
                    # Handle headers
                    blocks.append({
                        "type": "heading",
                        "heading": {
                            "type": "plain_text",
                            "text": section.replace('####', '').strip()
                        }
                    })
                else:
                    # Handle regular paragraphs
                    blocks.append({
                        "type": "rich_text",
                        "elements": [
                            {
                                "type": "rich_text_section",
                                "elements": self._parse_inline_elements(section)
                            }
                        ]
                    })
        return blocks

    def _parse_inline_elements(self, text: str) -> list:
        """Parse inline markdown elements into Slack format."""
        elements = []
        
        # Split text by emoji patterns
        parts = text.split()
        current_text = ""
        
        for part in parts:
            if part.startswith('#'):
                # Handle hashtags
                if current_text:
                    elements.append({"type": "text", "text": current_text.strip() + " "})
                    current_text = ""
                elements.append({
                    "type": "text",
                    "text": part + " ",
                    "style": {"bold": True}
                })
            elif '[link]' in part or '[insert link]' in part:
                # Handle link placeholders
                if current_text:
                    elements.append({"type": "text", "text": current_text.strip() + " "})
                    current_text = ""
                elements.append({
                    "type": "link",
                    "url": "https://example.com",  # Placeholder URL
                    "text": "Learn more"
                })
            else:
                current_text += part + " "
        
        if current_text:
            elements.append({"type": "text", "text": current_text.strip()})
        
        return elements

    def _fix_heading_levels(self, content: str) -> str:
        """Convert level 4 headings (####) to level 3 (###)."""
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            if line.startswith('####'):
                # Replace #### with ###
                fixed_lines.append(line.replace('####', '###'))
            else:
                fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)

    def create_canvas(self, title: str, content: str) -> str:
        """Create a new Slack canvas."""
        try:
            # Fix heading levels before creating canvas
            fixed_content = self._fix_heading_levels(content)
            
            payload = {
                "title": title,
                "document_content": {
                    "type": "markdown",
                    "markdown": fixed_content
                }
            }
            
            logger.info(f"Creating canvas with payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(
                f"{self.SLACK_API_BASE}/canvases.create",
                headers=self._get_headers(),
                json=payload
            )
            
            result = response.json()
            logger.info(f"Slack API response: {json.dumps(result, indent=2)}")
            
            if not response.ok:
                error_msg = (f"Slack API error: Status {response.status_code}, "
                            f"Error: {result.get('error', 'Unknown')}, "
                            f"Details: {result.get('error_details', 'No details')}")
                logger.error(error_msg)
                raise ValueError(error_msg)
                
            if not result.get("ok"):
                error_msg = (f"Slack API returned not ok: "
                            f"Error: {result.get('error', 'Unknown')}, "
                            f"Details: {result.get('error_details', 'No details')}")
                logger.error(error_msg)
                raise ValueError(error_msg)
                
            canvas_id = result.get("canvas_id")
            if not canvas_id:
                error_msg = f"No canvas ID in response: {json.dumps(result, indent=2)}"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
            logger.info(f"Successfully created canvas with ID: {canvas_id}")
            return canvas_id
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error creating canvas: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error creating canvas: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

    def share_canvas(self, canvas_id: str, channel_id: str = None, user_id: str = None):
        """Share canvas with channel or user."""
        try:
            workspace_url = os.getenv("SLACK_WORKSPACE_URL")
            team_id = os.getenv("SLACK_TEAM_ID")
            if not workspace_url or not team_id:
                raise ValueError("SLACK_WORKSPACE_URL and SLACK_TEAM_ID environment variables must be set")

            # Format the canvas URL correctly
            canvas_url = f"{workspace_url}/docs/{team_id}/{canvas_id}"
            
            # Get custom share message or use default
            share_message = self._get_field("share_message") or "*New Canvas Shared* :memo:"
            
            # Build message blocks
            blocks = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": share_message
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"<{canvas_url}|Click here to view the canvas>"
                    }
                }
            ]

            # Add action buttons if provided
            action_buttons_json = self._get_field("action_buttons")
            if action_buttons_json:
                try:
                    action_buttons = json.loads(action_buttons_json)
                    if action_buttons:
                        actions = []
                        for button in action_buttons:
                            actions.append({
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": button["label"],
                                    "emoji": True
                                },
                                "action_id": button["id"]
                            })
                        
                        blocks.append({
                            "type": "actions",
                            "elements": actions
                        })
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse action buttons JSON: {e}")
                except KeyError as e:
                    logger.warning(f"Invalid action button format: {e}")

            # Create message payload
            payload = {
                "channel": channel_id if channel_id else user_id,
                "blocks": blocks,
                "unfurl_links": True,
                "unfurl_media": True
            }

            response = requests.post(
                f"{self.SLACK_API_BASE}/chat.postMessage",
                headers=self._get_headers(),
                json=payload
            )
            
            result = response.json()
            logger.info(f"Share canvas response: {json.dumps(result, indent=2)}")
            
            if not response.ok:
                error_msg = (f"Slack API error: Status {response.status_code}, "
                            f"Error: {result.get('error', 'Unknown')}, "
                            f"Details: {result.get('error_details', 'No details')}")
                logger.error(error_msg)
                raise ValueError(error_msg)
                
            if not result.get("ok"):
                error_msg = (f"Slack API returned not ok: "
                            f"Error: {result.get('error', 'Unknown')}, "
                            f"Details: {result.get('error_details', 'No details')}")
                logger.error(error_msg)
                raise ValueError(error_msg)

            logger.info(f"Successfully shared canvas to {'channel' if channel_id else 'user'}")

        except Exception as e:
            error_msg = f"Error sharing canvas: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

    def set_access(self, canvas_id: str, access_level: str, channel_ids: str = None, user_ids: str = None):
        """Set access permissions for the canvas."""
        try:
            # Convert comma-separated strings to arrays
            channel_ids_array = [id.strip() for id in channel_ids.split(",")] if channel_ids else None
            user_ids_array = [id.strip() for id in user_ids.split(",")] if user_ids else None

            payload = {
                "canvas_id": canvas_id,
                "access_level": access_level
            }

            if channel_ids_array:
                payload["channel_ids"] = channel_ids_array
            if user_ids_array:
                payload["user_ids"] = user_ids_array

            logger.info(f"Setting access with payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(
                f"{self.SLACK_API_BASE}/canvases.access.set",
                headers=self._get_headers(),
                json=payload
            )
            
            result = response.json()
            logger.info(f"Slack API response: {json.dumps(result, indent=2)}")
            
            if not response.ok:
                error_msg = (f"Slack API error: Status {response.status_code}, "
                            f"Error: {result.get('error', 'Unknown')}, "
                            f"Details: {result.get('error_details', 'No details')}")
                logger.error(error_msg)
                raise ValueError(error_msg)
                
            if not result.get("ok"):
                error_msg = (f"Slack API returned not ok: "
                            f"Error: {result.get('error', 'Unknown')}, "
                            f"Details: {result.get('error_details', 'No details')}")
                logger.error(error_msg)
                raise ValueError(error_msg)

            logger.info("Successfully set canvas access")

        except requests.exceptions.RequestException as e:
            error_msg = f"Network error setting access: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error setting access: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

    def run(self):
        """Execute the block's workflow."""
        try:
            # Get required fields
            title = self._get_field("title", required=True)
            content = self._get_field("content", required=True)
            access_level = self._get_field("access_level", required=True)
            
            # Get optional fields
            channel_ids = self._get_field("channel_ids")
            user_ids = self._get_field("user_ids")

            if not channel_ids and not user_ids:
                raise ValueError("Either channel_ids or user_ids must be provided")

            # Create canvas
            canvas_id = self.create_canvas(title, content)

            # Share canvas with each channel/user
            if channel_ids:
                for channel_id in channel_ids.split(","):
                    self.share_canvas(canvas_id, channel_id=channel_id.strip())
            
            if user_ids:
                for user_id in user_ids.split(","):
                    self.share_canvas(canvas_id, user_id=user_id.strip())

            # Set access permissions with original comma-separated strings
            self.set_access(canvas_id, access_level, channel_ids, user_ids)

            self.result = {
                "canvas_id": canvas_id,
                "status": "Canvas created and shared successfully"
            }
            self.outcome = "success"

        except Exception as e:
            self.outcome = "error"
            self.result = {"error": str(e)}
            logger.error(f"Error in SlackCanvasBlock: {str(e)}") 