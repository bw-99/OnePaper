# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License
"""A file containing prompts definition."""

KEYWORD_REPORT_PROMPT = """
You are an expert in community analysis and machine learning. You are skilled at mapping out relationships and structures within professional networks, particularly in the tech industry.
You are adept at helping people identify key players, collaborations, and knowledge flows within the machine learning community, enabling them to leverage these insights for strategic decision-making.

# Goal
Identify a single representative keyword for a community based on its community report.
The keyword must encapsulate the essence of the community, considering its title, summary, findings, and other provided details.
Additionally, provide a concise and clear explanation for why this keyword was selected.

# Report Structure

The input will be a JSON-formatted community report with the following structure:

- TITLE: The community's name that represents its key entities. The title should be short but specific, including representative named entities when possible.
- SUMMARY: An executive summary of the community's overall structure, how its entities are related to each other, and significant points associated with its entities.
- RATING: A float score between 0-10 representing the relevance of the text to machine learning, community analysis, bug tracking, and automated program repair. A rating of 1 means trivial or irrelevant, and 10 means highly significant, impactful, and actionable.
- RATING EXPLANATION: A single-sentence explanation for the rating.
- DETAILED FINDINGS: A list of 5-10 key insights about the community. Each insight contains:
- SUMMARY: A brief summary of the finding.
- EXPLANATION: A detailed explanation of the finding.

Your task is to:
1. Identify one representative keyword for the community.
2. Provide a reason for the selection, based on the report's title, summary, rating, and findings.

The report should include the following sections:

Return output as a well-formed JSON-formatted string with the following format:
    {{
        "keyword": "<representative_keyword>",
        "keyword_explanation": "<reason_for_keyword_selection>"
    }}


# Grounding Rules

1. Use all relevant parts of the report, including the title, summary, findings, and rating, to identify the keyword.
2. Ensure the reason is concise and supported by details from the report.

# Example Input
-----------
Text:

title
Neural Network Optimization in Collaborative Research

summary
The community revolves around the development of optimized neural network techniques. Collaboration is a key theme, involving researchers from diverse institutions. Significant contributions include advancements in gradient-based methods, pruning techniques, and parallel computing.

rating
9.0

rating_explanation
The report highlights impactful developments in optimization techniques central to machine learning.

findings
[
    {
        "summary": "Gradient-based methods as a focus area",
        "explanation": "Several researchers in the community have developed cutting-edge algorithms that improve the efficiency of gradient descent for large-scale neural networks. These methods significantly reduce computation time and enhance model accuracy."
    },
    {
        "summary": "Pruning techniques gaining traction",
        "explanation": "Pruning has emerged as a key trend, enabling smaller and faster neural networks without sacrificing performance. This aligns with the community's focus on practical and scalable solutions."
    },
    {
        "summary": "Collaboration across institutions",
        "explanation": "The community thrives on partnerships between universities and tech companies, fostering innovative solutions and sharing computational resources for large-scale experiments."
    }
]

Output:
{{
    "keyword": "Optimization",
    "reason": "The keyword 'Optimization' represents the community's central focus, as evidenced by its emphasis on gradient-based methods, pruning, and scalability, highlighted in both the title and findings."
}}


# Real Data

Use the following text for your answer. Do not make anything up in your answer.

Text:
{input_text}

The report should include the following sections:

Return output as a well-formed JSON-formatted string with the following format:
    {{
        "keyword": "<representative_keyword>",
        "keyword_explanation": "<reason_for_keyword_selection>"
    }}


# Grounding Rules

1. Use all relevant parts of the report, including the title, summary, findings, and rating, to identify the keyword.
2. Ensure the reason is concise and supported by details from the report.

Output:"""
