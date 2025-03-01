# Description: Main action file for custom action - action_get_nhs_info

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import actions.clean_nhs_info as nhs_info

import os
import re
import logging
import requests
from dotenv import load_dotenv as load_env_variables

# Load environment variables from .env file
load_env_variables()

# Set up logging
logger = logging.getLogger(__name__)

class ActionGetNHSinfo(Action):
    def name(self) -> Text:
        return "action_get_nhs_info"
    
    def __init__(self):
        # set up the base URL and headers for the NHS API
        self.base_url = os.getenv("NHS_API_BASE_URL")
        self.headers = {
            "Content-Type": "application/json",
            "apikey": os.getenv("NHS_API_KEY")
        }

        # Check if the API key is set
        if not self.headers["apikey"]:
            raise ValueError("NHS_API_KEY is missing in .env")

    def _convert_to_slug(self, condition: str) -> str:
        """Convert a health condition string to a URL-friendly slug."""
        if not condition:
            return None
        
        # Convert to lowercase and replace spaces with hyphens
        slug = condition.lower().strip()
        # Replace spaces and multiple spaces with a single hyphen
        slug = re.sub(r'\s+', '-', slug)
        # Remove any characters that aren't letters, numbers, or hyphens
        slug = re.sub(r'[^a-z0-9-]', '', slug)
        # Remove consecutive hyphens
        slug = re.sub(r'-+', '-', slug)
        # Remove leading/trailing hyphens
        slug = slug.strip('-')
        return slug

    def _fetch_nhs_data(self, condition_slug: str) -> Dict[str, Any]:
        """Synchronously fetch data from NHS API using the condition slug."""
        
        url = f"{self.base_url}conditions/{condition_slug}/"
        # print(f"Fetching NHS data from: {url}")
        
        # Make a GET request to the NHS API
        logger.info(f"Fetching NHS data from: {url}")
        response = requests.get(url, headers=self.headers, timeout=10)
        if response.status_code != 200:
            raise requests.RequestException(
                logger.error(f"Failed to fetch data for {condition_slug} (status: {response.status_code})")
            )
        return response.json()

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        # Get the condition from slot
        condition = tracker.get_slot("condition")
        logger.info(f"Logger:\nCondition slot value in nhs_info: {condition}\n")
        if not condition:
            dispatcher.utter_message(
                text=f"condition: {condition}"
            )
            return []

        # Convert condition to slug directly
        condition_slug = self._convert_to_slug(condition)
        if not condition_slug:
            dispatcher.utter_message(
                text="I couldn’t process the condition name. Please try again."
            )
            return []

        try:
            data = self._fetch_nhs_data(condition_slug)
            formatted_output = nhs_info.main(data)

            dispatcher.utter_message(
                text=f"Here's what I found about {condition}:\n{formatted_output}"
            )
            # dispatcher.utter_message(response="utter_ask_helpful")
            return []

        except requests.RequestException as e:
            if "404" in str(e):
                dispatcher.utter_message(
                    text=f"Sorry, I couldn’t find information about {condition} in the NHS database."
                )
            else:
                dispatcher.utter_message(
                    text=f"Sorry, I couldn’t fetch information about {condition} right now. "
                         f"Please try again later."
                )
            # print(f"Error fetching NHS data for {condition_slug}: {str(e)}")
            logger.exception(f"Error fetching NHS data for {condition_slug}: {str(e)}")
            return []
        
        except Exception as e:
            dispatcher.utter_message(
                text=f"An unexpected error occurred while fetching info about {condition}. "
                     f"Please try again."
            )
            # print(f"Unexpected error in ActionGetNHSinfo for {condition_slug}: {str(e)}")
            logger.exception(f"Unexpected error in ActionGetNHSinfo for {condition_slug}: {str(e)}")
            return []

















# from typing import Any, Text, Dict, List
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
# import aiohttp
# from rasa_sdk.events import SlotSet
# import actions.clean_nhs_info as nhs_info

# import os
# from dotenv import load_dotenv


# load_dotenv()


# class ActionGetNHSinfo(Action):
#     def name(self) -> Text:
#         return "action_get_nhs_info"
    
#     def __init__(self):
#         self.base_url = "https://int.api.service.nhs.uk/nhs-website-content/"
#         self.headers = {
#             "Content-Type": "application/json",
#             "apikey": os.getenv("NHS_API_KEY")
#         }



#     async def _fetch_nhs_data(self, condition: str) -> Dict[str, Any]:
#         """Asynchronously fetch data from NHS API."""
#         async with aiohttp.ClientSession() as session:
#             async with session.get(
#                 f"{self.base_url}conditions/{condition}",
#                 headers=self.headers
#             ) as response:
#                 if response.status != 200:
#                     raise aiohttp.ClientResponseError(
#                         response.request_info,
#                         response.history,
#                         status=response.status
#                     )
#                 return await response.json()

#     async def run(
#         self,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: Dict[str, Any],
#     ) -> List[Dict[str, Any]]:
#         # Get the condition from slot
#         condition = tracker.get_slot("condition")
#         if not condition:
#             dispatcher.utter_message(text="I don't knwo the health condition!")
#             return []

#         try:
#             # Fetch data asynchronously
#             data = await self._fetch_nhs_data(condition)

#             formatted_output = nhs_info.main(data)

#             # Construct response message
#             # overview = health_aspects.get("overview", "").split('.')[0] + '.'
#             # dispatcher.utter_message(
#             #     text=f"Here's what I found about {condition}: {overview}\n\n"
#             #          f"I've gathered information about symptoms, treatments, causes, "
#             #          f"and self-care. What specific aspect would you like to know about?"
#             # )

#             dispatcher.utter_message(text=formatted_output)
#             dispatcher.utter_message(template="utter_ask_helpful")
#             return []

#         except aiohttp.ClientError as e:
#             dispatcher.utter_message(
#                 text=f"Sorry, I couldn't fetch information about {condition}. "
#                      f"Please try again later."
#             )
#             # debug
#             print(f"\n\nError fetching NHS data for NHS info: {str(e)}\n\n")
#             return []
        




























# def __init__(self):
#     self.base_url = "https://int.api.service.nhs.uk/nhs-website-content/"
#     self.headers = {
#         "Content-Type": "application/json",
#         "apikey": os.getenv("NHS_API_KEY")
#     }
#     # Define health aspects we want to extract
#     self.target_aspects = {
#         "OverviewHealthAspect": "overview",
#         "SymptomsHealthAspect": "nhs_symptoms",
#         "TreatmentsHealthAspect": "treatments",
#         "CausesHealthAspect": "causes",
#         "SelfCareHealthAspect": "self_care",
#         "DiagnosisHealthAspect": "diagnosis"
#     }


# def _extract_health_aspect_content(self, data: Dict[str, Any], aspect: str) -> str:
#     """Extract content for a specific health aspect from the NHS API response."""
#     try:
#         # Find the relevant section in hasPart
#         for part in data.get("hasPart", []):
#             if part.get("hasHealthAspect", "").endswith(aspect):
#                 # Get the description if available
#                 if "description" in part:
#                     return part["description"]
                
#                 # Otherwise, try to extract from mainEntityOfPage
#                 for entity in part.get("mainEntityOfPage", []):
#                     if "text" in entity:
#                         # Remove HTML tags for clean text
#                         text = entity["text"]
#                         # Basic HTML tag removal (you might want to use BeautifulSoup for more complex HTML)
#                         text = text.replace("<p>", "").replace("</p>", "\n")
#                         text = text.replace("<ul>", "").replace("</ul>", "")
#                         text = text.replace("<li>", "- ").replace("</li>", "\n")
#                         return text.strip()
        
#         return "Information not available"
#     except Exception as e:
#         return f"Error extracting information: {str(e)}"
















# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa-pro/concepts/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []