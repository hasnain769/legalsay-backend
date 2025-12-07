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

class FlagWithText(BaseModel):
    analysis: str = Field(description="The AI analysis of the risk or benefit")
    original_text: str = Field(description="The actual clause text from the contract")

# --- DEFINE YOUR OUTPUT SCHEMA ---
class ContractAnalysisOutput(BaseModel):
    """The structured analysis of the legal contract."""
    contract_type: str = Field(description="The classified type of the contract (e.g., NDA, Freelance Agreement).")
    jurisdiction: str = Field(description="The governing law/jurisdiction identified in the contract.")
    key_details: List[KeyDetail] = Field(description="Key extracted details like Parties, Effective Date, Term, Fees, etc.")
    red_flags: List[FlagWithText] = Field(description="A list of critical red flags with original text.")
    yellow_flags: List[FlagWithText] = Field(description="A list of moderate risks with original text.")
    green_flags: List[FlagWithText] = Field(description="A list of positive clauses with original text.")
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
            2. Findings from the Specialist (NDA, SOW, or General) - including jurisdiction.
            3. Risk Flags (Red/Yellow/Green) from the Risk Agent - each flag contains 'analysis' and 'original_text'.
            
            Your Output:
            - jurisdiction: Extract from specialist_findings. If not found, use 'Not Specified'.
            - plain_english_summary: A clear, professional summary of what this contract is and what it does. Mention the Jurisdiction if available.
            - total_health_score: An integer 0-100.
                - Start at 100.
                - Deduct 15-20 points for each RED FLAG.
                - Deduct 5-10 points for each YELLOW FLAG.
                - If the contract violates local law (based on Jurisdiction), the score should be very low (<40).
            - key_details: Ensure these are clean and readable.
            - flags: Pass through ALL flags from risk_findings with both 'analysis' and 'original_text' intact.
            """,
            output_schema=ContractAnalysisOutput,
        )

root_agent = LegalAgent()