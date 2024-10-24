from langchain.schema import Document
from langchain_core.messages import HumanMessage
from tavily import TavilyClient
from dotenv import load_dotenv
import os
import re
import logging

load_dotenv()

class TavilyFocusedSearch:
    '''
    The TavilyFocusedSearch class is responsible for conducting a focused search using the Tavily API.
    It interacts with the TavilyClient to retrieve search results based on user queries.
    '''
    def __init__(self):
        self.tavily_client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

    def parse_search_summary(self,relevant_company):
        '''
        This method is used to clean the summary of the relevant company.
        It removes the line with "Company Name", the sentences with links, and the "Company Summary:" text.
        It then joins the first two sentences of the cleaned text and returns the result.
        * If links are present in the query, this may result in an error from TavilySearch.
        * If the query is too long, this may result in an error from TavilySearch.
        '''
        cleaned_text = re.sub(r"Company Name:.*\n", "", relevant_company)  # Remove the line with "Company Name"
        cleaned_text = re.sub(r"\b\S+\.(com|org|net|gov|edu|io)\S*\b.*", "", cleaned_text)  # Remove sentences with links
        cleaned_text = cleaned_text.replace('Company Summary:', '')
        cleaned_text = cleaned_text.replace('\n', '')
        combined_string = ".".join(cleaned_text.split('.')[:2])
        return combined_string
        
    def search(self, state):
        search_results = state.get("search_results", [])
        search_query = [message for message in state['messages'] if type(message) == HumanMessage][-1].content
        # Get the list of domains to exclude from the search, human in the loop labeled the irrelevant results
        # thus we know the user is not interested in these results.
        exclude_domains = [result.metadata['url'] for result in search_results if result.metadata['relevance'] == 'no']
        # Get the summary of the relevant company, human in the loop confirmed this is the correct company
        relevant_company = [result.metadata['summary'] for result in search_results if result.metadata['relevance'] == 'yes'][0]
        # Clean the summary of the relevant company
        relevant_company = self.parse_search_summary(relevant_company)
        # Append the relevant company to the search query
        search_query += f". {relevant_company}."
        try:
            response = self.tavily_client.search(search_query, search_depth="advanced", max_results=10, exclude_domains=exclude_domains)
            state['messages'].append('tavily_extract')
            state['search_results'] = []
        except Exception as e:
            logging.error("An error occurred during tavily focused search: %s", e)
            print("❗An error occurred during a focused search, Sorry for the inconvenience❗")
            # In some cases, the search query may cause an error from TavilySearch.
            # If this happens, reset the search and bring the user back to the beginning of the workflow.
            state['messages'].append('tavily_search')
            state['search_results'] = []

            return state

        search_results = [
                Document(page_content=result["content"], metadata={"url": result["url"],
                                                                   "score": result["score"],
                                                                   "relevance":'',
                                                                   "summary":'',
                                                                   "raw_content":''})
                for result in response['results']]
      
        state['search_results'] = search_results

        return state
