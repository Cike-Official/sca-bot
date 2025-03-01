# # Description: This is used to match user symptoms to a medical condition in NHS DB using ChatGPT.



from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

import os
from openai import OpenAI  # Synchronous client
from mistralai import Mistral 

import logging
from dotenv import load_dotenv
from pathlib import Path
import actions.vars as vars

# Load environment variables from .env file
load_dotenv()

# Setup Logging
logger = logging.getLogger(__name__)

class ActionMatchSymptomsToCondition(Action):
    def name(self) -> Text:
        return "action_match_symptoms_to_condition"
    
    def __init__(self):

        # Load environment variables from .env file
        env_path = Path('.') / '.env'
        load_dotenv(dotenv_path=env_path)

        # Set up openai environment variables
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.openai_model = os.getenv('OPENAI_MODEL')
        if not self.openai_api_key or not self.openai_model:
            raise ValueError("Missing OPENAI_API_KEY or OPENAI_DEFAULT_MODEL in .env")
        
        # set up mistral environment variables
        self.mistral_api_key = os.getenv('MISTRAL_API_KEY')
        self.mistral_model = os.getenv('MISTRAL_MODEL')
        if not self.mistral_api_key or not self.mistral_model:
            raise ValueError("Missing MISTRAL_API_KEY or MISTRAL_MODEL in .env")
        
        # initialize OpenAI client
        self.openai = OpenAI(api_key=self.openai_api_key)

        # initialize Mistral client
        self.mistralai = Mistral(api_key=self.mistral_api_key)


    def _get_nhs_conditions(self) -> List[str]:
        # Get list of valid NHS conditions from database
        return vars.nhs_conditions

    def _format_user_report(self, tracker: Tracker) -> str:
        # Format user symptoms and context into a comprehensive report
        symptoms = tracker.get_slot("symptoms")
        age_group = tracker.get_slot("age_group")
        duration = tracker.get_slot("duration")
        medications = tracker.get_slot("medications")
        last_message = tracker.latest_message.get("text", "")
        report = f"User message: {last_message}\n\nMedical Information:\n"
        if symptoms:
            report += f"- Symptoms: {symptoms}\n"
        if age_group:
            report += f"- Age Group: {age_group}\n"
        if duration:
            report += f"- Duration: {duration}\n"
        if medications:
            report += f"- Current Medications: {medications}\n"
        return report
    
    def _get_condition_from_mistral(self, user_report: str, valid_conditions: List[str]) -> str:
        # Use ChatGPT to match symptoms to an NHS condition
        prompt = f"""Based on the following user report, determine the most likely medical condition 
that matches conditions in the NHS database. Only suggest conditions that are listed in the 
NHS database.

User Report:
{user_report}

Valid NHS Conditions:
{', '.join(valid_conditions)}

Return only the most likely condition name in lowercase, exactly as it appears in the NHS database.
If you're not confident about the match, return 'uncertain'."""
        
        try:
            response = self.mistralai.chat.complete(
                model=self.mistral_model,
                messages=[
                    {"role": "system", "content": "You are a medical condition matching assistant. Only suggest conditions from the NHS database."},
                    {"role": "user", "content": prompt}
                ],
            )
            
            condition = response.choices[0].message.content.strip().lower()
            return condition if condition in valid_conditions else "uncertain"
        except Exception as e:
            
            logger.error(f"Mistral API error: {str(e)}")
            return "uncertain"

#     def _get_condition_from_chatgpt(self, user_report: str, valid_conditions: List[str]) -> str:
#         # Use ChatGPT to match symptoms to an NHS condition
#         prompt = f"""Based on the following user report, determine the most likely medical condition 
# that matches conditions in the NHS database. Only suggest conditions that are listed in the 
# NHS database.

# User Report:
# {user_report}

# Valid NHS Conditions:
# {', '.join(valid_conditions)}

# Return only the most likely condition name in lowercase, exactly as it appears in the NHS database.
# If you're not confident about the match, return 'uncertain'."""
        
#         try:
#             response = self.openai.chat.completions.create(
#                 model=self.openai_model,
#                 messages=[
#                     {"role": "system", "content": "You are a medical condition matching assistant. Only suggest conditions from the NHS database."},
#                     {"role": "user", "content": prompt}
#                 ],
#                 temperature=0.3,
#                 max_tokens=50,
#                 timeout=20  # Synchronous timeout
#             )

#             # logger.info(f"\nGPT response: {response}\n")
            
#             condition = response.choices[0].message.content.strip().lower()
#             return condition if condition in valid_conditions else "uncertain"
        
#         except Exception as e:
#             logger.error(f"ChatGPT API error: {str(e)}")
#             return "uncertain"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        # Format user report
        user_report = self._format_user_report(tracker)
        logger.info(f'\nFormatted user report: {user_report}\n')

        # Get valid NHS conditions
        valid_conditions = self._get_nhs_conditions()
        
        try:
            condition = self._get_condition_from_mistral(user_report, valid_conditions)
            logger.info(f"Matched Condition (condition.py): {condition}\n")
            
            if condition == "uncertain":
                dispatcher.utter_message(
                    text="I'm not completely certain about your condition based on the symptoms. "
                         "It would be best to consult a healthcare professional for an accurate diagnosis."
                )
                return [SlotSet("condition", None)]
            
            dispatcher.utter_message(
                text=f"\nBased on your symptoms, this might be related to {condition}\n."
            )
            logger.info(f"Matched Condition (condition.py): {condition}\n")
            return [SlotSet("condition", condition)]
        
        except Exception as e:
            # error_msg = f"Error in run method (condition.py): {str(e)}"
            dispatcher.utter_message(
                text="I apologize, but I encountered an error while processing your symptoms. "
                     "Please try again or consult a healthcare professional."
            )
            logger.error(f"Error in run method (condition.py): {str(e)}")
            # logger.error(error_msg)
            return [SlotSet("condition", None)]

