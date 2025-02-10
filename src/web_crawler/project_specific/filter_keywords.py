import os
import shutil
import re

RELEVANT_KEYWORDS = [
    # General Project Terms
    'project', 'projects', 'research', 'researcher', 'innovation', 'innovative',
    'initiative', 'program', 'programme', 'collaboration', 'funding', 'grant',
    'consortium', 'partners', 'participants', 'beneficiaries', 'coordinator',
    'project duration', 'timeline', 'milestones', 'start date', 'end date',
    'status', 'ongoing', 'completed', 'upcoming',

    # Specific Project Components
    'work packages', 'deliverables', 'tasks', 'activities', 'methodology',
    'approach', 'results', 'findings', 'outcomes', 'impact', 'expected impact',
    'exploitation', 'dissemination', 'sustainability', 'innovation actions',
    'key performance indicators', 'KPIs', 'best practices', 'case studies',
    'proof of concept', 'feasibility study',

    # Collaboration and Consortium Details
    'coordinator', 'lead partner', 'beneficiaries', 'affiliated entities',
    'third parties', 'stakeholders', 'advisory board', 'steering committee',
    'partnership', 'membership', 'networking', 'collaborative efforts',
    'industry partners', 'academic partners',

    # Legal and Ethical
    'intellectual property', 'IPR', 'data management plan', 'ethics',
    'ethical considerations', 'compliance', 'regulation', 'policy',
    'legal framework', 'standards', 'guidelines', 'privacy', 'GDPR',

    # Website Navigation Terms (indicating project content)
    'about the project', 'project details', 'project information',
    'project description', 'project factsheet', 'project overview',
    'project summary', 'project objectives', 'project structure',
    'contact us', 'contact information', 'latest news', 'news and events',
    'announcements', 'blog', 'faq', 'frequently asked questions',
    'resources', 'downloads', 'gallery', 'team', 'consortium members',
    'partners and collaborators', 'related projects', 'acknowledgements',

    # Specific Sections and Documents
    'deliverable report', 'progress report', 'final report', 'abstract',
    'executive summary', 'consortium agreement', 'memorandum of understanding',
    'collaboration agreement', 'data sharing agreement', 'code of conduct',
    'risk management', 'quality assurance', 'project management',

    # International Collaboration
    'cross-border', 'transnational', 'international partners',
    'european union', 'EU', 'member states', 'associated countries',

    # Miscellaneous
    'call for proposals', 'proposal submission', 'evaluation criteria',
    'selection process', 'funding opportunities', 'open calls',
]

def is_relevant(text_content, keyword_list, threshold=8, min_length=500):
    """
    Determine if a text content is relevant based on keyword matching
    with case-insensitive matching, word boundaries, and a minimum length.

    Args:
        text_content (str): The text content to analyze.
        keyword_list (list): A list of keywords to search for.
        threshold (int): The minimum number of keywords that must be found.
        min_length (int): The minimum number of words required.

    Returns:
        bool: True if the content is relevant, False otherwise.
    """
    word_count = len(text_content.split())
    if word_count < min_length:
        return False  # Content is too short to be relevant

    keyword_count = 0
    for kw in keyword_list:
        # Use word boundaries and re.IGNORECASE for case-insensitive matching
        pattern = r'\b' + re.escape(kw) + r'\b'
        if re.search(pattern, text_content, flags=re.IGNORECASE):
            keyword_count += 1
    return keyword_count >= threshold

def keyword_filtering(input_folder, output_folder_relevant, output_folder_irrelevant):
    """
    Performs keyword filtering on text files to classify them as relevant or irrelevant.

    Args:
        input_folder (str): Path to the folder containing text files to filter.
        output_folder_relevant (str): Path to the folder to save relevant files.
        output_folder_irrelevant (str): Path to the folder to save irrelevant files.
    """
    os.makedirs(output_folder_relevant, exist_ok=True)
    os.makedirs(output_folder_irrelevant, exist_ok=True)

    relevant_count = 0
    irrelevant_count = 0
    total_files = 0

    # Process each text file in the input folder
    for text_file in os.listdir(input_folder):
        if text_file.endswith('.txt'):
            total_files += 1
            text_file_path = os.path.join(input_folder, text_file)
            try:
                with open(text_file_path, 'r', encoding='utf-8') as file:
                    text_content = file.read()
            except Exception as e:
                print(f"Error reading {text_file}: {e}")
                continue

            # Classify the content
            if is_relevant(text_content, RELEVANT_KEYWORDS, threshold=8, min_length=500):
                classification = '1'  # Relevant
                destination_folder = output_folder_relevant
                relevant_count += 1
                print(f"{text_file} is classified as RELEVANT.")
            else:
                classification = '0'  # Irrelevant
                destination_folder = output_folder_irrelevant
                irrelevant_count += 1
                print(f"{text_file} is classified as IRRELEVANT.")

            # Move the file to the appropriate folder
            try:
                shutil.move(text_file_path, os.path.join(destination_folder, text_file))
            except Exception as e:
                print(f"Error moving {text_file}: {e}")

    print("\nKeyword Filtering Completed.")
    print(f"Total files processed: {total_files}")
    print(f"Total relevant files: {relevant_count}")
    print(f"Total irrelevant files: {irrelevant_count}")

if __name__ == "__main__":
    input_folder = r"C:\workspace\SCAI\web_crawler\data\stripped_htmls"
    output_folder_relevant = r"C:\workspace\SCAI\web_crawler\data\filtered\relevant"
    output_folder_irrelevant = r"C:\workspace\SCAI\web_crawler\data\filtered\irrelevant"

    keyword_filtering(input_folder, output_folder_relevant, output_folder_irrelevant)