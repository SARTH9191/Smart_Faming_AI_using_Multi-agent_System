"""
Sensor Simulator - Generate Realistic Farm Sensor Data
"""
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

class SensorSimulator:
    def __init__(self):
        self.base_values = {
            'soil_moisture': 45.0,  # %
            'soil_ph': 6.5,
            'soil_temperature': 22.0,  # Celsius
            'air_temperature': 25.0,  # Celsius
            'humidity': 60.0,  # %
            'rainfall': 0.0,  # mm
            'light_intensity': 50000,  # lux
            'npk_nitrogen': 40,  # mg/kg
            'npk_phosphorus': 25,  # mg/kg
            'npk_potassium': 35  # mg/kg
        }
    
    def generate_sensor_data(self, farm_id: str = "FARM001", 
                            duration_minutes: int = 1) -> List[Dict[str, Any]]:
        """Generate simulated sensor data"""
        readings = []
        
        for i in range(duration_minutes):
            timestamp = datetime.now() - timedelta(minutes=duration_minutes - i)
            
            # Add realistic variations
            reading = {
                'farm_id': farm_id,
                'timestamp': timestamp.isoformat(),
                'soil_moisture': self._vary(self.base_values['soil_moisture'], 5),
                'soil_ph': self._vary(self.base_values['soil_ph'], 0.3),
                'soil_temperature': self._vary(self.base_values['soil_temperature'], 2),
                'air_temperature': self._vary(self.base_values['air_temperature'], 3),
                'humidity': self._vary(self.base_values['humidity'], 10),
                'rainfall': max(0, self._vary(self.base_values['rainfall'], 0.5)),
                'light_intensity': self._vary(self.base_values['light_intensity'], 10000),
                'npk_nitrogen': self._vary(self.base_values['npk_nitrogen'], 5),
                'npk_phosphorus': self._vary(self.base_values['npk_phosphorus'], 3),
                'npk_potassium': self._vary(self.base_values['npk_potassium'], 4)
            }
            
            readings.append(reading)
        
        return readings
    
    def _vary(self, base_value: float, variance: float) -> float:
        """Add random variation to base value"""
        variation = random.uniform(-variance, variance)
        return round(base_value + variation, 2)
    
    def simulate_weather_event(self, event_type: str):
        """Simulate weather events like rain, drought"""
        if event_type == "rain":
            self.base_values['rainfall'] = random.uniform(5, 20)
            self.base_values['humidity'] = random.uniform(75, 95)
            self.base_values['soil_moisture'] = min(100, self.base_values['soil_moisture'] + 15)
        elif event_type == "drought":
            self.base_values['rainfall'] = 0
            self.base_values['humidity'] = random.uniform(20, 40)
            self.base_values['soil_moisture'] = max(20, self.base_values['soil_moisture'] - 10)
        elif event_type == "heatwave":
            self.base_values['air_temperature'] = random.uniform(35, 45)
            self.base_values['soil_temperature'] = random.uniform(28, 35)
