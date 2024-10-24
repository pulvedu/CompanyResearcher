from langchain_core.messages import AIMessage, HumanMessage
from openai import OpenAI
import os
import tiktoken
import re
from pdb import set_trace as bp

class GenerateFinalSummary:
    """
    The GenerateFinalSummary class is responsible for generating a final summary of the company based on the search results.

    *** note ***
    If you want to generate more detailed summaries, you will need to use a model that has a larger context window.
    The current model only has a context window of 16385 tokens and max token output of 4096 tokens. 
    This will limit the number of website extractions that can be added to the prompt as well as the amount of
    detial the model can provide in it's response.
    
    """
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo") # Use the appropriate model encoding

    def generate_answer(self, state):
        search_results = state.get("search_results", [])
        search_query = [message for message in state['messages'] if type(message) == HumanMessage][-1].content
        # Get the raw content of the search results
        extract = [result.metadata['raw_content'] for result in search_results if result.metadata['raw_content']] 
        # Calculate token count for the extract
        prompt = f"""Based on the following raw website content, provide a detailed summary of the company mentioned in the query: "{search_query}". 
        Please include the following sections in markdown format, ensure the company's name is included as markdown documnet title:
        
        # Company Name

        ## Company Summary
        Provide a brief overview of the company.

        ## Key Products
        List and describe the key products or services offered by the company.

        ## Market
        Describe the market in which the company competes, including any relevant competitors or industry trends.

        Here is an example output:
        Eample:
        # Nike

        ## Company Summary
        Nike is a global leader in the design, development, manufacturing, and marketing of footwear, apparel, equipment, and accessories.

        ## Key Products
        - Air Max: A line of shoes known for their air cushioning.
        - Nike Pro: Performance apparel designed for athletes.

        ## Market
        Nike competes in the global sportswear market, with key competitors including Adidas and Under Armour. 

        Now, using the format above, provide the summary for the company mentioned in the query.

        Search Results:"""
        
        extract_token_count = sum(len(self.tokenizer.encode(result)) for result in extract)
        # GPT-3.5 Turbo has a context window of 16385 tokens
        max_tokens = 16385
        completion_tokens = 4000 #  GPT-3.5 Turbo has a 4,096 max token output (round to be safe)
        available_tokens = max_tokens - completion_tokens

        extract_token_count = extract_token_count + len(self.tokenizer.encode(prompt))
        # Adjust extract size if necessary
        while extract_token_count > available_tokens:
            extract.pop()  # Remove the last item
            extract_token_count = sum(len(self.tokenizer.encode(result)) for result in extract)

        prompt = prompt + "\n" + "\n".join(extract)

        llm_response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that provides detailed and accurate summaries of a specific company based on search results."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=completion_tokens
        )
        
        answer = llm_response.choices[0].message.content

        print("Final Summary:")
        print(answer)

        # Extract company name from the response
        company_name_match = re.search(r"^# (.+)", answer, re.MULTILINE)
        company_name = company_name_match.group(1) if company_name_match else "Company"

        state['messages'].append(AIMessage(content=answer))
        state['company_name'] = company_name  # Save the company name in the state
        return state
