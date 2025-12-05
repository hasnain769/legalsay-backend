from google.adk.agents.llm_agent import LlmAgent
from google.adk.planners import BuiltInPlanner
from google.adk.tools import google_search
from google.genai import types
from google.genai.types import ThinkingConfig
from pydantic import BaseModel, Field

class ExplainerOutput(BaseModel):
    explanation: str = Field(description="A clear, plain-English explanation of the risk, why it matters, and potential consequences.")

class ExplainerAgent(LlmAgent):
    def __init__(self):
        super().__init__(
            model='gemini-2.0-flash',
            name='explainer_agent',
            instruction="""You are a legal expert assistant.
            Your task is to explain a specific contract risk to a non-lawyer.
            
            You will be provided with:
            1. The text of the risk or flag.
            2. The context of the contract (type, summary).
            
            IMPORTANT: You have access to Google Search. Use it to find relevant case law or statutes if the risk involves specific legal concepts.
            
            Your output must be:
            - Clear and concise (plain English).
            - Explain WHY this is a risk.
            - Explain the potential consequences if left unchanged.
            - Cite specific laws or precedents if found via search.
            - Be professional but accessible (like a helpful lawyer).

            OUTPUT FORMAT:
            You MUST return a valid JSON object with the following structure:
            {
                "explanation": "Your plain English explanation here."
            }
            Do not wrap in markdown code blocks.
            """,
            tools=[google_search],
        )
