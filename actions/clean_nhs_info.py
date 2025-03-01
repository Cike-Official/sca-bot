# Description: Extract specific sections from NHS JSON data using JMESPath queries.

import jmespath
import re


def extract_nhs_data(json_data):
    """
    Extract specific sections from NHS JSON data using JMESPath queries.
    """
    queries = {
        'overview': "hasPart[?hasHealthAspect=='http://schema.org/OverviewHealthAspect'].hasPart[*].text",
        'symptoms': "hasPart[?hasHealthAspect=='http://schema.org/SymptomsHealthAspect'].hasPart[*].text",
        'treatments': "hasPart[?hasHealthAspect=='http://schema.org/TreatmentsHealthAspect'].hasPart[*].text",
        'diagnosis': "hasPart[?hasHealthAspect=='http://schema.org/MedicalHelpNonurgentHealthAspect'].hasPart[*].text",
        'self_care': "hasPart[?hasHealthAspect=='http://schema.org/SelfCareHealthAspect'].hasPart[*].text",
        'causes': "hasPart[?hasHealthAspect=='http://schema.org/TypesHealthAspect'].hasPart[*].text"
    }
    
    results = {}
    for section, query in queries.items():
        results[section] = jmespath.search(query, json_data)
    return results

def clean_text(text):
    """
    Clean HTML tags, links, and format text for chatbot presentation.
    """
    if not text:
        return ""
        
    if isinstance(text, str):
        # Remove HTML links while keeping the text
        text = re.sub(r'<a href="[^"]*">(.*?)</a>', r'\1', text)
        
        # Remove other HTML tags
        text = re.sub(r'</?[^>]+>', '', text)
        
        # Remove extra whitespace and normalize spacing
        text = re.sub(r'\s+', ' ', text)
        
        # Clean up bullet points
        text = text.replace('• ', '\n• ')
        
        # Remove any remaining HTML entities
        text = text.replace('&nbsp;', ' ')
        
        # Clean up extra spaces around punctuation
        text = re.sub(r'\s+([.,!?])', r'\1', text)
        
        # Remove multiple newlines
        text = re.sub(r'\n\s*\n', '\n', text)
        
        return text.strip()
        
    elif isinstance(text, dict):
        return clean_text(text.get('text', ''))
    elif isinstance(text, list):
        return '\n'.join(clean_text(item) for item in text if item)
    else:
        return str(text)

def format_results(results):
    """
    Format the extracted results for chatbot presentation.
    """
    formatted_output = ""
    for section, content in results.items():
        # Format section header
        section_title = section.replace('_', ' ').title()
        formatted_output += f"\n{section_title}\n{'='*len(section_title)}\n"
        
        if content:
            if isinstance(content, list):
                cleaned_content = [clean_text(item) for item in content if item]
                # Remove empty strings and join with appropriate spacing
                cleaned_content = [text for text in cleaned_content if text.strip()]
                formatted_output += '\n'.join(cleaned_content) + '\n'
        else:
            formatted_output += "No information available.\n"
            
    # Final cleanup of the whole text
    formatted_output = re.sub(r'\n\s*\n', '\n\n', formatted_output)
    return formatted_output.strip()

def main(json_data):
    # Extract the relevant information
    results = extract_nhs_data(json_data)
    formatted_output = format_results(results)
    
    # Print the results
    return formatted_output
    