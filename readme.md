# Customer Support Agent

A simple but industry-standard customer support agent that can access transaction data and maintain conversation memory. This system uses Python with MongoDB for storing payment records, Chroma for conversation memory, and Gemini for the language model.

## Project Structure

```
customer-support-agent/
├── .env.example                # Environment variable template
├── config.py                   # Configuration settings
├── db_module.py                # MongoDB connection and payment data retrieval
├── memory_module.py            # Chroma-based conversation memory
├── llm_module.py               # Gemini API integration
├── agent_module.py             # Main agent logic integrating all components
├── main.py                     # FastAPI web server
├── cli.py                      # Command-line interface for testing
└── requirements.txt            # Project dependencies
```

## Features

- Conversation memory persistence with ChromaDB
- MongoDB integration for payment data storage and retrieval
- Natural language processing with Gemini API
- Payment ID detection in user messages
- RESTful API with FastAPI
- CLI testing interface

## Installation

1. Clone the repository
2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```
4. Copy the `.env.example` file to `.env` and fill in your own settings:
```bash
cp .env.example .env
```
5. Update the `.env` file with your Gemini API key (get from https://aistudio.google.com/)

## Usage

### Start the API server:
```bash
python main.py
```

### Use the CLI client for testing:
```bash
python cli.py
```

### Via API:
- Send messages: `POST /message`
- Get conversation history: `GET /conversation/{conversation_id}`
- Reset conversation: `DELETE /conversation/{conversation_id}`

## Sample Data

The system automatically initializes with sample payment data:
- PAY123456: Premium Headphones ($129.99)
- PAY789012: Wireless Mouse + USB-C Cable ($75.50)
- PAY345678: Smart Watch ($199.95)

## How It Works

1. User sends a message to the API
2. System checks for payment IDs in the message
3. If a payment ID is found, payment info is retrieved from MongoDB
4. Conversation history is loaded from Chroma
5. All data is sent to Gemini to generate a response
6. Response is returned to the user and stored in memory

## Tool Calling Process

The system demonstrates a practical implementation of tool calling:
1. LLM identifies payment IDs in messages
2. Database lookup tool retrieves payment information
3. Memory tool accesses conversation history
4. LLM tool generates appropriate responses
5. Memory tool stores the conversation