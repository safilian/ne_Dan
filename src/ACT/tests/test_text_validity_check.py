from ACT.src.text_validity_check import (
    get_sections_from_text,
    get_sections_from_file,
    validate_section_order,
)
from ACT.tests.mock import SAMPLE_TEXT_FILE_PATH


def test_get_sections_from_text():
    text = "1. Introduction\n\n1.1. Background and Problem Statement\n\n1.2. Research Questions"
    expected_sections = [
        ("1", "Introduction"),
        ("1.1", "Background and Problem Statement"),
        ("1.2", "Research Questions"),
    ]
    assert get_sections_from_text(text) == expected_sections


def test_get_sections_from_file():
    expected_sections = [
        ("1", "Introduction"),
        ("1.1", "Background and Problem Statement:"),
        ("1.1.1", "Sample Heading"),
        ("1.2", "Research Questions:"),
        ("1.3", "Project Goals and Scope:"),
        ("2", "Literature Review"),
        ("2.1", "Data Quality and Anomaly Detection:"),
        ("2.2", "Applications of NLP in Data Quality:"),
        ("3", "Methodology"),
        ("3.1", "Data Collection and Preprocessing:"),
        ("3.3", "False Heading"),
        ("3.2", "Feature Engineering:"),
        ("3.3", "Model Selection and Evaluation:"),
        ("4", "Results and Discussion"),
        ("4.1", "Experimental Setup:"),
        ("4.2", "Model Performance:"),
        ("4.3", "Limitations and Future Work:"),
    ]
    assert get_sections_from_file(SAMPLE_TEXT_FILE_PATH) == expected_sections


def test_validate_section_order():
    sections = [
        ("1", "Introduction"),
        ("1.1", "Background and Problem Statement"),
        ("1.1.1", "Sample Heading"),
        ("1.2", "Research Questions"),
        ("1.3", "Project Goals and Scope"),
        ("2", "Literature Review"),
        ("2.1", "Data Quality and Anomaly Detection"),
        ("2.2", "Applications of NLP in Data Quality"),
        ("3", "Methodology"),
        ("3.1", "Data Collection and Preprocessing"),
        ("3.2", "Feature Engineering"),
        ("3.3", "Model Selection and Evaluation"),
        ("4", "Results and Discussion"),
        ("4.1", "Experimental Setup"),
        ("4.2", "Model Performance"),
        ("4.3", "Limitations and Future Work"),
    ]
    assert validate_section_order(sections) == True


def test_invalid_section_order():
    sections = [
        ("1", "Introduction"),
        ("1.1", "Background and Problem Statement"),
        ("1.2", "Research Questions"),
        ("1.1.1", "Sample Heading"),
        ("1.3", "Project Goals and Scope"),
        ("2", "Literature Review"),
        ("2.1", "Data Quality and Anomaly Detection"),
        ("2.2", "Applications of NLP in Data Quality"),
        ("3", "Methodology"),
        ("3.1", "Data Collection and Preprocessing"),
        ("3.3", "False Heading"),
        ("3.2", "Feature Engineering"),
        ("3.3", "Model Selection and Evaluation"),
        ("4", "Results and Discussion"),
        ("4.1", "Experimental Setup"),
        ("4.2", "Model Performance"),
        ("4.3", "Limitations and Future Work"),
    ]
    assert validate_section_order(sections) == False
