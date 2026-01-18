"""
SRUTHI-AI Brain Module - 100% Offline
LLM integration using local GGUF models only (no internet required)
"""

import os
import sys
import re
from typing import Optional
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import config
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.config import (
    GGUF_MODEL_PATH, GGUF_USE_GPU, GGUF_GPU_LAYERS,
    GGUF_CONTEXT_SIZE, GGUF_MAX_TOKENS, GGUF_TEMPERATURE,
    GGUF_TIMEOUT, DEBUG_MODE, AUTO_SAVE_CONVERSATIONS, AUTO_SAVE_THRESHOLD
)
from core.memory import Memory
from intelligence.command_parser import parse_and_execute


class AIBrain:
    """Offline AI brain using local GGUF models only"""
    
    def __init__(self, model_path: str = GGUF_MODEL_PATH, document_processor=None):
        """Initialize the offline AI brain with optional document processor for RAG"""
        self.model_path = model_path
        self.conversation_history = []
        self.memory = Memory()
        self.llm_gguf = None
        self.document_processor = document_processor  # For RAG functionality
        self.current_model = "Local GGUF (Offline)"
        
        # Get user name
        user_name = self.memory.get_user_name()
        self.user_name = user_name if user_name else "there"
        
        # Initialize offline model (GGUF)
        if os.path.exists(self.model_path):
            print(f"🧠 Loading offline GGUF model: {Path(self.model_path).name}")
            self._initialize_gguf()
        else:
            print(f"⚠️  GGUF model not found at: {self.model_path}")
            print(f"   Please download a GGUF model and update the path in .env")
            raise FileNotFoundError(f"GGUF model not found: {self.model_path}")
        
        print(f"✅ AI Brain initialized! User: {self.user_name}")
        print(f"   Mode: 100% Offline (No Internet Required)")
    
    def _initialize_gguf(self):
        """Initialize GGUF model"""
        try:
            from llama_cpp import Llama
            
            n_gpu_layers = GGUF_GPU_LAYERS if GGUF_USE_GPU else 0
            
            print(f"   GPU Layers: {n_gpu_layers}")
            print(f"   Context Size: {GGUF_CONTEXT_SIZE}")
            
            self.llm_gguf = Llama(
                model_path=self.model_path,
                n_ctx=GGUF_CONTEXT_SIZE,
                n_gpu_layers=n_gpu_layers,
                verbose=DEBUG_MODE
            )
            
            print("✅ GGUF model loaded successfully")
            
        except ImportError:
            print("❌ llama-cpp-python not installed!")
            print("   Install with: pip install llama-cpp-python")
            raise
        except Exception as e:
            print(f"❌ Failed to load GGUF model: {e}")
            raise
    
    def _get_system_prompt(self) -> str:
        """Generate system prompt with memory context"""
        user_name = self.memory.get_user_name() or "there"
        
        return f"""You are SRUTHI-AI, a helpful AI assistant running completely offline.
User: {user_name}

I can help with:
- Programming and coding questions
- Daily conversations and general knowledge
- Reminders, contacts, and information storage
- Suggestions and advice

Keep responses natural, friendly, and concise. I work 100% offline to protect your privacy."""
    
    def _parse_memory_commands(self, user_input: str) -> Optional[str]:
        """Parse and execute memory-related commands"""
        input_lower = user_input.lower()
        
        # "My name is X"
        if match := re.search(r"my name is (\w+)", input_lower):
            name = match.group(1).capitalize()
            self.memory.set_user_name(name)
            self.user_name = name
            return f"Nice to meet you, {name}! I'll remember that. 😊"
        
        # "Add contact X with phone Y"
        if match := re.search(r"add contact (\w+)(?: with phone | phone )?(\+?[\d\-]+)", input_lower):
            name = match.group(1).capitalize()
            phone = match.group(2)
            self.memory.add_contact(name, phone=phone)
            return f"✅ Added {name} ({phone}) to your contacts."
        
        # "Who is X?"
        if match := re.search(r"(?:who is|do you know) (\w+)", input_lower):
            name = match.group(1).capitalize()
            contact = self.memory.get_contact(name)
            if contact:
                phone = contact.get('phone', 'No phone')
                return f"📞 {name}: {phone}"
            return f"I don't have any information about {name}."
        
        # "List contacts"
        if "list contacts" in input_lower or "show contacts" in input_lower:
            contacts = self.memory.list_contacts()
            if not contacts:
                return "You don't have any contacts saved yet."
            result = "📇 Your contacts:\n"
            for contact in contacts:
                result += f"  • {contact['name']}: {contact.get('phone', 'No phone')}\n"
            return result.strip()
        
        # "Remind me to X"
        if "remind me" in input_lower:
            desc = re.sub(r"remind me to ", "", user_input, flags=re.IGNORECASE).strip()
            remind_time = datetime.now().replace(hour=9, minute=0, second=0) + timedelta(days=1)
            self.memory.add_reminder(desc, remind_time)
            return f"⏰ I'll remind you tomorrow at 9 AM: {desc}"
        
        # "Set timer for X minutes"
        if match := re.search(r"set (?:a )?timer for (\d+) (?:minute|min)", input_lower):
            minutes = int(match.group(1))
            self.memory.start_timer(minutes * 60, label=f"{minutes}-minute timer")
            return f"⏲️ Timer started for {minutes} minutes!"
        
        return None
    
    def _ask_gguf(self, prompt: str) -> Optional[str]:
        """Query local GGUF model"""
        try:
            # Build messages
            messages = [{"role": "system", "content": self._get_system_prompt()}]
            
            # Add recent history
            if self.conversation_history:
                recent = self.conversation_history[-10:]
                messages.extend(recent)
            
            messages.append({"role": "user", "content": prompt})
            
            # Generate response
            response = self.llm_gguf.create_chat_completion(
                messages=messages,
                max_tokens=GGUF_MAX_TOKENS,
                temperature=GGUF_TEMPERATURE,
                stop=["User:", "Human:", "\n\n\n"]
            )
            
            return response["choices"][0]["message"]["content"].strip()
            
        except Exception as e:
            if DEBUG_MODE:
                print(f"GGUF error: {e}")
            return None
    
    def ask(self, prompt: str, use_history: bool = True) -> Optional[str]:
        """
        Send prompt to local GGUF model with RAG context (100% offline)
        """
        try:
            # Check for system commands first
            is_command, command_result = parse_and_execute(prompt)
            if is_command:
                if command_result and command_result.get('success'):
                    response = command_result.get('message', 'Command executed successfully')
                else:
                    error_msg = command_result.get('error', 'Command failed') if command_result else 'Unknown error'
                    response = f"I tried to execute that command, but encountered an error: {error_msg}"
                self.conversation_history.append({"role": "user", "content": prompt})
                self.conversation_history.append({"role": "assistant", "content": response})
                self._auto_save_conversation()
                return response
            
            # Check for memory commands
            memory_response = self._parse_memory_commands(prompt)
            if memory_response:
                self.conversation_history.append({"role": "user", "content": prompt})
                self.conversation_history.append({"role": "assistant", "content": memory_response})
                self._auto_save_conversation()
                return memory_response
            
            # Query local GGUF model
            if not self.llm_gguf:
                return "AI model not loaded. Please check the configuration."
            
            # Get RAG context if documents are available
            enhanced_prompt = prompt
            if self.document_processor and hasattr(self.document_processor, 'get_relevant_context'):
                doc_context = self.document_processor.get_relevant_context(prompt)
                if doc_context:
                    enhanced_prompt = f"{doc_context}\n\nUser Question: {prompt}\n\nPlease answer based on the provided context."
                    print("📚 Using RAG context from documents")
            
            print("💻 Using local GGUF model (offline)")
            ai_response = self._ask_gguf(enhanced_prompt)
            
            if not ai_response:
                ai_response = "I'm sorry, I couldn't process that. Please try again."
            
            # Update history
            if use_history:
                self.conversation_history.append({"role": "user", "content": prompt})
                self.conversation_history.append({"role": "assistant", "content": ai_response})
                
                # Keep only recent history
                if len(self.conversation_history) > 20:
                    self.conversation_history = self.conversation_history[-20:]
                
                self._auto_save_conversation()
            
            return ai_response
            
        except Exception as e:
            print(f"❌ Error: {e}")
            if DEBUG_MODE:
                import traceback
                traceback.print_exc()
            return "I encountered an error. Please try again."
    
    def _auto_save_conversation(self):
        """Auto-save conversation if threshold is met"""
        if AUTO_SAVE_CONVERSATIONS and len(self.conversation_history) >= AUTO_SAVE_THRESHOLD:
            if hasattr(self, '_last_save_count'):
                if len(self.conversation_history) - self._last_save_count < AUTO_SAVE_THRESHOLD:
                    return
            
            try:
                self.memory.save_conversation(self.conversation_history[:])
                self._last_save_count = len(self.conversation_history)
                if DEBUG_MODE:
                    print("💾 Auto-saved conversation")
            except Exception as e:
                if DEBUG_MODE:
                    print(f"Failed to auto-save: {e}")
    
    def clear_history(self):
        """Clear conversation history"""
        if AUTO_SAVE_CONVERSATIONS and len(self.conversation_history) >= AUTO_SAVE_THRESHOLD:
            try:
                self.memory.save_conversation(self.conversation_history[:])
                print("💾 Conversation saved before clearing")
            except:
                pass
        
        self.conversation_history = []
        print("🧹 Conversation history cleared")
    
    def save_current_conversation(self, title: Optional[str] = None):
        """Manually save current conversation"""
        if not self.conversation_history:
            return None
        
        conv_id = self.memory.save_conversation(self.conversation_history[:], title=title)
        print(f"💾 Conversation saved: {conv_id}")
        return conv_id


if __name__ == "__main__":
    # Test the brain
    print("=" * 60)
    print("SRUTHI-AI Brain Test - Offline Mode")
    print("=" * 60)
    
    try:
        brain = AIBrain()
        
        # Test queries
        test_prompts = [
            "Hello! What can you do?",
            "What is Python?",
            "Tell me a joke"
        ]
        
        for prompt in test_prompts:
            print(f"\nUser: {prompt}")
            response = brain.ask(prompt)
            print(f"AI: {response}")
        
        print("\n✅ Brain test completed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
