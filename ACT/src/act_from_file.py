import fitz  # PyMuPDF
from act import ACTNode, NodeType

sample_filepath = '../../raw_data/sample_reports/s1-2022 (1)/45698120_Talha Islam_assignsubmission_file/45698120.pdf'

import re

def clean_section_text(text):
    """Removes trailing numbers, extra whitespace, and trims the text."""

    # Remove trailing page numbers (modify the regex if needed)
    text = re.sub(r"\s+\d+$", "", text.strip())

    return text.strip()  # Remove leading and trailing whitespace

def extract_content_for_header(doc, headers, header_text):
    for i, (header, page_number) in enumerate(headers):
        if header == header_text:
            all_text = ""
            start_index = find_header_index_in_page(doc, page_number, header_text)

            # Find the end index (the position of the next header)
            if i < len(headers) - 1:
                next_header, next_page_number = headers[i + 1]

                for i in range(page_number, next_page_number + 1):
                    all_text += doc[i - 1].get_text("text") 

                end_index = find_header_in_text(all_text, next_header) 
            else:
                for i in range(page_number, len(doc) + 1):
                    all_text += doc[i - 1].get_text("text")
                end_index = None  # Handle the case of the last header 

            return extract_section_content(all_text, page_number, start_index, end_index)

    return None  # If the header is not found

def find_header_in_text(page_text, header_text):
    """Finds the index of the header within the page text."""
    return page_text.find(header_text)


def find_header_index_in_page(doc, page_number, header_text):
    """Finds the precise index of the header within the page text."""
    page = doc[page_number - 1]
    page_text = page.get_text()
    return page_text.find(header_text)

def extract_section_content(all_text, page_number, start_index, end_index):
    """Extracts the section content from the specified page."""
    if end_index:
        section_text = all_text[start_index:end_index] 
    else:
        section_text = all_text[start_index:]

    return clean_section_text(section_text)  # Apply cleaning

def split_into_paragraphs(text):
    """Splits the text into a list of paragraphs."""
    return text.split("\n \n") 


def build_act_tree(filepath: str):
    doc = fitz.open(filepath)

    root = ACTNode(0, "Root", NodeType.SECTION, None)  # Create the root node
    section_stack = [root]  # Keep track of the current section at each level

    section_id = 1  # Start with section ID 1
    subsection_counters = {}  # A dictionary to track subsection IDs at each level

    for entry in doc.get_toc():
        level, title, page_number = entry

        # Determine appropriate parent
        while level <= len(section_stack) - 1:
            section_stack.pop()  # Pop until we find the right parent level
        parent = section_stack[-1]

        # Create and append the node
        node = ACTNode(level, title, NodeType.SECTION, None, parent=parent, page=page_number)
        section_stack.append(node)

    # Prepare headers from toc_data
    headers = [(entry[1], entry[2]) for entry in doc.get_toc()]

    sections = {}
    for header in headers:
        sections[header[0]] = extract_content_for_header(doc, headers, header[0])

    # Content Association 
    for node in root.level_order_iter():  # Assuming your ACTNode supports iteration
        if node.nodeType in (NodeType.SECTION, NodeType.PARAGRAPH): 
            node.text = sections.get(node.name, "") 

    # # Content Association with Paragraphs 
    for node in root.level_order_iter():  
        if node.nodeType == NodeType.SECTION: 
            node.id = section_id  
            section_id += 1 

            subsection_id = subsection_counters.get(node.id, 0) + 1  # Get or initialize
            subsection_counters[node.id] = subsection_id # Update the counter

            if not node.children:
                paragraphs = split_into_paragraphs(node.text) 
                print(len(paragraphs), node.name)




                for paragraph_text in paragraphs:
                    paragraph_node = ACTNode(0, paragraph_text[:5], NodeType.PARAGRAPH, paragraph_text, parent=node)
                    paragraph_node.id = f"{node.id}.{subsection_id}"  
                    subsection_id += 1 


    return root


sample_act = build_act_tree(sample_filepath)
sample_act.print_tree()
sample_act.visualize_tree()

for node in sample_act.children[2].children[2].children:
    print(node.name, node.id, node.text)

# print(sample_act.children[0].text)