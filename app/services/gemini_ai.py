"""
Gemini AI service for interpreting statistical results.
"""

import json
from typing import Any, Dict, List, Optional

from google import genai
from google.genai import types


class GeminiAIService:
    """
    Service that sends survey data and statistics to Gemini AI
    for interpretation and explanation.
    """

    DEFAULT_MODEL = "gemini-2.5-flash"

    def __init__(self, api_key: str, model: str = ""):
        """
        Initialize the Gemini AI service.

        Args:
            api_key: Google Gemini API key.
            model: Gemini model name. Falls back to DEFAULT_MODEL if empty.
        """
        self.client = genai.Client(api_key=api_key)
        self.model = model or self.DEFAULT_MODEL

    def interpret_results(
        self,
        overall_stats: List[Dict[str, Any]],
        grouped_stats: Optional[Dict] = None,
        groupings_info: Optional[Dict] = None,
    ) -> str:
        """
        Send statistical results to Gemini and get a plain-language interpretation.

        Args:
            overall_stats: List of per-question statistics dictionaries.
            grouped_stats: Optional grouped statistics by demographic.
            groupings_info: Optional metadata about grouping columns.

        Returns:
            AI-generated interpretation text.
        """
        prompt = self._build_prompt(overall_stats, grouped_stats, groupings_info)

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=4096,
                ),
            )
            return response.text
        except Exception as e:
            return f"AI analiza nije dostupna: {str(e)}"

    def _build_prompt(
        self,
        overall_stats: List[Dict[str, Any]],
        grouped_stats: Optional[Dict],
        groupings_info: Optional[Dict],
    ) -> str:
        """Build a concise prompt for the AI model."""
        stats_json = json.dumps(overall_stats, ensure_ascii=False, indent=2)

        prompt = (
            "You are a statistics expert. A user conducted a Likert-scale (1-5) survey. "
            "Below are the calculated descriptive statistics for each question.\n\n"
            "Statistical abbreviations:\n"
            "- N = number of respondents\n"
            "- AS = arithmetic mean\n"
            "- SD = standard deviation\n"
            "- Median = median value\n"
            "- Ske = skewness\n"
            "- Kur = kurtosis\n"
            "- Max D = Kolmogorov-Smirnov statistic\n"
            "- K-S p = Kolmogorov-Smirnov p-value\n\n"
            f"Overall statistics:\n{stats_json}\n"
        )

        if grouped_stats and groupings_info:
            grouped_json = json.dumps(grouped_stats, ensure_ascii=False, indent=2)
            prompt += f"\nGrouped statistics by demographics:\n{grouped_json}\n"

        prompt += (
            "\nProvide a SHORT and CLEAR interpretation (max 5-6 sentences). "
            "Highlight which questions scored highest/lowest, whether responses "
            "are normally distributed, and any notable patterns. "
            "Format your response as HTML using Bootstrap 5 classes for styling. "
            "Use elements like <h6>, <p>, <ul>, <li>, <strong>, <span class='badge bg-...'>, "
            "<span class='text-success'>, <span class='text-danger'>, etc. to make it visually clear. "
            "Do NOT wrap the response in ```html code blocks. Return raw HTML only. "
            "Answer in the SAME LANGUAGE as the question text."
        )

        return prompt
