from typing import TypedDict, Sequence, Union, List
from typing import Annotated
from langgraph.graph.message import add_messages

class State(TypedDict):
    """
    The State class is used to store the state of the graph.
    messages: A list of messages used to store the states of the 
              workflow which dictate the flow of the graph. 
    search_results: A list of search results from the tavily search agent.
    """
    messages: Annotated[list, add_messages]
    search_results: List[str]


    
    