from langchain.schema import Document
from tavily import TavilyClient
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os
import logging  

load_dotenv()


class TavilySearch:
    """
    The TavilySearch class is responsible for conducting a search using the Tavily API.
    It interacts with the TavilyClient to retrieve search results based on user queries.
    """
    def __init__(self):
        self.tavily_client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

    def get_user_query(self):
        print("\n             🔍 COMPANY RESEARCHER 🔍")
        print("           POWERED BY TAVILY and LANGCHAIN")
        print("======================================================")
        user_query = input("\nPlease let us know what company you'd like to research: ")

        return user_query

    def search(self, state):
        search_results = []
        user_query = self.get_user_query()

        # Update the state with the user query
        state['messages'] = [HumanMessage(content=user_query)]
        while True:
            try:
                # Get the latest human message as the search query AKA the user query
                search_query = [message for message in state['messages'] if type(message) == HumanMessage][-1].content
                # Perform the search
                response = self.tavily_client.search(
                    search_query,
                    search_depth="advanced",
                    max_results=10  
                )
                search_results.extend([
                    Document(page_content=result["content"], metadata={
                        "url": result["url"],
                        "score": result["score"],
                        "relevance": '',
                        "summary": '',
                        "raw_content": ''
                    })
                    for result in response['results']
                ])

                state['search_results'] = search_results
                return state

            except Exception as e:
                logging.error("An error occurred during the search: %s", e)
                new_query = input("\n❗ Please try again, provide more detail on the company and avoid using abbreviations\n"
                                  "Query length may be too short. Min query length is 5 characters. ❗\n"
                                  "\nPlease let us know what company you'd like to research: ")
                state['messages'].append(HumanMessage(content=new_query))
