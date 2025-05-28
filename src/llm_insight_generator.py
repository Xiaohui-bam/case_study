from abc import ABC, abstractmethod
from typing import Dict, Any
from openai import OpenAI



class LLMInsightGeneratorBase(ABC):
    @abstractmethod
    def generate_insight(self, findings: str) -> str:
        pass


class GPTInsightGenerator(LLMInsightGeneratorBase):
    def __init__(self, api_key:str,  model: str = "gpt-4o-mini"):
        self.model = model
        self.api_key = api_key
        self.client =OpenAI(api_key=self.api_key)

    def _build_prompt(self, findings: str) -> str:
        return (
            f"You are a Regulatory Reporting Analyst tasked with interpreting technical data quality findings "
            f"into plain-language summaries for financial regulators.\n\n"
            f"Here are the technical findings:\n{findings}\n\n"
            "Provide a concise summary suitable for a regulatory report. "
            "Explain what the issues mean, why they matter, and what action (if any) should be taken."
        )

    def generate_insight(self, findings: str) -> str:
        prompt = self._build_prompt(findings)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
        {"role": "system", "content": "You are a helpful Regulatory Reporting Analyst who explains financial data clearly for compliance and regulatory reporting."},
        {"role": "user", "content": prompt}])

        return response.choices[0].message.content.strip()
