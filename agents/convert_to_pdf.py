import markdown2
import os
from langchain_core.messages import AIMessage
import re
from xhtml2pdf import pisa  # Import xhtml2pdf for HTML to PDF conversion

class ConvertToPDF:
    """
    The ConvertToPDF class is responsible for converting the final summary to a PDF.
    It uses the xhtml2pdf library to convert the markdown to a PDF.
    """
    def __init__(self, save_dir='pdfs'):
        self.save_dir = save_dir
        os.makedirs(self.save_dir, exist_ok=True)  # Ensure the save directory exists

    def convert(self, state):
        # Extract the markdown content from the last AI message
        markdown_content = [message.content for message in state['messages'] if type(message) == AIMessage][-1]
        
        # Convert markdown to HTML
        html_content = markdown2.markdown(markdown_content)
        
        # Use the company name from the state to name the PDF
        company_name_match = re.search(r"^# (.+)", markdown_content, re.MULTILINE)
        company_name = company_name_match.group(1) if company_name_match else "Company"
        output_path = self._get_unique_filename(company_name)
        
        # Convert HTML to PDF using xhtml2pdf
        self._convert_html_to_pdf(html_content, output_path)
        
        print(f"\n✅ PDF generated successfully: {output_path}")
        
        # Prompt the user to search for another company or end the workflow
        while True:
                user_input = input(
                "\n🔍 Would you like to search for another company?\n"
                "➡️ Type 'yes' to generate a more detailed summary.\n"
                "➡️ Type 'no' if this is not the correct company.\n"
                "📝 Your answer: ")
                if user_input in ['yes', 'no']:
                    break
                else:
                    print("Invalid input. Please try again.")
        if user_input == 'yes':
            state['messages'].append('search')  # Reset to the starting node
        else:
            state['messages'].append('end')

        return state

    def _convert_html_to_pdf(self, source_html, output_filename):
        # Convert HTML to PDF using xhtml2pdf
        with open(output_filename, "w+b") as result_file:
            pisa_status = pisa.CreatePDF(source_html, dest=result_file)
        return pisa_status.err

    def _get_unique_filename(self, base_name):
        # Generate a unique filename by appending a number if necessary
        base_path = os.path.join(self.save_dir, f"{base_name}.pdf")
        if not os.path.exists(base_path):
            return base_path
        
        counter = 2
        while True:
            new_path = os.path.join(self.save_dir, f"{base_name}_{counter}.pdf")
            if not os.path.exists(new_path):
                return new_path
            counter += 1
