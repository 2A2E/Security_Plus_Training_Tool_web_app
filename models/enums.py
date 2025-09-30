"""
Enums for Security Plus Training Tool
"""
from enum import Enum

class QuestionType(Enum):
    """Enumeration of question types"""
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    FILL_IN_BLANK = "fill_in_blank"
    SCENARIO_BASED = "scenario_based"
    DRAG_DROP = "drag_drop"

class DifficultyLevel(Enum):
    """Enumeration of difficulty levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class QuestionCategory(Enum):
    """Enumeration of Security+ question categories"""
    THREATS_ATTACKS_VULNERABILITIES = "threats_attacks_vulnerabilities"
    TECHNOLOGIES_TOOLS = "technologies_tools"
    ARCHITECTURE_DESIGN = "architecture_design"
    IDENTITY_ACCESS_MANAGEMENT = "identity_access_management"
    RISK_MANAGEMENT = "risk_management"
    CRYPTOGRAPHY_PKI = "cryptography_pki"
    GOVERNANCE_COMPLIANCE = "governance_compliance"
    INCIDENT_RESPONSE = "incident_response"
    SECURITY_OPERATIONS = "security_operations"
    SECURITY_ASSESSMENT = "security_assessment"
