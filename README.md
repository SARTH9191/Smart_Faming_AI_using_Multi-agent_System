# 🌾 Smart Farming Agentic AI System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React 18.2](https://img.shields.io/badge/react-18.2-61dafb.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com/)

## 📖 Overview
A comprehensive AI-powered smart farming system with **17 specialized agents**, blockchain-based rewards, real-time monitoring, and a farmer-friendly multilingual dashboard. This system helps farmers make data-driven decisions for precision agriculture.

## ✨ Features

### 🤖 AI Agent System
- **Lead Agent** - Orchestrates all farming operations
- **Soil Analysis Agent** - Monitors soil health and nutrients
- **Weather Collector Agent** - Real-time weather data integration
- **Weather Forecast Agent** - Predictive weather analysis
- **Water Management Agent** - Smart irrigation recommendations
- **Fertilizer Agent** - Optimal fertilization planning
- **Disease Detection Agent** - Early disease identification
- **Yield Prediction Agent** - Harvest forecasting
- **Market Forecast Agent** - Price trend analysis
- **Market Integration Agent** - Direct market access
- **Government Scheme Agent** - Subsidy and scheme recommendations
- **Blockchain Agent** - Transparent reward system
- **Sustainability Agent** - Eco-friendly farming practices
- **Drone/Satellite Agent** - Aerial crop monitoring
- **Climate Risk Agent** - Risk assessment and mitigation
- **Voice Assistant Agent** - Voice-controlled operations
- **Speech Recognition Agent** - Multilingual voice processing

### 🎯 Core Capabilities
- 🌦️ **Real-time Weather Integration** - Live weather updates and forecasts
- 💧 **Smart Irrigation Management** - Water optimization based on soil and weather
- 🔬 **Disease Detection** - AI-powered crop disease identification
- 📊 **Yield Prediction** - Data-driven harvest forecasting
- 💰 **Market Price Forecasting** - Price trend analysis and recommendations
- 🏛️ **Government Scheme Integration** - Automatic subsidy eligibility checking
- ⛓️ **Blockchain Green Token Rewards** - Earn tokens for sustainable practices
- 🎤 **Voice Assistant** - Multilingual voice commands (English, Hindi, Marathi)
- 📱 **Mobile-Friendly Dashboard** - Responsive design for all devices
- 🔒 **Secure Authentication** - SHA-256 hashed passwords with session management

## 🛠️ Tech Stack

| Category | Technology |
|----------|-----------|
| **Backend** | FastAPI + Python 3.11+ |
| **Frontend** | React 18.2 + Modern CSS |
| **Database** | SQLite + JSON |
| **Blockchain** | Custom Implementation (SHA-256) |
| **AI Architecture** | Multi-Agent System (17 Agents) |
| **Voice Recognition** | Google Speech Recognition API |
| **Security** | SHA-256 Hashing + Session Tokens |
| **API Documentation** | OpenAPI (Swagger) |

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- Node.js 16+ and npm
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/smart-farming-ai.git
cd smart-farming-ai
```

2. **Backend Setup**
```bash
cd backend
pip install -r requirements.txt
```

3. **Frontend Setup**
```bash
cd frontend
npm install
```

### Running the Application

**Option 1: Using Batch Files (Windows)**
```bash
# Start backend
start_backend.bat

# Start frontend (in a new terminal)
start_frontend.bat
```

**Option 2: Manual Start**
```bash
# Terminal 1 - Backend
cd backend
python main.py

# Terminal 2 - Frontend
cd frontend
npm start
```

### Access Points
- 🌐 **Frontend Dashboard**: http://localhost:3000
- 🔧 **Backend API**: http://localhost:8000
- 📚 **API Documentation**: http://localhost:8000/docs
- 📖 **ReDoc**: http://localhost:8000/redoc

### Default Login Credentials
```
Username: testfarmer
Password: secure123
```

## 📁 Project Structure
```
smart-farming-ai/
├── backend/              # FastAPI backend server
│   ├── agents/          # 17 specialized AI agents
│   ├── core/            # Core systems (auth, database, sensors)
│   ├── main.py          # FastAPI application entry point
│   └── requirements.txt # Python dependencies
├── frontend/            # React frontend application
│   ├── src/             # React components and logic
│   ├── public/          # Static assets
│   └── package.json     # Node dependencies
├── blockchain/          # Blockchain ledger and logic
│   └── ledger.json      # Green token transactions
├── database/            # SQLite databases
├── data/                # Sample crop and market data
├── docs/                # Detailed documentation
│   ├── architecture.md  # System architecture
│   └── agent_flow.md    # Agent workflow diagrams
└── README.md            # This file
```

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [QUICKSTART.md](QUICKSTART.md) | Fast setup guide |
| [INSTALLATION.md](INSTALLATION.md) | Detailed installation steps |
| [COMPLETE_API_DOCUMENTATION.md](COMPLETE_API_DOCUMENTATION.md) | Full API reference |
| [VOICE_ASSISTANT_COMPLETE_GUIDE.md](VOICE_ASSISTANT_COMPLETE_GUIDE.md) | Voice features guide |
| [BLOCKCHAIN_IMPLEMENTATION_GUIDE.md](BLOCKCHAIN_IMPLEMENTATION_GUIDE.md) | Blockchain system details |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution guidelines |

## 🎯 Use Cases

1. **Precision Agriculture** - Data-driven farming decisions
2. **Resource Optimization** - Efficient water and fertilizer use
3. **Early Disease Detection** - Prevent crop losses
4. **Market Intelligence** - Better selling decisions
5. **Sustainable Farming** - Earn rewards for eco-friendly practices
6. **Government Benefits** - Easy access to subsidies and schemes

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to get started.

### Ways to Contribute
- 🐛 Report bugs and issues
- 💡 Suggest new features
- 🔧 Submit pull requests
- 📝 Improve documentation
- 🌍 Add language support

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Weather data powered by OpenWeatherMap API
- Voice recognition using Google Speech API
- Inspired by precision agriculture research

## 📧 Contact & Support

For questions, suggestions, or support:
- 📬 Open an issue on GitHub
- 📖 Check the [documentation](docs/)
- 💬 Start a discussion in the Discussions tab

## 🌟 Star History

If you find this project useful, please consider giving it a star! ⭐

---

**Made with ❤️ for farmers worldwide** 🌾
