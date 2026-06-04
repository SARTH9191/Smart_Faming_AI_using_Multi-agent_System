# 🔄 Agent Flow & Decision Logic

## Lead Agent Orchestration Flow

```
START
  │
  ├─► Get Latest Sensor Data
  │
  ├─► Execute Agents in Priority Order:
  │   │
  │   ├─► 1. Soil Agent (Foundation)
  │   │   └─► Analyze NPK, pH, moisture, temperature
  │   │
  │   ├─► 2. Weather Forecast Agent (Critical for decisions)
  │   │   └─► Predict rain, temperature, wind
  │   │
  │   ├─► 3. Water Management Agent (Critical)
  │   │   └─► Calculate irrigation need
  │   │   └─► Consider weather forecast
  │   │
  │   ├─► 4. Fertilizer Agent
  │   │   └─► Calculate NPK requirements
  │   │   └─► Recommend organic options
  │   │
  │   ├─► 5. Disease Detection Agent
  │   │   └─► Scan for diseases
  │   │   └─► Recommend treatment
  │   │
  │   ├─► 6. Yield Prediction Agent
  │   │   └─► Predict harvest yield
  │   │   └─► Calculate harvest date
  │   │
  │   └─► 7. Sustainability Agent
  │       └─► Calculate eco score
  │       └─► Track carbon/water footprint
  │
  ├─► Conflict Resolution
  │   │
  │   ├─► IF rain predicted AND irrigation recommended
  │   │   └─► POSTPONE irrigation
  │   │
  │   ├─► IF heavy rain AND fertilizer scheduled
  │   │   └─► POSTPONE fertilization
  │   │
  │   └─► IF disease detected AND harvest near
  │       └─► PRIORITIZE treatment
  │
  ├─► Generate Global Recommendations
  │   └─► Aggregate insights from all agents
  │   └─► Prioritize by criticality
  │
  ├─► Determine Priority Actions
  │   ├─► Critical: Disease control
  │   ├─► High: Irrigation
  │   └─► Medium: Fertilization
  │
  ├─► Store Recommendations in Database
  │
  └─► Return Results to Frontend
```

## Individual Agent Flows

### Soil Agent Flow

```
Input: Sensor Data (moisture, pH, NPK, temperature)
  │
  ├─► Evaluate Each Parameter
  │   ├─► Soil Moisture (30-70% optimal)
  │   ├─► pH Level (6.0-7.5 optimal)
  │   ├─► NPK Levels (crop-specific)
  │   └─► Temperature (15-28°C optimal)
  │
  ├─► Calculate Individual Scores (0-100)
  │
  ├─► Overall Health Score = Average(scores)
  │
  ├─► Determine Quality
  │   ├─► 80-100: Excellent
  │   ├─► 60-79: Good
  │   ├─► 40-59: Medium
  │   └─► 0-39: Poor
  │
  ├─► Generate Issues & Recommendations
  │
  └─► Output: Soil Health Report
```

### Weather Forecast Agent Flow

```
Input: Location, Forecast Duration
  │
  ├─► Fetch/Simulate Weather Data
  │   ├─► Temperature trends
  │   ├─► Rain probability
  │   ├─► Wind patterns
  │   └─► Humidity levels
  │
  ├─► Generate Hourly Forecast
  │   └─► For next 24-48 hours
  │
  ├─► Calculate Summary Statistics
  │   ├─► Average temperature
  │   ├─► Max/min temperature
  │   └─► Rain probability
  │
  ├─► Weather Risk Assessment
  │   ├─► High temperature risk (>38°C)
  │   ├─► Heavy rain risk (>80% prob)
  │   └─► Drought risk (<10% rain)
  │
  ├─► Generate Farming Recommendations
  │   ├─► IF rain > 60%: Postpone irrigation
  │   ├─► IF temp > 35°C: Increase watering
  │   └─► IF dry: Check water reserves
  │
  └─► Output: Weather Forecast Report
```

### Water Management Agent Flow

```
Input: Sensor Data + Weather Forecast
  │
  ├─► Check Soil Moisture Level
  │   └─► Threshold: 40%
  │
  ├─► Check Weather Prediction
  │   ├─► Rain expected? (>60% prob)
  │   └─► Rain probability
  │
  ├─► Decision Logic:
  │   │
  │   ├─► IF rain expected AND prob > 60%
  │   │   └─► DECISION: Don't irrigate
  │   │   └─► REASON: Rain will provide water
  │   │
  │   ├─► ELSE IF moisture < 40%
  │   │   ├─► DECISION: Irrigate
  │   │   ├─► Calculate Duration
  │   │   │   └─► base_time + (deficit * 2) minutes
  │   │   ├─► Calculate Volume
  │   │   │   └─► duration * 50 L/min
  │   │   └─► Check Evaporation Risk
  │   │       ├─► IF temp > 35°C AND humidity < 40%
  │   │       │   └─► RISK: High
  │   │       │   └─► RECOMMEND: Early morning/evening
  │   │       └─► ELSE: Normal timing OK
  │   │
  │   └─► ELSE
  │       └─► DECISION: No irrigation needed
  │
  ├─► Generate 7-Day Schedule
  │   └─► Every 2-3 days pattern
  │
  └─► Output: Irrigation Decision Report
```

### Disease Detection Agent Flow

```
Input: Crop Type, Symptoms (optional), Image (optional)
  │
  ├─► Load Disease Database for Crop
  │
  ├─► Detection Method:
  │   │
  │   ├─► IF image provided
  │   │   └─► [FUTURE] CNN Model Analysis
  │   │       ├─► Preprocess image
  │   │       ├─► Run through model
  │   │       └─► Get prediction + confidence
  │   │
  │   └─► ELSE (Current Implementation)
  │       └─► Simulation-based detection
  │           ├─► 30% chance of detection
  │           └─► Random disease from database
  │
  ├─► IF disease detected
  │   ├─► Retrieve disease information
  │   │   ├─► Symptoms
  │   │   ├─► Severity
  │   │   ├─► Treatment
  │   │   └─► Prevention
  │   │
  │   ├─► Generate Recommendations
  │   │   ├─► Immediate treatment steps
  │   │   ├─► Contact agronomist
  │   │   └─► Quarantine if needed
  │   │
  │   └─► Confidence Score (70-95%)
  │
  ├─► ELSE
  │   └─► Report: No disease detected
  │       └─► Continue monitoring
  │
  └─► Output: Disease Detection Report
```

### Market Forecast Agent Flow

```
Input: Crop Type, Days Ahead
  │
  ├─► Get Base Price for Crop
  │
  ├─► Determine Price Trend
  │   ├─► Rising
  │   ├─► Falling
  │   └─► Stable
  │
  ├─► Simulate Daily Prices
  │   └─► For next 30 days
  │       ├─► Apply trend direction
  │       ├─► Add random variation
  │       └─► Track max price & date
  │
  ├─► Calculate Market Insights
  │   ├─► Demand level
  │   ├─► Supply status
  │   ├─► Export demand
  │   └─► Seasonal factor
  │
  ├─► Identify Best Selling Window
  │   ├─► Date with highest price
  │   ├─► Expected price
  │   └─► Potential gain %
  │
  ├─► Generate Recommendations
  │   │
  │   ├─► IF trend = rising AND gain > 10%
  │   │   └─► HOLD for X days
  │   │
  │   ├─► ELSE IF trend = falling
  │   │   └─► SELL soon
  │   │
  │   └─► ELSE
  │       └─► SELL as per schedule
  │
  └─► Output: Market Forecast Report
```

### Blockchain Agent Flow

```
Input: Farm Action (type, details, farm_id)
  │
  ├─► Calculate Green Tokens Earned
  │   ├─► Drip irrigation: +20
  │   ├─► Organic fertilizer: +15
  │   ├─► Solar pump: +30
  │   ├─► Rainwater harvesting: +25
  │   └─► Other eco actions: +5-20
  │
  ├─► Create New Block
  │   ├─► Index = last_block.index + 1
  │   ├─► Timestamp = current time
  │   ├─► Data = action details + tokens
  │   ├─► Previous Hash = last_block.hash
  │   └─► Hash = SHA256(block data)
  │
  ├─► Validate Block
  │   └─► Check previous_hash matches
  │
  ├─► Add to Chain
  │   └─► chain.append(new_block)
  │
  ├─► Update Token Balance
  │   └─► balance[farm_id] += tokens
  │
  ├─► Save to Ledger File
  │   └─► JSON format
  │
  └─► Output: Transaction Receipt
```

### Climate Risk Agent Flow

```
Input: Location, Assessment Period (days)
  │
  ├─► Assess Individual Risks:
  │   │
  │   ├─► Drought Risk
  │   │   ├─► Rainfall deficit
  │   │   ├─► Soil moisture index
  │   │   └─► Temperature anomaly
  │   │
  │   ├─► Flood Risk
  │   │   ├─► Heavy rain probability
  │   │   └─► Watershed saturation
  │   │
  │   ├─► Heatwave Risk
  │   │   ├─► Max temperature forecast
  │   │   └─► Consecutive hot days
  │   │
  │   ├─► Frost Risk
  │   │   └─► Min temperature forecast
  │   │
  │   └─► Storm Risk
  │       ├─► Wind speed forecast
  │       └─► Storm probability
  │
  ├─► Calculate Risk Scores (0-100)
  │
  ├─► Overall Risk = Average(all risks)
  │
  ├─► Risk Level Classification
  │   ├─► 0-40: Low
  │   ├─► 41-70: Medium
  │   └─► 71-100: High
  │
  ├─► Generate Daily Risk Index
  │   └─► Next 30 days
  │       └─► Each day: risk score + primary threat
  │
  ├─► Create Mitigation Strategies
  │   └─► For each high-risk factor
  │
  └─► Output: Climate Risk Assessment
```

## Decision Conflict Resolution

### Irrigation vs Rain Conflict

```
IF water_agent.should_irrigate = TRUE
   AND weather_agent.rain_probability > 60%
THEN
   RESOLVE: Don't irrigate
   REASON: Rain will provide adequate water
   LOG: Conflict resolved - Irrigation postponed due to rain
```

### Fertilizer Application vs Heavy Rain

```
IF fertilizer_agent.recommended = TRUE
   AND weather_agent.rain_probability > 70%
THEN
   RESOLVE: Postpone fertilization
   REASON: Heavy rain will wash away nutrients
   RECOMMEND: Wait until after rain + 1-2 days
```

### Disease Treatment vs Harvest Timing

```
IF disease_agent.disease_detected = TRUE
   AND yield_agent.days_to_harvest < 7
THEN
   RESOLVE: Priority to disease control
   REASON: Disease can spread and reduce yield
   ACTION: Apply quick-acting organic treatment
```

## Priority Determination Logic

```
Priority Levels:
  CRITICAL (Act within 24 hours)
  HIGH (Act within 2-3 days)
  MEDIUM (Act within 1 week)
  LOW (Monitor regularly)

Assignment Rules:
  - Disease detected → CRITICAL
  - Soil moisture < 25% → CRITICAL
  - Irrigation needed → HIGH
  - Fertilizer deficit > 30% → HIGH
  - Market optimal window approaching → HIGH
  - pH adjustment needed → MEDIUM
  - Sustainability improvements → LOW
```
