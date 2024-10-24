from tavily import TavilyClient
from dotenv import load_dotenv
import os
import logging

load_dotenv()

class TavilyExtract:
    """
    The TavilyExtract class is responsible for extracting content from the search results.
    It interacts with the TavilyClient to retrieve the raw content of the search results.
    """
    def __init__(self):
        self.tavily_client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

    def extract(self, state):
        search_results = state.get("search_results", [])
        urls = [site.metadata['url'] for site in search_results][:5]
        try:
            response = self.tavily_client.extract(urls=urls)

        except Exception as e:
            logging.error("An error occurred during tavily extraction: %s", e)
            print("❗An error occurred during tavily extraction, Sorry for the inconvenience❗")
            # If this happens, reset the search and bring the user back to the beginning of the workflow.
            state['messages'].append('tavily_search')  
 
            return state
        
        for web_site in response['results']:
            for result in search_results:
                if result.metadata['url'] == web_site['url']:
                    result.metadata['raw_content'] = web_site['raw_content']
        state['messages'].append('generate_final_summary')
        return state
