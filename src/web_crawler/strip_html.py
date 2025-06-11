import os
from bs4 import BeautifulSoup

def clean_html_folder(html_folder_path, output_folder_path):
    """
    Processes all HTML files in a folder, extracts text content,
    and saves the cleaned text to the output folder.

    Args:
        html_folder_path (str): Path to the folder containing HTML files.
        output_folder_path (str): Path to the folder to save the cleaned text files.
    """
    os.makedirs(output_folder_path, exist_ok=True)

    # Get the list of HTML files in the folder
    html_files = [f for f in os.listdir(html_folder_path) if f.endswith('.html')]

    for html_file in html_files:
        html_file_path = os.path.join(html_folder_path, html_file)
        
        # Read the HTML content from the file
        with open(html_file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()

        # Use BeautifulSoup to parse the HTML content
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extract text content from the HTML
        text_content = soup.get_text(separator=' ', strip=True)

        # Remove extra whitespace and newlines
        text_content = ' '.join(text_content.split())

        # Define the output file path
        output_file_name = os.path.splitext(html_file)[0] + '.md'
        output_file_path = os.path.join(output_folder_path, output_file_name)

        # Write the cleaned text to the output file
        with open(output_file_path, 'w', encoding='utf-8') as file:
            file.write(text_content)

        print(f"Processed {html_file} and saved cleaned text to {output_file_name}")

if __name__ == "__main__":
    # Replace these paths with your actual folder paths
    html_folder = r"C:\workspace\SCAI\web_crawler\data\html_test"
    output_folder = r"C:\workspace\SCAI\web_crawler\data\stripped_htmls"

    clean_html_folder(html_folder, output_folder)