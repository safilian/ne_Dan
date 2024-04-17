from enum import Enum
import fitz  # PyMuPDF
from anytree import NodeMixin, RenderTree
from anytree.iterators.levelorderiter import LevelOrderIter
from anytree.iterators.postorderiter import PostOrderIter
from anytree.render import AsciiStyle
from json import JSONEncoder

from .pdf_utls import extract_content_for_header, split_into_paragraphs, is_title
from .assistant import ACT_Assistant


class NodeTypeEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, NodeType):
            return obj.value
        return super().default(obj)


class NodeType(Enum):
    SECTION = "Section"
    PARAGRAPH = "Paragraph"
    CAPTION = "Caption"
    IMAGE = "Image"
    TABLE = "Table"
    TITLE = "Title"
    ROOT = "Root"


class ACTNode(NodeMixin):
    def __init__(
        self,
        id: str,
        name: str,
        nodeType,
        text=None,
        page=None,
        goal=None,
        parent=None,
        children=None,
        thread_id=None,
    ):
        if not isinstance(nodeType, NodeType):  # Ensure type is a NodeType
            raise TypeError("Node type must be a NodeType enum member")
        super(ACTNode, self).__init__()
        self.id = id
        self.name = name
        self.nodeType = nodeType
        self.text = text
        self.goal = goal
        self.parent = parent
        self.page = page
        if children:
            self.children = children
        thread_id = thread_id

    def print_tree(self, indent=0):
        output = ""
        for pre, fill, node in RenderTree(self):
            print("%s%s" % (pre, node.name))
            output += "%s%s\n" % (pre, node.name)
        return output

    def level_order_iter(self):
        return LevelOrderIter(self)

    def build_goal(self):
        if self.nodeType == NodeType.PARAGRAPH or self.nodeType == NodeType.CAPTION:
            self.goal = self.goal.text
        elif self.nodeType == NodeType.SECTION:
            union_goal = ""
            for child in PostOrderIter(self):
                union_goal += child.goal
            self.goal = union_goal

    def post_order_iter(self, **kwargs):
        return PostOrderIter(self, **kwargs)


class ACTTree:  # New class to encapsulate structure logic
    root: ACTNode

    def __init__(self, filepath: str):
        self.root = self._build_act_tree(filepath)
        # Assign hierarchical IDs
        self.assign_hierarchical_ids()
        # self.generate_goal()

    def _build_act_tree(self, filepath: str):
        doc = fitz.open(filepath)

        root = ACTNode(0, "Root", NodeType.ROOT)  # Create the root node

        # Keep track of the current section at each level
        section_stack = [root]

        section_id = 1  # Start with section ID 1
        subsection_counters = {}  # A dictionary to track subsection IDs at each level

        for entry in doc.get_toc():
            level, title, page_number = entry

            # Determine appropriate parent
            while level <= len(section_stack) - 1:
                section_stack.pop()  # Pop until we find the right parent level
            parent = section_stack[-1]

            # Create and append the node
            node = ACTNode(
                level, title, NodeType.SECTION, None, parent=parent, page=page_number
            )
            section_stack.append(node)

        # Prepare headers from toc_data
        headers = [(entry[1], entry[2]) for entry in doc.get_toc()]

        sections = {}
        for header in headers:
            sections[header[0]] = extract_content_for_header(doc, headers, header[0])

        # Content Association
        for node in root.level_order_iter():
            if node.nodeType in (NodeType.SECTION, NodeType.PARAGRAPH):
                node.text = sections.get(node.name, "")

        # Content Association with Paragraphs
        for node in root.level_order_iter():
            if node.nodeType == NodeType.SECTION:
                node.id = section_id
                section_id += 1

                subsection_id = (
                    subsection_counters.get(node.id, 0) + 1
                )  # Get or initialize
                # Update the counter
                subsection_counters[node.id] = subsection_id

                if not node.children:
                    paragraphs = split_into_paragraphs(node.text)

                    for paragraph_text in paragraphs:
                        if is_title(paragraph_text):
                            ACTNode(
                                0,
                                paragraph_text,
                                NodeType.TITLE,
                                paragraph_text,
                                parent=node,
                            )
                        else:
                            ACTNode(
                                0,
                                paragraph_text[:5],
                                NodeType.PARAGRAPH,
                                paragraph_text,
                                parent=node,
                            )

        return root

    def visualize_tree(self, file_path="act_tree.png"):
        from anytree.exporter import UniqueDotExporter  # Import here for clarity

        UniqueDotExporter(self.root).to_picture(file_path)

    def export_json(self, file_path):
        from anytree.exporter import JsonExporter

        # JSON Export is now independent of the Node class
        exporter = JsonExporter(
            indent=4, sort_keys=True, default=NodeTypeEncoder().default
        )
        with open(file_path, "w") as outfile:
            exporter.write(self.root, outfile)

    def assign_hierarchical_ids(self):
        node_id = 0

        for pre, _, node in RenderTree(self.root, style=AsciiStyle()):
            if node.parent and node.parent.parent is None:
                node_id += 1
            node.id = node_id

            if node.parent is not None:
                parent_depth = len(str(node.parent.id).split("."))
                subsection_id = 1
                for sibling in node.parent.children:
                    if sibling == node and node.parent.parent is not None:
                        node.id = f"{node.parent.id}.{subsection_id}"
                        break
                    subsection_id += 1

    def print_tree(self):
        self.root.print_tree()

    def generate_goal(self):
        act_assistant = ACT_Assistant()
        count = 0
        for node in self.root.post_order_iter():
            if count == 10:
                break
            if node.nodeType == NodeType.PARAGRAPH:
                act_assistant.add_message_to_thread("Paragraph:\n" + node.text)
                node.goal = act_assistant.run_assistant_single_paragraph()
            elif node.nodeType == NodeType.TITLE:
                node.goal = node.text
            elif node.nodeType == NodeType.SECTION:
                union_goal = ""
                for child in node.children:
                    if child.goal:
                        union_goal += child.goal
                node.goal = union_goal
            count += 1
