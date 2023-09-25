researchpal: A Python Library for Automated Literature Review Generation

researchpal is a Python library that automates the process of generating academic literature reviews based on a research question. It utilizes external data sources to fetch research papers, synthesizes the findings, and generates a concise literature review. This library is particularly useful for researchers and students looking to streamline the literature review process.

Features:
1. Fetches research papers from Springer and Arxiv.
2. Synthesizes research findings into a coherent literature review.
3. Extracts citations and generates a references list.
4. Supports both short and long literature reviews.

Prerequisites:
Before using researchpal, ensure you have the following prerequisites:

1. Python 3.x installed on your system.
2. An API key for OpenAI (required for certain functionalities).

Installation:
To install researchpal, you can use pip: "pip install researchpal"

Usage:
Here's a basic example of how to use researchpal in your Python script: from researchpal import literature_review

research_question = "your_query"
openai_key = "your_openai_api_key"
length = "short"  # Can be "short" or "long"

generate_literature_review(research_question, openai_key, length)

Options:
1. research_question: Your research question.
2. openai_key: Your OpenAI API key.
3. length (optional): The length of the literature review ("short" or "long," default is "short").

License:
This project is licensed under the MIT License - see the LICENSE file for details.

Contributing:
Contributions are welcome! Please read our Contributing Guidelines for more information.

Support and Feedback:
For support or feedback, please contact us at email@example.com.

Acknowledgments:
This library makes use of data from Springer and Arxiv, and it may require an OpenAI API key for certain functionality.