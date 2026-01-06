"""
Smart Assistant Memory Module
Persistent storage for user data, contacts, reminders, timers, and conversations
Reusable, thread-safe, JSON-based storage
"""

import os
import json
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import uuid


class Memory:
    """Persistent memory storage with conversation history"""
    
    def __init__(self, memory_file: Optional[str] = None):
        """
        Initialize memory system
        
        Args:
            memory_file: Path to JSON storage file
        """
        if memory_file is None:
            # Default to data/memory.json
            base_dir = Path(__file__).parent.parent
            memory_file = base_dir / "data" / "memory.json"
        
        self.memory_file = Path(memory_file)
        self.lock = threading.Lock()
        
        # Ensure data directory exists
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize or load memory
        self._initialize()
    
    def _initialize(self):
        """Initialize memory file with default structure"""
        if not self.memory_file.exists():
            default_data = {
                "user_profile": {
                    "name": None,
                    "email": None,
                    "created_at": datetime.now().isoformat()
                },
                "contacts": [],
                "reminders": [],
                "timers": [],
                "conversations": [],
                "custom_data": {}
            }
            self._write_data(default_data)
    
    def _read_data(self) -> Dict:
        """Read memory data from file (thread-safe)"""
        with self.lock:
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                # Reinitialize if corrupted
                self._initialize()
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
    
    def _write_data(self, data: Dict):
        """Write memory data to file (thread-safe)"""
        with self.lock:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
    
    # ========================================================================
    # USER PROFILE
    # ========================================================================
    
    def set_user_name(self, name: str):
        """Set user's name"""
        data = self._read_data()
        data["user_profile"]["name"] = name
        self._write_data(data)
    
    def set_user_email(self, email: str):
        """Set user's email"""
        data = self._read_data()
        data["user_profile"]["email"] = email
        self._write_data(data)
    
    def get_user_name(self) -> Optional[str]:
        """Get user's name"""
        data = self._read_data()
        return data["user_profile"].get("name")
    
    def get_user_info(self) -> Dict:
        """Get user profile information"""
        data = self._read_data()
        return data["user_profile"]
    
    # ========================================================================
    # CONTACTS
    # ========================================================================
    
    def add_contact(self, name: str, phone: Optional[str] = None, 
                   email: Optional[str] = None, notes: Optional[str] = None) -> str:
        """
        Add a contact
        
        Returns:
            str: Contact ID
        """
        data = self._read_data()
        contact_id = f"contact_{uuid.uuid4().hex[:8]}"
        
        contact = {
            "id": contact_id,
            "name": name,
            "phone": phone,
            "email": email,
            "notes": notes,
            "created_at": datetime.now().isoformat()
        }
        
        data["contacts"].append(contact)
        self._write_data(data)
        return contact_id
    
    def get_contact(self, name: str) -> Optional[Dict]:
        """Get contact by name (case-insensitive)"""
        data = self._read_data()
        for contact in data["contacts"]:
            if contact["name"].lower() == name.lower():
                return contact
        return None
    
    def list_contacts(self) -> List[Dict]:
        """List all contacts"""
        data = self._read_data()
        return data["contacts"]
    
    def delete_contact(self, contact_id: str):
        """Delete a contact"""
        data = self._read_data()
        data["contacts"] = [c for c in data["contacts"] if c["id"] != contact_id]
        self._write_data(data)
    
    # ========================================================================
    # REMINDERS
    # ========================================================================
    
    def add_reminder(self, description: str, remind_datetime: datetime) -> str:
        """
        Add a reminder
        
        Returns:
            str: Reminder ID
        """
        data = self._read_data()
        reminder_id = f"reminder_{uuid.uuid4().hex[:8]}"
        
        reminder = {
            "id": reminder_id,
            "description": description,
            "datetime": remind_datetime.isoformat(),
            "completed": False,
            "created_at": datetime.now().isoformat()
        }
        
        data["reminders"].append(reminder)
        self._write_data(data)
        return reminder_id
    
    def get_active_reminders(self) -> List[Dict]:
        """Get active (incomplete, future) reminders"""
        data = self._read_data()
        now = datetime.now()
        active = []
        
        for reminder in data["reminders"]:
            if not reminder["completed"]:
                remind_time = datetime.fromisoformat(reminder["datetime"])
                if remind_time > now:
                    active.append(reminder)
        
        return active
    
    def complete_reminder(self, reminder_id: str):
        """Mark reminder as completed"""
        data = self._read_data()
        for reminder in data["reminders"]:
            if reminder["id"] == reminder_id:
                reminder["completed"] = True
                break
        self._write_data(data)
    
    # ========================================================================
    # TIMERS
    # ========================================================================
    
    def start_timer(self, duration_seconds: int, label: str = "Timer") -> str:
        """
        Start a timer
        
        Returns:
            str: Timer ID
        """
        data = self._read_data()
        timer_id = f"timer_{uuid.uuid4().hex[:8]}"
        
        timer = {
            "id": timer_id,
            "label": label,
            "start_time": datetime.now().isoformat(),
            "duration_seconds": duration_seconds,
            "active": True
        }
        
        data["timers"].append(timer)
        self._write_data(data)
        return timer_id
    
    def get_active_timers(self) -> List[Dict]:
        """Get active timers with remaining time"""
        data = self._read_data()
        now = datetime.now()
        active = []
        
        for timer in data["timers"]:
            if timer["active"]:
                start = datetime.fromisoformat(timer["start_time"])
                elapsed = (now - start).total_seconds()
                remaining = timer["duration_seconds"] - elapsed
                
                timer_info = timer.copy()
                timer_info["remaining_seconds"] = max(0, remaining)
                timer_info["expired"] = remaining <= 0
                active.append(timer_info)
        
        return active
    
    def cancel_timer(self, timer_id: str):
        """Cancel/stop a timer"""
        data = self._read_data()
        for timer in data["timers"]:
            if timer["id"] == timer_id:
                timer["active"] = False
                break
        self._write_data(data)
    
    # ========================================================================
    # CONVERSATION HISTORY (ChatGPT-like)
    # ========================================================================
    
    def save_conversation(self, messages: List[Dict], title: Optional[str] = None) -> str:
        """
        Save a conversation
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            title: Optional title (auto-generated from first user message if None)
            
        Returns:
            str: Conversation ID
        """
        data = self._read_data()
        conversation_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:4]}"
        
        # Auto-generate title from first user message
        if title is None and messages:
            first_user_msg = next((m for m in messages if m.get("role") == "user"), None)
            if first_user_msg:
                title = first_user_msg["content"][:50]
                if len(first_user_msg["content"]) > 50:
                    title += "..."
        
        # Add timestamps if missing
        for msg in messages:
            if "timestamp" not in msg:
                msg["timestamp"] = datetime.now().isoformat()
        
        conversation = {
            "id": conversation_id,
            "title": title or "Untitled Conversation",
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "message_count": len(messages),
            "messages": messages
        }
        
        data["conversations"].append(conversation)
        self._write_data(data)
        return conversation_id
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict]:
        """Get a specific conversation"""
        data = self._read_data()
        for conv in data["conversations"]:
            if conv["id"] == conversation_id:
                return conv
        return None
    
    def list_conversations(self, limit: int = 20) -> List[Dict]:
        """
        List recent conversations (without full messages for efficiency)
        
        Returns:
            List of conversation summaries
        """
        data = self._read_data()
        conversations = data["conversations"]
        
        # Sort by last_updated (newest first)
        conversations.sort(key=lambda x: x.get("last_updated", x["created_at"]), reverse=True)
        
        # Return summaries without full message content
        summaries = []
        for conv in conversations[:limit]:
            summary = {
                "id": conv["id"],
                "title": conv["title"],
                "created_at": conv["created_at"],
                "message_count": conv["message_count"]
            }
            summaries.append(summary)
        
        return summaries
    
    def search_conversations(self, query: str) -> List[Dict]:
        """Search conversations by keyword"""
        data = self._read_data()
        query_lower = query.lower()
        results = []
        
        for conv in data["conversations"]:
            # Search in title and message content
            if query_lower in conv["title"].lower():
                results.append({
                    "id": conv["id"],
                    "title": conv["title"],
                    "created_at": conv["created_at"],
                    "matched_in": "title"
                })
                continue
            
            # Search in messages
            for msg in conv["messages"]:
                if query_lower in msg["content"].lower():
                    results.append({
                        "id": conv["id"],
                        "title": conv["title"],
                        "created_at": conv["created_at"],
                        "matched_in": "content"
                    })
                    break
        
        return results
    
    def delete_conversation(self, conversation_id: str):
        """Delete a conversation"""
        data = self._read_data()
        data["conversations"] = [c for c in data["conversations"] if c["id"] != conversation_id]
        self._write_data(data)
    
    def export_conversation(self, conversation_id: str, output_path: str, format: str = 'txt'):
        """
        Export conversation to file
        
        Args:
            conversation_id: ID of conversation
            output_path: Output file path
            format: 'txt', 'md', or 'json'
        """
        conv = self.get_conversation(conversation_id)
        if not conv:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            if format == 'json':
                json.dump(conv, f, indent=2, ensure_ascii=False)
            elif format == 'md':
                f.write(f"# {conv['title']}\n\n")
                f.write(f"**Created:** {conv['created_at']}\n\n")
                f.write("---\n\n")
                for msg in conv["messages"]:
                    role = "**You:**" if msg["role"] == "user" else "**Assistant:**"
                    f.write(f"{role} {msg['content']}\n\n")
            else:  # txt
                f.write(f"{conv['title']}\n")
                f.write(f"Created: {conv['created_at']}\n")
                f.write("=" * 60 + "\n\n")
                for msg in conv["messages"]:
                    role = "You" if msg["role"] == "user" else "Assistant"
                    f.write(f"{role}: {msg['content']}\n\n")
    
    # ========================================================================
    # CUSTOM DATA
    # ========================================================================
    
    def save(self, key: str, value: Any):
        """Save custom key-value data"""
        data = self._read_data()
        data["custom_data"][key] = value
        self._write_data(data)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get custom data"""
        data = self._read_data()
        return data["custom_data"].get(key, default)
    
    def delete(self, key: str):
        """Delete custom data"""
        data = self._read_data()
        if key in data["custom_data"]:
            del data["custom_data"][key]
            self._write_data(data)
    
    # ========================================================================
    # UTILITIES
    # ========================================================================
    
    def get_stats(self) -> Dict:
        """Get memory statistics"""
        data = self._read_data()
        return {
            "contacts": len(data["contacts"]),
            "reminders": len(data["reminders"]),
            "timers": len(data["timers"]),
            "conversations": len(data["conversations"]),
            "total_messages": sum(c["message_count"] for c in data["conversations"]),
            "user_name": data["user_profile"].get("name")
        }
    
    def clear_all(self):
        """Clear ALL memory (CAUTION!)"""
        self._initialize()


if __name__ == "__main__":
    # Test the memory module
    print("=" * 60)
    print("SRUTHI-AI Memory Module Test")
    print("=" * 60)
    
    memory = Memory()
    
    # Test user profile
    memory.set_user_name("Anand")
    print(f"\nUser: {memory.get_user_name()}")
    
    # Test contacts
    memory.add_contact("Rahul", phone="+91-9876543210")
    print(f"Contacts: {memory.list_contacts()}")
    
    # Test conversation save
    messages = [
        {"role": "user", "content": "Hello!"},
        {"role": "assistant", "content": "Hi! How can I help?"}
    ]
    conv_id = memory.save_conversation(messages)
    print(f"\nSaved conversation: {conv_id}")
    print(f"Conversations: {memory.list_conversations()}")
    
    print(f"\nStats: {memory.get_stats()}")
    print("\n✅ Memory module working!")
