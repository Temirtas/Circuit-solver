# ⚡ AI Circuit Solver

🔗 **Live demo:** [circuit-solver-xi.vercel.app](https://circuit-solver-xi.vercel.app)

Upload a photo of a circuit diagram with a question, and get a step-by-step AI-generated solution — like a worked textbook answer.

## How it works
1. Upload an image of a circuit diagram (hand-drawn, printed, or digital) along with a question
2. The image is sent to a vision-capable AI model via [GitHub Models](https://github.com/marketplace/models)
3. The AI identifies the components, solves the problem, and returns a structured, step-by-step breakdown
4. Results are displayed with highlighted key values, similar to a textbook solution

## Tech stack
- **Backend**: Python, Flask
- **AI**: GPT-4o via GitHub Models (OpenAI-compatible API)
- **Frontend**: HTML, CSS, vanilla JavaScript

## Setup

1. Clone this repo
```bash
git clone <your-repo-url>
cd circuit-solver
```

2. Create a virtual environment and install dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with your own GitHub token:
GITHUB_TOKEN=your_github_personal_access_token
You can generate a token at GitHub → Settings → Developer settings → Personal access tokens.

4. Run the app
```bash
python3 app.py
```

5. Open `http://127.0.0.1:5000` in your browser

## Disclaimer
AI-generated solutions may occasionally contain errors, especially on complex circuits. Always verify important results independently.