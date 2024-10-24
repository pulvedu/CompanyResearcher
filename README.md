# Company Researcher

## Project Description

The goal of company reasearcher is to automate the process of company research, 
providing a structured and efficient approach to gathering and summarizing information.

LLM's lack the ability to distinguish between multiple "small" companies that share the same name,
making it difficult to conduct focused research on such companies. CompanyResearcher is a collection
of agents that work together to get the most accurate and comprehensive information about a company.

## Implementation Details 

### Summary of Agents

- TavilySearch:
        - Conducts a general search using the Tavily API.
- AnalyzeSearch:
        - Analyzes the search results and brings a human in the loop to help determine if the search results are relevant to the company the user is researching.
- TavilyFocusedSearch:
        - Conducts a focused search using the Tavily API given the knownledge gained from the AnalyzeSearch agent using human in the loop.
- TavilyExtract:
        - Extracts raw content from the the search results returned by the TavilyFocusedSearch agent.
- GenerateFinalSummary: 
        - Generates a final summary of the findings.
- ConvertToPDF:
        - Converts the final summary into a PDF document.

### LangGraph

The workflow is managed using LangGraph, the LangChain StateGraph defines nodes for each task and 
edges/conditional edges to determine the flow based on the results of each task. The graph is compiled and executed
to automate the company research process, providing a structured and efficient approach to gathering
and summarizing information.

[alt text](https://github.com/[username]/[reponame]/blob/[branch]/image.jpg?raw=true)

## Installation

To set up the project locally, follow these steps:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/pulvedu/CompanyResearcher.git
   cd CompanyResearcher
   ```

2. **Create a virtual environment:**

   ```bash
   python3 -m venv venv_company_ressearch
   ```

3. **Activate the virtual environment:**

   - On macOS and Linux:

     ```bash
     source venv_company_ressearch/bin/activate
     ```

   - On Windows:

     ```bash
     .\venv_company_ressearch\Scripts\activate
     ```

4. **Install the required packages:**

   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Run the application:**

   ```bash
   python company_researcher.py 
   ```

2. **Access the features:**

   - Follow the on-screen instructions to perform various research tasks.
   - Use the command-line interface to input data and receive outputs.

## Configuration (API-KEYS

- You need to add API keys for both Tavily and OpenAI to a `.env` file in this repo
- Ensure that your environment variables are set up correctly. You can configure them in a `.env` file,
  which is ignored by version control as specified in the `.gitignore` file.
1. Create a `.env` in `/CompanyResearcher/.env`
2. In the file add on one line `TAVILY_API_KEY=<your-api-key>` and on another line `OPENAI_API_KEY=<your-api-key>`

## Contributing

We welcome contributions to enhance the functionality of Company Researcher. To contribute:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Commit your changes and push them to your fork.
4. Submit a pull request with a detailed description of your changes.

## Contact

For questions or feedback, please contact [Dustin Pulver](dusty.pulver28@gmail.com).
