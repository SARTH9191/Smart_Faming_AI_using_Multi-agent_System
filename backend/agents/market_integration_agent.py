"""
🏪 MARKET INTEGRATION AGENT
Connects farmers with buyers, suggests storage & transport
"""
from typing import Dict, Any, List
import random

class MarketIntegrationAgent:
    def __init__(self):
        self.name = "Market Integration Agent"
        
        # Sample buyer database
        self.buyers = [
            {"name": "AgriTrade Corp", "type": "wholesale", "location": "Delhi", "rating": 4.5},
            {"name": "FreshMart Chain", "type": "retail", "location": "Mumbai", "rating": 4.2},
            {"name": "Export Solutions Ltd", "type": "export", "location": "Gujarat", "rating": 4.8},
            {"name": "Local Mandi", "type": "mandi", "location": "Punjab", "rating": 3.9},
            {"name": "Online AgriMarket", "type": "e-commerce", "location": "Pan-India", "rating": 4.6}
        ]
    
    def find_buyers(self, crop: str, quantity_tons: float, location: str = "Delhi") -> Dict[str, Any]:
        """Find potential buyers for crops"""
        
        result = {
            "agent": self.name,
            "timestamp": None,
            "crop": crop,
            "quantity_tons": quantity_tons,
            "location": location,
            "potential_buyers": [],
            "e_nam_info": {},
            "recommendations": []
        }
        
        # Filter and score buyers
        for buyer in self.buyers:
            # Add to results with offer price
            offer = {
                "buyer_name": buyer["name"],
                "buyer_type": buyer["type"],
                "location": buyer["location"],
                "rating": buyer["rating"],
                "estimated_offer": round(random.uniform(18000, 24000), 2),
                "payment_terms": random.choice(["Immediate", "7 days", "15 days"]),
                "contact": f"+91-{random.randint(7000000000, 9999999999)}"
            }
            result["potential_buyers"].append(offer)
        
        # Sort by offer price
        result["potential_buyers"].sort(key=lambda x: x["estimated_offer"], reverse=True)
        
        # e-NAM integration info
        result["e_nam_info"] = {
            "platform": "e-NAM (National Agriculture Market)",
            "benefits": [
                "Pan-India market access",
                "Transparent price discovery",
                "Online payment",
                "Quality assurance"
            ],
            "registration_link": "https://www.enam.gov.in",
            "nearest_e_nam_mandi": f"e-NAM Mandi, {location}"
        }
        
        # Storage options
        result["storage_options"] = self._get_storage_options(quantity_tons, location)
        
        # Transport suggestions
        result["transport_options"] = self._get_transport_options(quantity_tons, location)
        
        # Recommendations
        best_buyer = result["potential_buyers"][0]
        result["recommendations"].append(f"💰 Best offer: {best_buyer['buyer_name']} at ₹{best_buyer['estimated_offer']}/ton")
        result["recommendations"].append("📱 Register on e-NAM for wider market access")
        result["recommendations"].append("🤝 Verify buyer credentials before transaction")
        
        return result
    
    def _get_storage_options(self, quantity: float, location: str) -> List[Dict]:
        """Get storage facility options"""
        
        options = [
            {
                "facility": "Government Warehouse",
                "capacity": "500 tons",
                "cost_per_ton_per_month": 50,
                "location": f"Near {location}",
                "insurance": "Available",
                "quality_certification": "Yes"
            },
            {
                "facility": "Cold Storage (for perishables)",
                "capacity": "200 tons",
                "cost_per_ton_per_month": 200,
                "location": f"{location} Industrial Area",
                "insurance": "Included",
                "quality_certification": "Yes"
            },
            {
                "facility": "Private Warehouse",
                "capacity": "1000 tons",
                "cost_per_ton_per_month": 80,
                "location": f"{location} Highway",
                "insurance": "Optional",
                "quality_certification": "Yes"
            }
        ]
        
        return options
    
    def _get_transport_options(self, quantity: float, location: str) -> List[Dict]:
        """Get transport options"""
        
        options = [
            {
                "mode": "Road (Truck)",
                "capacity": "10-20 tons per vehicle",
                "cost_per_km": 15,
                "duration": "2-5 days (inter-state)",
                "suitable_for": "Short to medium distance"
            },
            {
                "mode": "Rail (Goods Train)",
                "capacity": "50+ tons",
                "cost_per_km": 8,
                "duration": "5-10 days",
                "suitable_for": "Long distance, bulk"
            },
            {
                "mode": "Local Transport",
                "capacity": "1-5 tons",
                "cost_per_km": 25,
                "duration": "Same day",
                "suitable_for": "Local mandi"
            }
        ]
        
        return options
