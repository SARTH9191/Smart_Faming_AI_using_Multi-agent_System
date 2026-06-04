# 🏗️ Smart Farming AI System - Architecture

## System Overview

The Smart Farming Agentic AI System is a comprehensive precision agriculture platform powered by 17 specialized AI agents working in coordination to optimize farming operations.
## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React)                          │
│  ┌────────────┬────────────┬────────────┬─────────────┐    │
│  │ Dashboard  │  Weather   │   Market   │ Blockchain  │    │
│  └────────────┴────────────┴────────────┴─────────────┘    │
│                Voice Assistant (Multilingual)                │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/REST API
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Backend (FastAPI)                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           Lead Agent (Orchestrator)                  │   │
│  │    • Coordinates all agents                          │   │
│  │    • Resolves conflicts                              │   │
│  │    • Makes global decisions                          │   │
│  └─────────────────────────────────────────────────────┘   │
│                              │                               │
│  ┌───────────────────────────┴──────────────────────────┐  │
│  │              Specialized Agents                       │  │
│  ├─────────────────────┬─────────────────────────────────┤ │
│  │ Core Farming        │ Economics & Gov              │ │
│  │ • Soil Agent        │ • Market Forecast            │ │
│  │ • Weather Collector │ • Market Integration         │ │
│  │ • Weather Forecast  │ • Govt Scheme                │ │
│  │ • Water Management  │                              │ │
│  │ • Fertilizer Agent  │ Advanced Sustainability      │ │
│  │ • Disease Detection │ • Blockchain Agent           │ │
│  │ • Yield Prediction  │ • Sustainability Agent       │ │
│  │                     │ • Drone/Satellite Agent      │ │
│  │                     │ • Climate Risk Agent         │ │
│  │                     │ • Voice Assistant Agent      │ │
│  └─────────────────────┴──────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              │
        ┌─────────────────────┴─────────────────────┐
        │                                             │
        ▼                                             ▼
┌────────────────┐                          ┌────────────────┐
│  SQLite DB     │                          │  Blockchain    │
│  • Sensors     │                          │  • Ledger      │
│  • Actions     │                          │  • Tokens      │
│  • Crops       │                          │  • Rewards     │
└────────────────┘                          └────────────────┘
```

## Component Breakdown

### 1. Frontend Layer (React)

**Components:**
- **Dashboard**: Real-time sensor monitoring, AI recommendations
- **Weather View**: Current weather + 24-hour forecast
- **Market View**: Price trends, optimal selling window
- **Blockchain View**: Green token wallet, transaction history
- **Voice Assistant**: Multilingual voice command interface

**Technology:**
- React 18
- Axios for API calls
- Responsive CSS Grid
- Speech Recognition API

### 2. Backend Layer (FastAPI)

**Main Components:**
- **FastAPI Server**: RESTful API endpoints
- **Lead Agent**: Master orchestrator
- **16 Specialized Agents**: Domain-specific intelligence
- **Database Manager**: SQLite operations
- **Sensor Simulator**: Test data generation

**Key Endpoints:**
```
POST /simulate_sensors     - Generate sensor data
POST /run_agents          - Execute all AI agents
GET  /dashboard           - Get complete dashboard data
GET  /get_weather         - Current weather
GET  /get_forecast        - Weather forecast
POST /predict_yield       - Crop yield prediction
POST /detect_disease      - Disease detection
GET  /get_market_forecast - Market prices
GET  /get_govt_schemes    - Government schemes
GET  /blockchain_log      - Blockchain transactions
POST /voice_command       - Voice assistant
```

### 3. AI Agents Layer

#### Lead Agent (Orchestrator)
- Coordinates execution of all agents
- Resolves conflicts (e.g., don't irrigate if rain predicted)
- Generates global recommendations
- Priority action determination

#### Core Farming Agents

**1. Soil Agent**
- Analyzes NPK levels, pH, moisture
- Soil health scoring
- Trend analysis
- Recommendations for soil improvement

**2. Weather Data Collector**
- Fetches real-time weather
- Integration ready for OpenWeatherMap API
- Simulated data for testing

**3. Weather Forecast Agent**
- 6hr/12hr/24hr/7-day predictions
- Rain probability calculation
- Weather risk scoring
- Farming recommendations based on forecast

**4. Water Management Agent**
- Smart irrigation scheduling
- Pump ON/OFF decisions
- Evaporation risk calculation
- Water volume optimization

**5. Fertilizer & Pesticide Agent**
- NPK requirement calculation
- Organic vs chemical options
- Eco-friendly pesticide recommendations
- Application timing

**6. Disease Detection Agent**
- Symptom-based detection
- Treatment recommendations
- Prevention strategies
- CNN-ready architecture for image analysis

**7. Crop Yield Prediction Agent**
- Multi-factor yield estimation
- Harvest date prediction
- Market value estimation
- Confidence scoring
- 

#### Economics & Government Agents

**8. Market Forecast Agent**
- Price trend prediction
- Best selling window identification
- Market insights (demand, supply, export)
- 30-day price forecast

**9. Market Integration Agent**
- Buyer matching
- e-NAM integration info
- Storage facility recommendations
- Transport options

**10. Government Scheme Agent**
- Applicable scheme identification
- Subsidy calculation
- Application support
- Claim template generation

#### Advanced Sustainability Agents

**11. Blockchain Agent**
- Mini blockchain implementation
- SHA-256 hash linking
- Green Token minting
- Transparent transaction log

**12. Sustainability Agent**
- Carbon footprint calculation
- Water footprint analysis
- Eco-practice identification
- Sustainability scoring (0-100)

**13. Drone & Satellite Agent**
- NDVI analysis simulation
- Soil health mapping
- Zone-wise health status
- Satellite climate prediction

**14. Climate Risk Agent**
- Drought/flood/heatwave prediction
- 30-day risk index
- Risk mitigation strategies
- Daily risk scoring

**15. Voice Assistant Agent**
- Multilingual support (English, Hindi, Marathi)
- Intent detection
- Voice-friendly responses
- Action execution


### 4. Data Layer

**SQLite Database Tables:**
```sql
sensor_data         - Real-time sensor readings
recommendations     - AI agent recommendations
crops              - Crop information
actions_log        - Farming actions history
```

**Blockchain Ledger:**
```json
{
  "chain": [blocks],
  "balances": {farm_id: tokens}
}
```

## Data Flow

1. **Sensor Data Collection**
   - Sensors generate readings (or simulated)
   - Stored in SQLite database
   - Available for agent analysis

2. **Agent Orchestration**
   - Lead Agent triggers execution
   - Agents analyze in priority order
   - Results aggregated

3. **Conflict Resolution**
   - Lead Agent identifies conflicts
   - Applies resolution rules
   - Generates final recommendations

4. **Blockchain Recording**
   - Sustainable actions logged
   - Green Tokens calculated
   - Block created and linked
   - Ledger updated

5. **Frontend Display**
   - API fetches latest data
   - Dashboard updates
   - Recommendations displayed
   - User takes action

## Scalability Considerations

1. **Agent Addition**: New agents can be added without modifying existing code
2. **Database**: Can migrate from SQLite to PostgreSQL for production
3. **API**: RESTful design allows multiple frontends
4. **Blockchain**: Can integrate with actual blockchain networks
5. **ML Models**: Placeholder for TensorFlow/PyTorch models

## Security Features

1. **Blockchain Integrity**: Cryptographic hash verification
2. **CORS Protection**: Configurable origins
3. **Input Validation**: Pydantic models
4. **Error Handling**: Graceful degradation

## Future Enhancements

1. Real weather API integration (OpenWeatherMap)
2. CNN model for disease detection (TensorFlow)
3. Time series forecasting (LSTM) for prices
4. IoT sensor integration (MQTT)
5. Mobile app (React Native)
6. Multi-farm management
7. SMS/WhatsApp notifications
8. Drone integration (DJI SDK)
9. Satellite imagery (Sentinel API)
10. Payment gateway for marketplace
