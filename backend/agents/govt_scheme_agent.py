"""
🏛️ GOVERNMENT SCHEME INTEGRATION AGENT
Recommends applicable government schemes and subsidies
"""
from typing import Dict, Any, List
import random

class GovtSchemeAgent:
    def __init__(self):
        self.name = "Government Scheme Agent"
        
        # Government schemes database
        self.schemes = [
            {
                "name": "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)",
                "type": "Direct Cash Transfer",
                "benefit": "₹6,000 per year in 3 installments",
                "eligibility": "All farmers with cultivable land",
                "state": "all",
                "crop": "all",
                "application": "Online via PM-KISAN portal"
            },
            {
                "name": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
                "type": "Crop Insurance",
                "benefit": "Coverage for crop loss due to natural calamities",
                "eligibility": "All farmers (landowner/tenant)",
                "state": "all",
                "crop": "all",
                "application": "Through banks, CSCs, or insurance portals"
            },
            {
                "name": "Kisan Credit Card (KCC)",
                "type": "Credit Facility",
                "benefit": "Low-interest farm loans up to ₹3 lakhs",
                "eligibility": "Farmers, tenant farmers, sharecroppers",
                "state": "all",
                "crop": "all",
                "application": "Apply through banks"
            },
            {
                "name": "Soil Health Card Scheme",
                "type": "Advisory",
                "benefit": "Free soil testing and recommendations",
                "eligibility": "All farmers",
                "state": "all",
                "crop": "all",
                "application": "Through Krishi Vigyan Kendra or agriculture dept"
            },
            {
                "name": "Paramparagat Krishi Vikas Yojana (PKVY)",
                "type": "Organic Farming Support",
                "benefit": "₹50,000 per hectare for 3 years",
                "eligibility": "Farmers adopting organic farming",
                "state": "all",
                "crop": "all",
                "application": "Through State Agriculture Department"
            },
            {
                "name": "Micro Irrigation Subsidy",
                "type": "Equipment Subsidy",
                "benefit": "40-55% subsidy on drip/sprinkler systems",
                "eligibility": "Small and marginal farmers",
                "state": "all",
                "crop": "all",
                "application": "State Agriculture/Horticulture Department"
            },
            {
                "name": "National Mission for Sustainable Agriculture",
                "type": "Training & Support",
                "benefit": "Free training, technical assistance",
                "eligibility": "All farmers",
                "state": "all",
                "crop": "all",
                "application": "Contact local agriculture officer"
            }
        ]
    
    def get_applicable_schemes(self, state: str = "all", crop_type: str = "all", 
                               farmer_category: str = "small") -> Dict[str, Any]:
        """Get applicable government schemes"""
        
        result = {
            "agent": self.name,
            "timestamp": None,
            "state": state,
            "crop_type": crop_type,
            "farmer_category": farmer_category,
            "applicable_schemes": [],
            "total_potential_benefit": 0,
            "priority_schemes": [],
            "application_support": {}
        }
        
        # Filter applicable schemes
        for scheme in self.schemes:
            if (scheme["state"] == "all" or scheme["state"] == state) and \
               (scheme["crop"] == "all" or scheme["crop"] == crop_type):
                
                scheme_info = scheme.copy()
                scheme_info["priority"] = self._calculate_scheme_priority(scheme, farmer_category)
                result["applicable_schemes"].append(scheme_info)
        
        # Sort by priority
        result["applicable_schemes"].sort(key=lambda x: x["priority"], reverse=True)
        
        # Top 3 priority schemes
        result["priority_schemes"] = result["applicable_schemes"][:3]
        
        # Calculate potential benefit
        benefit_estimate = 0
        for scheme in result["applicable_schemes"]:
            if "₹" in scheme["benefit"]:
                # Extract numeric value (simplified)
                benefit_estimate += 10000  # Average estimate
        
        result["total_potential_benefit"] = benefit_estimate
        
        # Application support
        result["application_support"] = {
            "documents_required": [
                "Aadhaar Card",
                "Land ownership documents / Tenant agreement",
                "Bank account details",
                "Passport size photographs",
                "Crop sowing certificate (if applicable)"
            ],
            "common_portals": [
                "PM-KISAN: https://pmkisan.gov.in",
                "PMFBY: https://pmfby.gov.in",
                "DBT Agriculture: https://dbtdirect.gov.in"
            ],
            "helpline": "Kisan Call Center: 1800-180-1551"
        }
        
        # Generate claim-ready data
        result["claim_templates"] = self._generate_claim_templates()
        
        return result
    
    def _calculate_scheme_priority(self, scheme: Dict, farmer_category: str) -> int:
        """Calculate scheme priority score"""
        
        priority = 50  # Base priority
        
        # High priority for insurance
        if scheme["type"] == "Crop Insurance":
            priority += 30
        
        # High priority for direct cash benefit
        if scheme["type"] == "Direct Cash Transfer":
            priority += 25
        
        # High priority for credit facility
        if scheme["type"] == "Credit Facility":
            priority += 20
        
        # Small farmers benefit more from subsidies
        if farmer_category == "small" and "Subsidy" in scheme["type"]:
            priority += 15
        
        return priority
    
    def _generate_claim_templates(self) -> Dict[str, Any]:
        """Generate templates for insurance/subsidy claims"""
        
        templates = {
            "crop_insurance_claim": {
                "steps": [
                    "1. Report crop loss within 72 hours to insurance company",
                    "2. Submit claim form with required documents",
                    "3. Attend field inspection by surveyor",
                    "4. Submit post-harvest report if applicable",
                    "5. Receive claim settlement in bank account"
                ],
                "documents": [
                    "Crop insurance policy copy",
                    "Land records",
                    "Sowing certificate",
                    "Photographs of damaged crop",
                    "Bank account details"
                ]
            },
            "subsidy_application": {
                "steps": [
                    "1. Register on DBT Agriculture portal",
                    "2. Fill subsidy application form online",
                    "3. Upload required documents",
                    "4. Submit for verification",
                    "5. Track application status online"
                ],
                "documents": [
                    "Aadhaar card",
                    "Land records",
                    "Bank passbook",
                    "Quotation/invoice of equipment (if applicable)"
                ]
            }
        }
        
        return templates
    
    def generate_subsidy_report(self, farm_id: str, actions_taken: List[Dict]) -> Dict[str, Any]:
        """Generate report for subsidy claims"""
        
        report = {
            "farm_id": farm_id,
            "report_date": None,
            "actions_summary": actions_taken,
            "eligible_subsidies": [],
            "total_claim_amount": 0
        }
        
        # Analyze actions for eligible subsidies
        for action in actions_taken:
            if "irrigation" in action.get("action_type", "").lower():
                report["eligible_subsidies"].append({
                    "scheme": "Micro Irrigation Subsidy",
                    "estimated_amount": 5000
                })
            elif "organic" in action.get("action_type", "").lower():
                report["eligible_subsidies"].append({
                    "scheme": "PKVY Organic Farming",
                    "estimated_amount": 15000
                })
        
        report["total_claim_amount"] = sum(s["estimated_amount"] for s in report["eligible_subsidies"])
        
        return report
