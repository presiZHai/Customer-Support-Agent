import unittest
from unittest.mock import MagicMock, patch
from agent_module import CustomerSupportAgent
from db_module import PaymentDatabase
from memory_module import ConversationMemory
from llm_module import LLMProcessor

class TestCustomerSupportAgent(unittest.TestCase):
    """
    Unit tests for the CustomerSupportAgent and its components
    """
    
    def setUp(self):
        """Set up test fixtures"""
        # Mock dependencies
        self.mock_db = MagicMock(spec=PaymentDatabase)
        self.mock_memory = MagicMock(spec=ConversationMemory)
        self.mock_llm = MagicMock(spec=LLMProcessor)
        
        # Create patches
        self.db_patch = patch('agent_module.PaymentDatabase', return_value=self.mock_db)
        self.memory_patch = patch('agent_module.ConversationMemory', return_value=self.mock_memory)
        self.llm_patch = patch('agent_module.LLMProcessor', return_value=self.mock_llm)
        
        # Start patches
        self.db_patch.start()
        self.memory_patch.start()
        self.llm_patch.start()
        
        # Sample payment data
        self.sample_payment = {
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
        
        # Create the agent
        self.agent = CustomerSupportAgent("test_convo_id")
    
    def tearDown(self):
        """Clean up after tests"""
        self.db_patch.stop()
        self.memory_patch.stop()
        self.llm_patch.stop()
    
    def test_process_message_with_payment_id(self):
        """Test processing a message containing a payment ID"""
        # Setup mocks
        self.mock_llm.extract_payment_id.return_value = "PAY123456"
        self.mock_db.get_payment_by_id.return_value = self.sample_payment
        self.mock_memory.format_for_prompt.return_value = "Previous conversation history"
        self.mock_llm.process_message.return_value = "I can see your order for Premium Headphones is completed."
        
        # Execute
        response = self.agent.process_user_message("What's the status of PAY123456?")
        
        # Assert
        self.mock_llm.extract_payment_id.assert_called_once_with("What's the status of PAY123456?")
        self.mock_db.get_payment_by_id.assert_called_once_with("PAY123456")
        self.mock_memory.format_for_prompt.assert_called_once()
        self.mock_llm.process_message.assert_called_once()
        self.mock_memory.add_message.assert_called()
        self.assertEqual(response, "I can see your order for Premium Headphones is completed.")
    
    def test_process_message_without_payment_id(self):
        """Test processing a message without a payment ID"""
        # Setup mocks
        self.mock_llm.extract_payment_id.return_value = None
        self.mock_memory.format_for_prompt.return_value = "Previous conversation history"
        self.mock_llm.process_message.return_value = "Can you provide your payment ID so I can look up your order?"
        
        # Execute
        response = self.agent.process_user_message("What's the status of my order?")
        
        # Assert
        self.mock_llm.extract_payment_id.assert_called_once_with("What's the status of my order?")
        self.mock_db.get_payment_by_id.assert_not_called()
        self.mock_memory.format_for_prompt.assert_called_once()
        self.mock_llm.process_message.assert_called_once()
        self.mock_memory.add_message.assert_called()
        self.assertEqual(response, "Can you provide your payment ID so I can look up your order?")
    
    def test_reset_conversation(self):
        """Test resetting a conversation"""
        # Execute
        self.agent.reset_conversation()
        
        # Assert
        self.mock_memory.clear_conversation.assert_called_once()
    
    def test_close(self):
        """Test closing the agent's connections"""
        # Execute
        self.agent.close()
        
        # Assert
        self.mock_db.close.assert_called_once()

class TestLLMProcessor(unittest.TestCase):
    """
    Unit tests for the LLMProcessor
    """
    
    @patch('llm_module.genai')
    def setUp(self, mock_genai):
        """Set up test fixtures"""
        self.llm = LLMProcessor()
        self.mock_genai = mock_genai
    
    def test_extract_payment_id(self):
        """Test payment ID extraction"""
        # Test various formats
        self.assertEqual(self.llm.extract_payment_id("My payment id is PAY123456"), "PAY123456")
        self.assertEqual(self.llm.extract_payment_id("Order number: pay987654"), "PAY987654")
        self.assertEqual(self.llm.extract_payment_id("No payment ID here"), None)
        self.assertEqual(self.llm.extract_payment_id("Invalid ID: XYZ123456"), None)

if __name__ == '__main__':
    unittest.main()