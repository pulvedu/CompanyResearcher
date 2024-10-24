from langgraph.graph import END, StateGraph
from agents.tavily_search import TavilySearch
from agents.tavily_focused_search import TavilyFocusedSearch
from agents.generate_final_summary import GenerateFinalSummary
from agents.tavily_extract import TavilyExtract
from agents.analyze_search import AnalyzeSearch
from utils.state import State
from agents.convert_to_pdf import ConvertToPDF
import logging
from IPython.display import Image

# Configure errorlogging
logging.basicConfig(
    filename='company_researcher_errors.log',
    level=logging.ERROR,   
    format='%(asctime)s - %(levelname)s - %(message)s'  
)

class CompanyResearcher:
    """
    The goal of company reasearcher is to automate the process of company research , 
    providing a structured and efficient approach to gathering and summarizing information.

    LLM's lack the ability to distinguish between multiple "small" companies that share the same name,
    making it difficult to conduct focused research on such companies. CompanyResearcher is a collection
    of agents that work together to get the most accurate and comprehensive information about a company.

    Summary of Agents:
    TavilySearch: 
        Conducts a general search using the Tavily API.
    AnalyzeSearch: 
        Analyzes the search results and brings a human in the loop to
        help determine if the search results are relevant to the company the user
        is researching.
    TavilyFocusedSearch: 
        Conducts a focused search using the Tavily API given the knownledge
        gained from the AnalyzeSearch agent using human in the loop.
    TavilyExtract: 
        Extracts raw content from the the search results returned by the TavilyFocusedSearch agent.
    GenerateFinalSummary: 
        Generates a final summary of the findings.
    ConvertToPDF: 
        Converts the final summary into a PDF document.

    The workflow is managed using a StateGraph, which defines nodes for each task and conditional
    edges to determine the flow based on the results of each task. The graph is compiled and executed
    to automate the company research process, providing a structured and efficient approach to gathering
    and summarizing information.
    """
    def __init__(self):
       # Initialize agents
        self.tavily_search = TavilySearch()
        self.analyze_search = AnalyzeSearch()
        self.tavily_focused_search = TavilyFocusedSearch()
        self.tavily_extract = TavilyExtract()
        self.generate_final_summary = GenerateFinalSummary()
        self.convert_to_pdf = ConvertToPDF()  

        # Define the LangGraph Graph
        self.workflow = StateGraph(State)
        self.workflow.add_node("tavily_search", self.tavily_search.search) 
        self.workflow.add_node("analyze_search", self.analyze_search.analyze_search)
        self.workflow.add_node("tavily_focused_search", self.tavily_focused_search.search)  
        self.workflow.add_node("tavily_extract", self.tavily_extract.extract)
        self.workflow.add_node("generate_final_summary", self.generate_final_summary.generate_answer)
        self.workflow.add_node("convert_to_pdf", self.convert_to_pdf.convert)  

        # Define the conditional edges
        self.workflow.add_conditional_edges("analyze_search",
                                            self.analyze_search_condition,
                                            {"tavily_focused_search": "tavily_focused_search",
                                            "tavily_search": "tavily_search"})
        self.workflow.add_conditional_edges("tavily_focused_search",
                                            self.tavily_focused_search_condition,
                                            {"tavily_extract": "tavily_extract",
                                            "tavily_search": "tavily_search"})
        self.workflow.add_conditional_edges("tavily_extract",
                                            self.tavily_extract_condition,
                                            {"generate_final_summary": "generate_final_summary",
                                             "tavily_search": "tavily_search"})
        self.workflow.add_conditional_edges("convert_to_pdf",
                                            self.convert_to_pdf_condition,
                                            {"end": END,
                                            "tavily_search": "tavily_search"})
        # Define the entry point
        self.workflow.set_entry_point("tavily_search")
        # Add edges to the graph
        self.workflow.add_edge("tavily_search", "analyze_search")
        self.workflow.add_edge("generate_final_summary", "convert_to_pdf") 
        self.workflow.add_edge("convert_to_pdf", END) 

        # Compile the graph
        self.company_researcher = self.workflow.compile()

    ##### Define the functions that determine the conditional edges #####
    
    # Analyize the search results and determine if we should do a focused search or not
    def analyze_search_condition(self,state):
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.content == "tavily_focused_search":
            return "tavily_focused_search"
        else:
            return "tavily_search"

    # Determine if we should extract or continue the search
    def tavily_focused_search_condition(self,state):

        messages = state["messages"]
        last_message = messages[-1]

        if last_message.content == "tavily_extract":
            return "tavily_extract"
        else:
            return "tavily_search"

    # Determine if we should generate the final summary or continue the search
    def tavily_extract_condition(self,state):
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.content == "tavily_search":
            return "tavily_search"
        else:
            return "generate_final_summary"
    
    # Determine if we should convert to pdf or continue the search
    def convert_to_pdf_condition(self,state):
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.content == "end":
            return "end"
        else:
            return "tavily_search"

    # Run the graph
    def run(self):
        return self.company_researcher.invoke({"messages":[], 
                                        "search_results": [],
                                        "llm_answers": []},
                                        config={"recursion_limit": 50})
    
    # Generate a diagram of the graph
    def generate_graph_diagram(self):
        im = Image(self.company_researcher.get_graph(xray=True).draw_mermaid_png())
        open('company_researcher_diagram.png', 'wb').write(im.data)

if __name__ == "__main__":
    response = CompanyResearcher()


