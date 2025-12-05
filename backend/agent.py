from google.adk.agents.llm_agent import LlmAgent
from google.adk.planners import BuiltInPlanner
from google.genai import types
from google.genai.types import ThinkingConfig
from pydantic import BaseModel, Field
from typing import List
# We no longer need 'GoogleLlm' or 'genai' imports here

class KeyDetail(BaseModel):
    label: str = Field(description="The label of the detail (e.g., 'Parties', 'Effective Date').")
    value: str = Field(description="The value of the detail.")

# --- DEFINE YOUR OUTPUT SCHEMA ---
class ContractAnalysisOutput(BaseModel):
    """The structured analysis of the legal contract."""
    contract_type: str = Field(description="The classified type of the contract (e.g., NDA, Freelance Agreement).")
    key_details: List[KeyDetail] = Field(description="Key extracted details like Parties, Effective Date, Term, Fees, etc.")
    red_flags: List[str] = Field(description="A list of critical red flags or high-risk clauses found in the contract.")
    yellow_flags: List[str] = Field(description="A list of moderate risks or clauses that require clarification.")
    green_flags: List[str] = Field(description="A list of positive or standard, fair clauses.")
    plain_english_summary: str = Field(description="A concise summary of the contract's purpose and key terms in plain English.")
    total_health_score: int = Field(description="An overall score from 0 (very bad) to 100 (excellent) representing the contract's fairness and safety.")
# --- END SCHEMA ---

class LegalAgent(LlmAgent):
    def __init__(self):
        super().__init__(
            model='gemini-2.0-flash',
            name='legal_synthesizer',
            instruction="""You are the Chief Legal Officer.
            Your goal is to synthesize the findings from your specialist agents into a cohesive, final report.
            
            You will receive:
            1. The Contract Type (from Classifier).
            2. Findings from the Specialist (NDA, SOW, or General).
            3. Risk Flags (Red/Yellow/Green) from the Risk Agent.
            4. The Jurisdiction (Governing Law).
            
            Your Output:
            - plain_english_summary: A clear, professional summary of what this contract is and what it does. Mention the Jurisdiction if relevant.
            - total_health_score: An integer 0-100.
                - Start at 100.
                - Deduct 15-20 points for each RED FLAG.
                - Deduct 5-10 points for each YELLOW FLAG.
                - If the contract violates local law (based on Jurisdiction), the score should be very low (<40).
            - key_details: Ensure these are clean and readable.
            - flags: Pass through the most important flags.
            """,
            output_schema=ContractAnalysisOutput,
        )

root_agent = LegalAgent()