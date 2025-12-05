from typing import List
from .classifier import ContractType

def get_specialists_for_type(contract_type: ContractType) -> List[str]:
    """
    Returns a list of specialist agent names based on the contract type.
    """
    common_agents = ["risk_agent", "general_parser"]
    
    if contract_type == ContractType.NDA:
        return common_agents + ["nda_parser"]
    elif contract_type == ContractType.FREELANCE:
        return common_agents + ["sow_parser"]
    else:
        return common_agents
