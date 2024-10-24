from langchain_core.messages import HumanMessage
from openai import OpenAI
import os
from utils.url_parser import group_urls


class AnalyzeSearch:
    """
    The AnalyzeSearch class is responsible for analyzing the search results and determining if the user 
    is satisfied with the results.It uses the OpenAI API to generate a summary of the search results and 
    prompts the user to confirm if the results are satisfactory.If the user is not satisfied, the search is reset.

    In some cases, search results will return multiple companies that are similar or have the same name.
    We introduce a human in the loop to help the agent determine the correct company from the search results.
    """
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    def analyze_search(self,state):
        search_results = state.get("search_results", [])
        search_query = [message for message in state['messages'] if type(message) == HumanMessage][-1].content
        # Group the search results by url to help group but similar companies into the same group for better summaries.
        result = group_urls([site.metadata['url'] for site in search_results])
        sort_results =  dict(sorted(result.items(), key=lambda item: len(item[1]), reverse=True))
        search_result_groups = [[result for result in search_results if result.metadata['url'] in group] for group in sort_results.values()]
        
        for search_result in search_result_groups:
            summary_prompt = f"""Provide a summary of the search results found for the user query "{search_query}".
            Search Results:
            {search_result}
            present the output as follows:
            Company Name: Company Summary
            """
            summary_response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a critical analyst tasked with providing a general summary of the company found in the search results"},
                    {"role": "user", "content": summary_prompt}
                ]
            )
            summary = summary_response.choices[0].message.content
            print("\n🔍 **Company Search Result**\n")
            print(f"📄 {summary}\n")

            # Prompt the user to confirm if the summary is for the correct company
            while True:
                user_input = input(
                    "\n🔍 Is this the company you were looking for?\n"
                    "➡️ Type 'yes' to generate a more detailed summary.\n"
                    "➡️ Type 'no' if this is not the correct company.\n"
                    "➡️ Type 'reset' to reset the search.\n"
                    "📝 Your answer: "
                )
                if user_input in ['yes', 'no']:
                    # Update the search results with the user's confirmation
                    # and add the summary to the result
                    for result in search_result:
                        result.metadata['relevance'] = user_input
                        result.metadata['summary'] = summary
                    break
                elif user_input == 'reset':
                    break
                else:
                    print("Invalid input. Please try again.")
            if user_input == 'yes' or user_input == 'reset':
                break

        # Check if all results were marked as irrelevant
        num_of_irrelevant_results = [result for result in search_results if result.metadata['relevance'] == 'no']
        # If all results were marked as irrelevant, prompt the user to try again with more details
        if len(num_of_irrelevant_results) == len(search_results):
            print("*************************************************************************************************************************")
            print("It seems none of the results matched the company you were looking for. Please try your search again and add more details.")
            print("*************************************************************************************************************************")
            state['messages'].append('tavily_search')  # Reset to the starting node
        # If the user input is reset, prompt the user to try again with more details
        elif user_input == 'reset':
            print('\n!!!! Please be more descriptive when entering the company you want to research !!!!\n')
            state['messages'].append('tavily_search')
        else:
            state['messages'].append('tavily_focused_search')

        return state
