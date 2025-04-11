from writer.abstract import register_abstract_template
from writer.blocks.base_block import WorkflowBlock
from writer.ss_types import AbstractTemplate
import requests
import base64
import os
import json

class AshbyIntegration(WorkflowBlock):
    @classmethod
    def register(cls, type: str):
        super(AshbyIntegration, cls).register(type)
        register_abstract_template(type, AbstractTemplate(
            baseType="workflows_node",
            writer={
                "name": "Ashby Integration",
                "icon": "person_search",
                "description": "Interact with Ashby ATS API",
                "category": "Other",
                "fields": {
                    "action": {
                        "name": "Action",
                        "type": "Text",
                        "desc": "Select the Ashby API action to perform",
                        "options": {
                            "application.info": "Get Application Info",
                            "application.list": "List Applications",
                            "applicationFeedback.list": "Get Application Feedback",
                            "candidate.info": "Get Candidate Info",
                            "candidate.list": "List Candidates",
                            "job.list": "List Jobs",
                            "interview.list": "List Interviews"
                        }
                    },
                    # Dynamic fields based on action
                    "application_id": {
                        "name": "Application ID",
                        "type": "Text",
                        "desc": "Required for application.info and applicationFeedback.list",
                        "required": False
                    },
                    "candidate_id": {
                        "name": "Candidate ID",
                        "type": "Text", 
                        "desc": "Required for candidate.info",
                        "required": False
                    },
                    "filters": {
                        "name": "Filters",
                        "type": "Object",
                        "control": "Textarea",
                        "desc": "JSON filters for list operations",
                        "default": "{}"
                    }
                },
                "outs": {
                    "success": {
                        "name": "Success",
                        "description": "API call succeeded",
                        "style": "success",
                    },
                    "error": {
                        "name": "Error",
                        "description": "API call failed",
                        "style": "error",
                    }
                }
            }
        ))

    def run(self):
        try:
            print("\nAshby Integration Block - Starting execution:")
            
            # Get required fields
            api_key = os.getenv("ASHBY_API_KEY")
            action = self._get_field("action", required=True)
            filters = self._get_field("filters", False, default_field_value="{}")
            print(f"Selected Action: {action}")
            print("✓ Required fields retrieved")

            if not api_key:
                raise Exception("ASHBY_API_KEY is not set in the environment variables")

            # Auth header
            auth_string = f"{api_key}:"
            auth_bytes = auth_string.encode("ascii")
            base64_auth = base64.b64encode(auth_bytes).decode("ascii")
            headers = {
                "Authorization": f"Basic {base64_auth}",
                "Content-Type": "application/json"
            }
            print("✓ Authentication headers prepared")

            # Build request based on action
            endpoint = f"https://api.ashbyhq.com/{action}"
            payload = {}
            print(f"\nPreparing API call to: {endpoint}")

            if action == "application.info":
                application_id = self._get_field("application_id", required=True)
                payload["applicationId"] = application_id
                print(f"Application ID: {application_id}")

            elif action == "applicationFeedback.list":
                application_id = self._get_field("application_id", required=True)
                payload["applicationId"] = application_id
                print(f"Application ID for feedback: {application_id}")

            elif action == "candidate.info":
                candidate_id = self._get_field("candidate_id", required=True)
                payload["candidateId"] = candidate_id
                print(f"Candidate ID: {candidate_id}")

            # Add any filters
            if filters:
                try:
                    filters_dict = json.loads(filters)
                    payload.update(filters_dict)
                    print(f"Applied filters: {filters_dict}")
                except json.JSONDecodeError as e:
                    print(f"❌ Invalid JSON in filters: {e}")
                    filters_dict = {}

            # Make API request
            print("\nMaking API request...")
            response = requests.post(
                endpoint,
                headers=headers,
                json=payload
            )
            print(f"Response Status Code: {response.status_code}")

            if response.status_code == 200:
                self.result = response.json()
                print("\n✓ API call successful")
                if isinstance(self.result, dict) and "results" in self.result:
                    print(f"Number of results: {len(self.result['results'])}")
                self.outcome = "success"
                print("\n✓ Ashby Block completed successfully")
            else:
                error_msg = response.text
                print(f"\n❌ API Error Response: {error_msg}")
                self.outcome = "error"
                raise Exception(f"Ashby API error: {response.text}")

        except Exception as e:
            error_msg = f"Ashby Block failed: {str(e)}"
            print(f"\n❌ {error_msg}")
            self.outcome = "error"
            raise e 
