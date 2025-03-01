# d = "I am a man"
# d = list(d)
# # print(','.join(d))


# import os
# import asyncio
# from openai import AsyncOpenAI
# from dotenv import load_dotenv
# from pathlib import Path


# # Load environment variables from .env file
# env_path = Path('.') / '.env'
# load_dotenv(dotenv_path=env_path)

# # Set up required environment variables
# openai_api_key = os.getenv('OPENAI_API_KEY')
# default_model = os.getenv('OPENAI_DEFAULT_MODEL')

# # Check if environment variables are set correctly
# if not openai_api_key or not default_model:
#     raise ValueError("Environment variables OPENAI_API_KEY or OPENAI_DEFAULT_MODEL are not set.")

# # Initialize OpenAI client
# openai = AsyncOpenAI(
#     api_key=openai_api_key
# )

# # Get valid NHS conditions
# valid_conditions = vars.nhs_conditions

# # ############### format_user_report
# def format_user_report(last_message, symptoms, age_group, duration, medications):

#     report = f"User message: {last_message}\n\n"
#     report += "Medical Information:\n"

#     if symptoms:
#         report += f"- Symptoms: {symptoms}\n"
#     if age_group:
#         report += f"- Age Group: {age_group}\n"
#     if duration:
#         report += f"- Duration: {duration}\n"
#     if medications:
#         report += f"- Current Medications: {medications}\n"
#     return report
# # #########################################################


# # ############### get_condition_from_chatgpt
# async def get_condition_from_chatgpt(report, valid_conditions):
#     prompt = f"""Based on the following user report, determine the most likely medical condition 
#     that matches conditions in the NHS database. Only suggest conditions that are listed in the 
#     NHS database.

#     User Report:
#     {report}

#     Valid NHS Conditions:
#     {', '.join(valid_conditions)}

#     Return only the most likely condition name in lowercase, exactly as it appears in the NHS database.
#     If you're not confident about the match, return 'uncertain'.
#     """

#     try:
#         response = await openai.chat.completions.create(
#             model=default_model,
#             messages=[
#                 {"role": "system", "content": "You are a medical condition matching assistant. Only suggest conditions from the NHS database."},
#                 {"role": "user", "content": prompt}
#             ],
#             temperature=0.3,  # Lower temperature for more focused responses
#             max_tokens=50     # We only need the condition name
#         )
        
#         condition = response.choices[0].message.content.strip().lower()
#         print(f"From '_get_cond...': {condition}")
#         return condition if condition in valid_conditions else "uncertain"
        
#     except Exception as e:
#         print(f"ChatGPT API error: {str(e)}")
#         condition = "uncertain"
#     return condition
# # #########################################################


# # OPENAI test
# async def main():
#     # User report
#     symptoms = 'headache'
#     age_group = 'teen'
#     duration = '4 weeks'
#     medications = 'none'
#     last_message = 'I have been having a splitting headache for the past 4 weeks now'

#     # Format user report
#     user_report = format_user_report(
#         last_message=last_message,
#         symptoms=symptoms, 
#         age_group=age_group,
#         duration=duration, 
#         medications=medications)
    
    
#     # Get condition match from ChatGPT
#     condition = await get_condition_from_chatgpt(user_report, valid_conditions)
    
#     if condition == "uncertain":
#         print(
#             text="I'm not completely certain about your condition based on the symptoms. "
#                     "It would be best to consult a healthcare professional for an accurate diagnosis. "
#                     "Would you like to know about some common conditions that might be related to your symptoms?"
#         )
        
#     else:
#         print(
#             f"Based on your symptoms, this might be related to {condition}. "
#             f"Would you like to learn more about {condition}?"
#         )
    
#     if __name__ == "__main__":
#         asyncio.run(main()) 