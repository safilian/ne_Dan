# ACT

## Description
This folder contains the files and resources related to the ACT (Answer_based_Tree) project.


## Constructing Answer-based Tree (ACT)

### Each node attributes:
- ID
- Type
- Text
- Goal

#### Node Type: 
- Paragraph
- Section

### Algorithm:
```python
Constructing_Answer_based_Tree(ACT, Answer) {
    Input: Answer
    Output: ACT tree

    Create an empty ACT tree with a root node R with Null values
    Expand ACT in such way that {
        all internal nodes are related to the section or subsection
        child nodes of a section node are subsections of the section or are paragraphs or captions in that section related to the section
        all leaf nodes are related to paragraphs to caption
        text of internal node is the title of the section
        text of a leaf node is paragraph or section
        For all leaf nodes N that are paragraphs, N.Goal = LLM_Pragraph_Main_Goal(N.Text)
        For all leaf nodes N that are captions, N.Goal is a summary of the caption
        For all internal node N, N.Goal =
    }
}
```

## Example
![act_tree](act_tree.png "Samle ACT tree")

## Contributing
1. Fork this repository.
2. Create a new branch: `git checkout -b feature/your-feature-name`.
3. Make your changes and commit them: `git commit -m 'Add some feature'`.
4. Push to the branch: `git push origin feature/your-feature-name`.
5. Submit a pull request.

## License
This project is licensed under the [MIT License](LICENSE).

## Contact
For any questions or suggestions, please feel free to reach out to us at [dannguyen0801@gmail.com](dannguyen0801@gmail.com).