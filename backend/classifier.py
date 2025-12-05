from google.adk.agents.llm_agent import LlmAgent
from google.adk.planners import BuiltInPlanner
from google.genai.types import ThinkingConfig
from pydantic import BaseModel, Field
from enum import Enum

class ContractType(str, Enum):
    NDA = "NDA"
    FREELANCE = "Freelance Agreement"
    OTHER = "Other"

class ClassifierOutput(BaseModel):
    contract_type: ContractType = Field(description="The type of the contract.")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0.")

class ClassifierAgent(LlmAgent):
    def __init__(self):
        super().__init__(
            model='gemini-2.0-flash',
            name='classifier_agent',
            instruction="""You are an expert legal contract classifier.
            Analyze the provided text and classify it into one of the following categories:
            - NDA (Non-Disclosure Agreement)
            - Freelance Agreement (Service Agreement, Contractor Agreement, Master Services Agreement/MSA, Statement of Work/SOW)
            - Other (Lease, Employment, etc.)
            
            Respond ONLY with a JSON object matching the ClassifierOutput schema.
            """,
            planner=BuiltInPlanner(thinking_config=ThinkingConfig(include_thoughts=True)),
            output_schema=ClassifierOutput,
        )
