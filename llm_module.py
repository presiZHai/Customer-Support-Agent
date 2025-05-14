import google.generativeai as genai
import re
from typing import Dict, Any, Optional
from config import GEMINI_API_KEY, GEMINI_MODEL, SYSTEM_PROMPT

class LLMProcessor:
    """
    Handles interactions with the Gemini API for natural language processing
    """
    def __init__(self):
        """Initialize the LLM processor with the Gemini API"""
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(GEMINI_MODEL)
        print(f"Initialized Gemini model: {GEMINI_MODEL}")
    
    def process_message(self, 
                         user_message: str, 
                         conversation_history: str,
                         payment_info: Optional[Dict[str, Any]] = None) -> str:
        """
        Process a user message and generate a response
        
        Args:
            user_message (str): The current user message
            conversation_history (str): Previous conversation context
            payment_info (Dict[str, Any], optional): Payment details if available
            
        Returns:
            str: The generated response
        """
        # Build the prompt with relevant information
        prompt = self._build_prompt(user_message, conversation_history, payment_info)
        
        # Generate response from Gemini
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error generating response: {e}")
            return "I'm having trouble processing your request right now. Could you try again?"
    
    def extract_payment_id(self, message: str) -> Optional[str]:
        """
        Extract a potential payment ID from the user message
        
        Args:
            message (str): The user message
            
        Returns:
            Optional[str]: The extracted payment ID or None
        """
        # Simple regex pattern to match payment IDs (e.g., PAY123456)
        pattern = r'\b(PAY[A-Z0-9]{6,10})\b'
        match = re.search(pattern, message, re.IGNORECASE)
        
        if match:
            return match.group(1).upper()  # Normalize to uppercase
        return None
    
    def _build_prompt(self, 
                     user_message: str, 
                     conversation_history: str,
                     payment_info: Optional[Dict[str, Any]] = None) -> str:
        """
        Build a prompt for the LLM with all relevant context
        
        Args:
            user_message (str): The current user message
            conversation_history (str): Previous conversation context
            payment_info (Dict[str, Any], optional): Payment details if available
            
        Returns:
            str: The complete prompt for the LLM
        """
        prompt_parts = [
            SYSTEM_PROMPT,
            "\n\n",
            conversation_history,
            "\n\n"
        ]
        
        # Include payment information if available
        if payment_info:
            prompt_parts.append("Payment Information:\n")
            prompt_parts.append(f"ID: {payment_info['payment_id']}\n")
            prompt_parts.append(f"Customer: {payment_info['customer_name']}\n")
            prompt_parts.append(f"Amount: {payment_info['amount']} {payment_info['currency']}\n")
            prompt_parts.append(f"Status: {payment_info['status']}\n")
            prompt_parts.append("Items:\n")
            for item in payment_info['items']:
                prompt_parts.append(f"- {item['name']} (Qty: {item['quantity']}) - {item['price']} {payment_info['currency']}\n")
            prompt_parts.append("\n")
        
        # Add the current message
        prompt_parts.append("Current customer message: " + user_message)
        prompt_parts.append("\n\nProvide a helpful, professional customer support response.")
        
        return "".join(prompt_parts)

# Testing functionality
if __name__ == "__main__":
    # Sample data for testing
    llm = LLMProcessor()
    
    # Test payment ID extraction
    test_message = "My payment ID is PAY123456 and I haven't received my order yet."
    payment_id = llm.extract_payment_id(test_message)
    print(f"Extracted payment ID: {payment_id}")
    
    # Test prompt building
    sample_payment = {
        "payment_id": "PAY123456",
        "customer_name": "John Doe",
        "customer_email": "john.doe@example.com",
        "amount": 129.99,
        "currency": "USD",
        "status": "completed",
        "items": [
            {"name": "Premium Headphones", "quantity": 1, "price": 129.99}
        ],
        "date": "2025-05-10T14:30:45"
    }
    
    prompt = llm._build_prompt(
        user_message="Where is my order? I ordered headphones three days ago.",
        conversation_history="Customer: Hi, I need help with my order.\nSupport Agent: I'd be happy to help! Could you provide your order or payment ID?",
        payment_info=sample_payment
    )
    
    print("\nGenerated Prompt:")
    print(prompt)