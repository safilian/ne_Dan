from enum import Enum
import networkx as nx
import matplotlib.pyplot as plt
from anytree import NodeMixin, RenderTree, AsciiStyle
from anytree.exporter import UniqueDotExporter
from anytree.iterators.levelorderiter import LevelOrderIter
from anytree.iterators.postorderiter import PostOrderIter
from anytree.exporter import JsonExporter
from json import JSONEncoder

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



class ACTNode(NodeMixin):
    def __init__(self, id: str, name: str, nodeType, text, page=None, goal=None, parent=None, children=None, **kwargs):
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
        self.children = []

    def print_tree(self, indent=0):
        for pre, fill, node in RenderTree(self):
            print("%s%s" % (pre, node.id))

    def visualize_tree(self):
        UniqueDotExporter(self).to_picture("act_tree.png")
    
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
    
    def export_json(self, file_path):
        exporter = JsonExporter(indent=4, sort_keys=True, default=NodeTypeEncoder().default)
        with open(file_path, "w") as outfile:
                exporter.write(self, outfile)
        return exporter.export(self)
    
    def assign_hierarchical_ids(self):
        node_id = 0 

        for pre, _, node in RenderTree(self, style=AsciiStyle()):
            if node.parent and node.parent.parent is None:
                node_id += 1 
            node.id = node_id
            print(f"Global node_id: {node_id}")


            if node.parent is not None:  
                parent_depth = len(str(node.parent.id).split("."))
                subsection_id = 1 
                print(f"Node: {node.id}, Parent: {node.parent.id}")  # Added
                for sibling in node.parent.children:
                    if sibling == node and node.parent.parent is not None:  
                        node.id = f"{node.parent.id}.{subsection_id}"
                        print(f"Formatted ID: {node.id}") 
                        break
                    subsection_id += 1 







def print_act_tree(node, indent=0):
    print("  " * indent + f"({node.id}) {node.type}: {node.text} - Goal: {node.goal}")
    for child in node.children:
        print_act_tree(child, indent + 1)
        

    # def Constructing_Answer_based_Tree(answer):


#     root = ACTNode(0, "Root", None)  # Create the root node
#     current_section = None

#     for element in answer:
#         if element.type == "Section":
#             current_section = ACTNode(element.id, "Section", element.text)
#             root.add_child(current_section) 
#         elif element.type == "Paragraph" or element.type == "Caption":
#             node = ACTNode(element.id, element.type, element.text)
#             if element.type == "Paragraph":
#                 node.goal = LLM_Pragraph_Main_Goal(element.text)  
#             else:  # element.type == "Caption"
#                 node.goal = summarize_caption(element.text)  # Replace with your summarization logic
#             current_section.add_child(node)  

#     return root 


def visualize_act_tree(root):
    G = nx.DiGraph()  # Directed graph for the hierarchy 

    def add_nodes(node):
        G.add_node(node.id, type=node.type, text=node.text)
        for child in node.children:
            G.add_edge(node.id, child.id)
            add_nodes(child)

    add_nodes(root)

    # Customize visualization (optional)
    node_labels = nx.get_node_attributes(G, 'text')
    pos = nx.spring_layout(G)  # Or other layout algorithms

    nx.draw(G, pos, with_labels=True, labels=node_labels)
    plt.show()
