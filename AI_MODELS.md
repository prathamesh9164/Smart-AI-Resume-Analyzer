# AI Models in Smart Resume Analyzer

Smart Resume Analyzer uses advanced AI models to provide detailed analysis and feedback on your resume. This document explains the AI models integrated into the application and how they work.

## Available AI Models

### 1. Groq

Groq is a powerful AI model provider that offers fast, OpenAI-compatible language model inference. In Smart Resume Analyzer, Groq is used to:

- Analyze resume content and structure
- Identify key skills and missing skills for target roles
- Provide personalized recommendations for improvement
- Score resumes based on quality and relevance

## How AI Analysis Works

When you upload your resume for AI analysis, the following process occurs:

1. **Text Extraction**: The system extracts text from your PDF or DOCX resume
2. **AI Processing**: Groq analyzes the resume text
3. **Structured Analysis**: The AI generates a structured analysis including:
   - Overall assessment
   - Skills analysis (current and missing skills)
   - Strengths
   - Areas for improvement
   - Recommended courses
   - Resume score (0-100)

## Configuring AI Models

To use these AI models, you need to set up API keys in your `.env` file:

```
# API Keys for AI Models
GROQ_API_KEY=your_groq_api_key_here

# Optional: model used by default when the app starts
GROQ_MODEL=qwen/qwen3.8-27b

# Optional: comma-separated model IDs shown in the app's model selector
GROQ_MODELS=qwen/qwen3.8-27b,llama-3.3-70b-versatile,llama-3.1-8b-instant,meta-llama/llama-4-scout-17b-16e-instruct
```

- For Groq, you need an API key from [Groq Console](https://console.groq.com)
- The **AI model** selector on the Resume Analyzer page controls analysis, JD matching, generated content, and chat.
- Use **Compare this analysis with another model** below a role-based analysis to compare scores and summaries.
- Model IDs must be enabled for your Groq account. You can override the displayed list with `GROQ_MODELS`.

## Privacy and Data Handling

When using the AI analysis features:

- Resume data is sent to the respective AI model providers (Groq)
- Analysis results are stored in the local database for reference
- No personal data is shared with third parties beyond what's necessary for analysis
- You can delete your data at any time through the application

## Future AI Integrations

We plan to integrate additional AI models in the future to provide even more comprehensive resume analysis and feedback. Stay tuned for updates! 