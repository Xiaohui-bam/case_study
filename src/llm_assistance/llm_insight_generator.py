from abc import ABC, abstractmethod
from typing import Dict, Any
from openai import OpenAI


class LLMInsightGeneratorBase(ABC):
    """
    Base class for generating insights from LLMs (Large Language Models).
    This class defines the interface for generating insights based on technical findings.
    Subclasses should implement the `generate_insight` method.
    """

    @abstractmethod
    def generate_insight(self, findings: str) -> str:
        pass


class GPTInsightGenerator(LLMInsightGeneratorBase):
    """
    Class for generating insights using OpenAI's GPT models.
    This class uses the OpenAI API to generate plain-language summaries of technical data quality findings.
    Inputs:
        api_key (str): OpenAI API key for authentication.
        model (str): The GPT model to use (default is "gpt-4o-mini").
    """

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        """
        Initializes the GPTInsightGenerator with an API key and model.
        """
        self.model = model
        self.api_key = api_key
        self.client = OpenAI(api_key=self.api_key)

    def _build_prompt(self, findings: str) -> str:
        """
        Build the prompt for the LLM based on the technical findings.
        This method formats the findings into a clear and concise prompt for the LLM to generate insights.
        """
        return (
            f"You are a Regulatory Reporting Analyst tasked with interpreting technical data quality findings "
            f"into plain-language summaries for financial regulators.\n\n"
            f"Here are the technical findings:\n{findings}\n\n"
            "Provide a concise summary suitable for a regulatory report. "
            "Explain what the issues mean, why they matter, and what action (if any) should be taken."
        )

    def generate_insight(self, findings: str) -> str:
        """
        Generate insights from the LLM based on the provided technical findings.
        This method sends the findings to the LLM and retrieves a plain-language summary.
        """
        prompt = self._build_prompt(findings)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful Regulatory Reporting Analyst who explains financial data clearly for compliance and regulatory reporting.",
                },
                {"role": "user", "content": prompt},
            ],
        )

        return response.choices[0].message.content.strip()
