from random import sample
from act import ACTNode, NodeType, ACTTree
from assistant import ACT_Assistant

sample_filepath = '../../raw_data/sample_reports/s1-2022 (1)/45698120_Talha Islam_assignsubmission_file/45698120.pdf'




sample_act = ACTTree(sample_filepath)
sample_act.print_tree()
sample_act.visualize_tree()

for node in sample_act.root.root.children[2].children[2].children:
    print(node.name, node.id, node.text)

sample_act.export_json("sample_act.json")
print(sample_act.root.children[0].text)

# sample_node3 = ACTNode(0, "This is a sample section", NodeType.SECTION, "This is a sample section")
# sample_node1 = ACTNode(0, "This is a sample paragraph", NodeType.PARAGRAPH, "This is a sample paragraph", parent=sample_node3)
# sample_node2 = ACTNode(0, "This is a sample title", NodeType.TITLE, "This is a sample title", parent=sample_node3)

# sample_node3.print_tree()
