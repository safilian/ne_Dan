import json
from pathlib import Path
import re

from ACT.src.act import ACTTree, NodeType

# message_pattern = r"Message sent:\s*\[TextContentBlock\(text=Text\(annotations=\[\], value='(.+)'\), type='text'\]"
# response_pattern = r"Assistant Response:\s*(-.*)$"

message_pattern = r"Message sent:\s*\[TextContentBlock\(text=Text\(annotations=\[\], value='Paragraph:\\n(.+)'\), type='text'\)]"
response_pattern = r"Assistant Response:\s*(.+)$"


def extract_messages(log_file_path):
    messages = {}
    message, response = None, None
    with open(log_file_path, "r") as file:
        for line in file:
            response_match = re.search(response_pattern, line, flags=re.DOTALL)
            message_match = re.search(message_pattern, line, flags=re.DOTALL)

            if message_match:
                message = message_match.group(1).replace("\\n", "\n")
            if response_match:
                response = response_match.group(1)
            if message and response:
                messages[message[:20]] = response
                message, response = None, None  # Reset

    return messages


# Example Usage
log_file = "logs/app.log"
extracted_messages = extract_messages(log_file)

# for message_dict in extracted_messages:
#     print("Message Sent:", message_dict["message"])
#     print("Assistant Response:", message_dict["response"])
#     print("------")

act_tree = ACTTree(Path("data/processed/act/45698120.json"))
for node in act_tree.root.post_order_iter():
    if node.nodeType == NodeType.PARAGRAPH:
        node.goal = extracted_messages.get(node.text[:20])
        if not node.goal:
            print(f"Goal not found for paragraph: {node.text[:100]}, {node.id}")
    if node.nodeType == NodeType.TITLE:
        node.goal = node.text
    elif node.nodeType == NodeType.SECTION:
        union_goal = ""
        for child in node.children:
            if child.goal:
                union_goal += child.goal + "\n"
        node.goal = union_goal
act_tree.export_json(Path("data/processed/act/45698120_with_goals.json"))
# print(extracted_messages)
