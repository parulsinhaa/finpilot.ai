# FinPilot AI

FinPilot AI is an intelligent financial assistant designed to help users manage, analyze, and optimize their personal finances through simulations, AI-driven insights, and interactive dashboards. The application combines financial calculators, goal tracking, and scenario analysis into a unified platform with a modern UI built using Streamlit.

This repository contains the complete source code for the FinPilot AI application, including frontend interfaces, backend services, simulation engines, and deployment configurations.

---

## Features

- AI-powered financial assistant
- Interactive dashboards and analytics
- Financial calculators (EMI, savings, investments)
- Goal tracking and planning
- What-if scenario simulations
- Real-time insights and reports
- Multi-page UI with dynamic navigation
- Theme and currency customization

---

## Project Structure

```
finpilot.ai/
│
├── app/                  # Core application logic
│   ├── tasks/            # Task modules (easy, medium, hard)
│   ├── main.py           # Entry point
│   ├── ai_engine.py
│   ├── simulation_engine.py
│   └── calculators.py
│
├── backend/              # Backend services
│   ├── auth.py
│   ├── db.py
│   ├── currency.py
│   ├── notifications.py
│   └── payments.py
│
├── frontend/             # UI components (Streamlit pages)
│   ├── dashboard.py
│   ├── ai_chat.py
│   ├── goals.py
│   ├── reports.py
│   └── what_if.py
│
├── assets/               # Static files
│   ├── styles/
│   └── logo/
│
├── inference.py          # Model inference logic
├── requirements.txt      # Dependencies
├── Dockerfile            # Container configuration
└── openenv.yaml          # Deployment config
```

---

## Getting Started

### Prerequisites

Ensure the following are installed:

- Python 3.9+
- pip
- virtualenv (recommended)

---

### Installation

Clone the repository:

```bash
git clone https://github.com/parulsinhaa/FinPilot.ai.git
cd FinPilot.ai
```

Create and activate a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate    # Windows
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Running the Application

Start the Streamlit app:

```bash
streamlit run app/main.py
```

The application will be available at:

```
http://localhost:8501
```

---

## Environment Variables

Create a `.env` file in the root directory and add:

```env
API_BASE_URL=https://api.openai.com/v1
MODEL_NAME=gpt-4o-mini
OPENAI_API_KEY=your_openai_key
HF_TOKEN=your_huggingface_token
```

These variables are required for AI functionality and external integrations.

---

## Deployment

### Hugging Face Spaces

1. Push the repository to Hugging Face Spaces
2. Add the required secrets in Space Settings:
   - API_BASE_URL
   - MODEL_NAME
   - OPENAI_API_KEY
   - HF_TOKEN
3. Ensure `openenv.yaml` and `requirements.txt` are properly configured

---

### Docker Deployment

Build and run using Docker:

```bash
docker build -t finpilot-ai .
docker run -p 8501:8501 finpilot-ai
```

---

## Troubleshooting

- **UI not loading properly**  
  Ensure `assets/styles/main.css` is correctly loaded

- **Pages not visible**  
  Check `st.session_state.current_page` routing logic

- **API errors**  
  Verify `.env` variables are set correctly

- **Deployment UI broken on Hugging Face**  
  Confirm correct working directory and file paths

---

## Contributing

Contributions are welcome. To contribute:

1. Fork the repository
2. Create a new branch
3. Make changes
4. Submit a pull request

---

## License

This project is for educational and hackathon purposes. Licensing can be added as required.

---

## Acknowledgements

FinPilot AI is built as part of a hackathon project focused on combining financial intelligence with AI-driven user experiences.
