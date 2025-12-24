# 🛡️ SRS Ambiguity Guard

A comprehensive AI-powered tool for detecting and resolving ambiguity in Software Requirements Specifications (SRS). This application uses machine learning and Retrieval-Augmented Generation (RAG) to identify ambiguous requirements and provide clear, actionable rewrites.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## 🎯 Overview

SRS Ambiguity Guard is designed to help software engineers, requirements analysts, and QA specialists improve the quality of software requirements by:

- **Detecting Ambiguity**: Uses a fine-tuned DeBERTa model to identify ambiguous requirements
- **Resolving Ambiguity**: Leverages RAG (Retrieval-Augmented Generation) with Google Gemini to provide clear rewrites
- **Knowledge Base**: Built-in knowledge base with ISO standards, IREB glossary, and ambiguity rules
- **Batch Processing**: Analyze multiple requirements simultaneously
- **Export Results**: Generate comprehensive reports for documentation

## ✨ Features

### Core Functionality
- ✅ **AI-Powered Detection**: Fine-tuned DeBERTa model for accurate ambiguity detection
- ✅ **Intelligent Resolution**: RAG pipeline with hybrid retrieval (vector + keyword search)
- ✅ **Knowledge Base**: Pre-loaded with ISO 29148 standard, IREB glossary, and 15+ ambiguity rules
- ✅ **Batch Analysis**: Process multiple requirements in a single run
- ✅ **Evidence Tracking**: View sources and context used for each rewrite

### User Interface
- 🎨 **Modern UI**: Clean, intuitive Streamlit interface
- 📊 **Summary Statistics**: Quick overview of analysis results
- 📋 **Sentence Preview**: Preview how requirements will be split before processing
- 🔍 **Comparison View**: Side-by-side comparison of original vs. rewritten requirements
- 📥 **Export Reports**: Download detailed analysis reports

### Advanced Features
- 🔧 **Customizable Settings**: Adjust detection thresholds and evidence limits
- 📚 **Knowledge Base Management**: Upload custom documents to enhance the knowledge base
- ⏹️ **Stop Processing**: Interrupt long-running analyses
- 🛡️ **Error Handling**: Comprehensive error handling with user-friendly messages
- 📖 **Help Documentation**: Built-in help section with usage tips

## 🛠️ Technology Stack

### Machine Learning & AI
- **PyTorch**: Deep learning framework
- **Transformers (Hugging Face)**: Pre-trained models and tokenizers
- **DeBERTa**: Fine-tuned classification model for ambiguity detection
- **Sentence Transformers**: Dense embeddings for semantic search
- **Google Gemini 2.5 Flash**: LLM for requirement rewriting

### Data & Storage
- **ChromaDB**: Vector database for document storage and retrieval
- **BM25**: Keyword-based sparse retrieval
- **Cross-Encoder**: Re-ranking for improved relevance

### Web Framework
- **Streamlit**: Interactive web application framework

### Document Processing
- **PyMuPDF (fitz)**: PDF text extraction
- **JSON**: Structured data parsing

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Google Gemini API key (for LLM functionality)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd Project
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Download Model (if not included)

The DeBERTa classifier model should be in `./models/deberta_classifier/`. If missing, you'll need to train or download a fine-tuned model.

### Step 5: Set Up Environment Variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

To get a Gemini API key:
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the key to your `.env` file

## ⚙️ Configuration

### Default Paths

The application uses the following default paths (configurable in `app.py`):

- **Knowledge Base**: `./data/raw/` - Contains initial knowledge documents
- **Upload Directory**: `./data/user_uploads/` - Stores uploaded documents
- **Vector Database**: `./data/rag_db/` - ChromaDB storage location
- **Model Path**: `./models/deberta_classifier/` - Detection model location

### Knowledge Base Documents

The application comes with pre-loaded knowledge:

- **ISO 29148.pdf**: International standard for requirements engineering
- **ireb_cpre_glossary_SE_2.1.pdf**: IREB glossary of requirements engineering terms
- **ambiguity_rules.json**: 15 ambiguity detection rules with examples
- **glossary.json**: 24 key requirements engineering terms
- **template.txt**: Requirement templates for different types

## 🚀 Usage

### Starting the Application

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

### Basic Workflow

1. **Enter Requirements**
   - Type or paste requirements in the text area
   - Each sentence will be analyzed separately
   - Use the preview to verify sentence splitting

2. **Analyze**
   - Click "🔍 Analyze Batch" to process all requirements
   - Monitor progress with the progress bar
   - View real-time status updates

3. **Review Results**
   - Check summary statistics (total, clear, ambiguous, ambiguity rate)
   - Review detailed results with suggested rewrites
   - View evidence sources used for each rewrite

4. **Export**
   - Click "📥 Export Results" to download a comprehensive report
   - Report includes summary, detailed results, and evidence

### Batch Processing

1. Click "📄 Batch Processing" section
2. Upload a `.txt` file containing multiple requirements
3. The file content will be automatically loaded into the text area
4. Proceed with analysis as normal

### Enhancing Knowledge Base

1. Go to the sidebar "📚 Knowledge Base" section
2. Upload documents (PDF, JSON, or TXT)
3. Click "Process & Ingest"
4. Documents will be processed and added to the knowledge base
5. Future analyses will use the enhanced knowledge base

### Settings

#### Detection Settings
- **Confidence Threshold**: Adjust sensitivity (lower = more sensitive)
- **Show Confidence Scores**: Toggle confidence score display

#### Resolution Settings
- **Show AI Explanation**: Include explanations with rewrites
- **Max Evidence Items**: Limit number of evidence sources shown
- **Side-by-Side Comparison**: Toggle comparison view

## 📁 Project Structure

```
Project/
├── app.py                      # Main application entry point
├── ingest.py                   # Knowledge base ingestion script
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (create this)
├── README.md                   # This file
│
├── data/
│   ├── raw/                    # Initial knowledge base documents
│   │   ├── ISO29148.pdf
│   │   ├── ireb_cpre_glossary_SE_2.1.pdf
│   │   ├── ambiguity_rules.json
│   │   ├── glossary.json
│   │   └── template.txt
│   ├── rag_db/                 # ChromaDB vector database
│   └── user_uploads/           # User-uploaded documents
│
├── models/
│   └── deberta_classifier/     # Fine-tuned DeBERTa model
│
└── src/
    ├── core/                   # Core application logic
    │   ├── models.py           # Model loading
    │   └── processing.py       # Requirement processing
    │
    ├── ui/                     # UI components
    │   ├── sidebar.py          # Sidebar UI
    │   ├── main_panel.py       # Main panel UI
    │   └── results.py          # Results display
    │
    ├── utils/                  # Utility functions
    │   ├── report.py           # Report generation
    │   ├── text.py             # Text processing
    │   └── ui_helpers.py       # UI helpers
    │
    ├── detection.py            # Ambiguity detection model
    ├── resolution.py           # RAG resolution pipeline
    └── ingestion.py            # Document ingestion logic
```

## 🔍 How It Works

### 1. Ambiguity Detection

The application uses a fine-tuned DeBERTa model to classify requirements:

```
Input Requirement → Tokenization → DeBERTa Model → Classification (Clear/Ambiguous) + Confidence Score
```

### 2. Ambiguity Resolution (RAG Pipeline)

For ambiguous requirements, the system uses a hybrid RAG approach:

1. **Hybrid Retrieval**
   - **Dense Search**: Semantic similarity using Sentence Transformers
   - **Sparse Search**: Keyword matching using BM25
   - **RRF Fusion**: Combines both retrieval methods

2. **Re-ranking**
   - Cross-Encoder re-ranks top candidates
   - Selects top 5 most relevant documents

3. **Generation**
   - Context from retrieved documents is injected into prompt
   - Google Gemini generates clear rewrite
   - Evidence sources are tracked for citation

### 3. Knowledge Base

The knowledge base contains:
- **Standards**: ISO 29148 requirements engineering standard
- **Glossary**: IREB glossary with 100+ terms
- **Rules**: 15 ambiguity detection rules with examples
- **Templates**: Requirement templates for different types

## 🐛 Troubleshooting

### Common Issues

#### 1. Missing GEMINI_API_KEY Error

**Problem**: Application shows "Missing GEMINI_API_KEY" error

**Solution**:
- Create a `.env` file in the project root
- Add `GEMINI_API_KEY=your_key_here`
- Restart the application

#### 2. Model Not Found

**Problem**: Error loading DeBERTa model

**Solution**:
- Ensure `./models/deberta_classifier/` directory exists
- Check that model files are present (config.json, model.safetensors, etc.)
- If missing, you'll need to train or download the model

#### 3. Empty Knowledge Base

**Problem**: "Knowledge base is empty" warning

**Solution**:
- Run `python ingest.py` to load initial knowledge
- Or upload documents through the UI sidebar
- Check that `./data/raw/` contains documents

#### 4. Import Errors

**Problem**: ModuleNotFoundError when running

**Solution**:
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`
- Check that you're in the project root directory

#### 5. ChromaDB Errors

**Problem**: Database connection or corruption errors

**Solution**:
- Delete `./data/rag_db/` directory
- Restart application (it will recreate the database)
- Re-run ingestion if needed

### Performance Tips

- **GPU Acceleration**: If available, PyTorch will automatically use GPU for detection
- **Batch Size**: Process requirements in smaller batches for better responsiveness
- **Knowledge Base**: Keep knowledge base focused on relevant documents
- **API Limits**: Be aware of Gemini API rate limits for large batches

## 📊 Example Usage

### Example 1: Detecting Vague Quantifiers

**Input**:
```
The system should be fast. The login process must be quick.
```

**Output**:
- Requirement 1: ⚠️ **Ambiguous** (Confidence: 87%)
  - **Suggested Rewrite**: "The system shall respond to user requests within 200ms under normal load conditions."
  - **Evidence**: Retrieved from ambiguity_rules.json (Vague Quantifiers rule)

### Example 2: Resolving Passive Voice

**Input**:
```
The data is saved automatically.
```

**Output**:
- ⚠️ **Ambiguous** (Confidence: 92%)
  - **Suggested Rewrite**: "The System shall automatically save user data to the database after each transaction."
  - **Evidence**: Retrieved from ISO29148.pdf and ambiguity_rules.json

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- Additional ambiguity detection rules
- Support for more document formats
- Enhanced PDF processing
- Performance optimizations
- UI/UX improvements
- Additional language support

## 📝 License



## 🙏 Acknowledgments

- **ISO/IEEE 29148**: International standard for requirements engineering
- **IREB**: International Requirements Engineering Board for glossary
- **Hugging Face**: Pre-trained models and transformers library
- **Google**: Gemini API for LLM capabilities
- **Streamlit**: Web application framework

## 📧 Contact

swe2209842@xmu.edu.my

---

**Note**: This is a research/educational project. For production use, consider additional testing, security measures, and performance optimizations.

