"""
VAPI Integration for Voice Calls
================================

Handles integration with VAPI for making voice calls using Realtime API.
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, Optional, Callable
import httpx
import websockets
from openai import OpenAI

logger = logging.getLogger(__name__)


class VAPIClient:
    """Client for making voice calls through VAPI with Realtime API integration."""
    
    def __init__(self):
        """Initialize VAPI client."""
        self.api_key = os.getenv("VAPI_API_KEY")
        self.base_url = os.getenv("VAPI_BASE_URL", "https://api.vapi.ai")
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        if not self.api_key:
            raise ValueError("VAPI_API_KEY environment variable is required")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def create_call_context(self, user_data: Dict[str, Any], 
                                game_data: Dict[str, Any]) -> str:
        """
        Create context for the AI model based on user and game data.
        
        Args:
            user_data: User profile and history data
            game_data: Game information data
            
        Returns:
            Formatted context string
        """
        context_parts = [
            "TICKET SALES AGENT CONTEXT",
            "=" * 30,
            "",
            "ROLE: You are a friendly and knowledgeable ticket sales agent calling to offer",
            "game tickets based on the customer's interests and history.",
            "",
            "USER INFORMATION:",
        ]
        
        if user_data.get("profile"):
            profile = user_data["profile"]
            context_parts.extend([
                f"- Name: {profile.get('name', 'Customer')}",
                f"- Email: {profile.get('email', 'N/A')}",
                f"- Phone: {profile.get('phone', 'N/A')}",
            ])
        
        if user_data.get("preferences"):
            prefs = user_data["preferences"]
            context_parts.extend([
                "",
                "PREFERENCES:",
                f"- Favorite Teams: {', '.join(prefs.get('favorite_teams', []))}",
                f"- Favorite Sports: {', '.join(prefs.get('favorite_sports', []))}",
            ])
        
        if user_data.get("history"):
            context_parts.extend([
                "",
                "RECENT GAME ATTENDANCE:",
            ])
            for game in user_data["history"][:3]:  # Show last 3 games
                context_parts.append(
                    f"- {game.get('game_title', 'Game')} at {game.get('venue', 'N/A')} "
                    f"({game.get('game_date', 'N/A')})"
                )
        
        if game_data:
            context_parts.extend([
                "",
                "AVAILABLE GAMES TO PROMOTE:",
            ])
            for game in game_data[:2]:  # Show top 2 recommended games
                props = game.get("properties", {})
                context_parts.append(
                    f"- {props.get('title', 'Game')} on {props.get('date', 'TBD')} "
                    f"at {props.get('venue', 'TBD')}"
                )
        
        context_parts.extend([
            "",
            "CONVERSATION GUIDELINES:",
            "- Be warm, friendly, and professional",
            "- Reference their past attendance and preferences",
            "- Focus on games that match their interests",
            "- Ask about their availability and preferences",
            "- Handle objections gracefully",
            "- Always end with a clear next step",
            "",
            "Remember: This is a real customer call. Be natural and conversational!"
        ])
        
        return "\n".join(context_parts)
    
    async def create_assistant(self, context: str) -> Dict[str, Any]:
        """
        Create a VAPI assistant with the given context.
        
        Args:
            context: Context information for the assistant
            
        Returns:
            Assistant configuration
        """
        assistant_config = {
            "model": {
                "provider": "openai",
                "model": "gpt-4o-realtime-preview",
                "systemMessage": context,
                "temperature": 0.7,
                "maxTokens": 300
            },
            "voice": {
                "provider": "openai",
                "voiceId": "alloy"  # Can be: alloy, echo, fable, onyx, nova, shimmer
            },
            "transcriber": {
                "provider": "deepgram",
                "model": "nova-2",
                "language": "en-US"
            },
            "firstMessage": "Hi! This is calling from the ticket office. I hope you're having a great day!",
            "endCallMessage": "Thank you for your time! Have a wonderful day!",
            "recordingEnabled": True,
            "endCallPhrases": ["goodbye", "hang up", "end call"],
            "maxDurationSeconds": 300  # 5 minutes max
        }
        
        return assistant_config
    
    async def make_call(self, phone_number: str, assistant_config: Dict[str, Any],
                       callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Initiate a phone call using VAPI.
        
        Args:
            phone_number: Phone number to call
            assistant_config: Assistant configuration
            callback: Optional callback for call events
            
        Returns:
            Call information
        """
        try:
            call_payload = {
                "assistant": assistant_config,
                "phoneNumber": phone_number,
                "metadata": {
                    "purpose": "ticket_sales",
                    "timestamp": asyncio.get_event_loop().time()
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/call/phone",
                    json=call_payload,
                    headers=self.headers,
                    timeout=30.0
                )
                
                if response.status_code == 201:
                    call_data = response.json()
                    call_id = call_data.get("id")
                    
                    logger.info(f"Call initiated successfully: {call_id}")
                    
                    # Monitor call if callback provided
                    if callback:
                        asyncio.create_task(self._monitor_call(call_id, callback))
                    
                    return call_data
                else:
                    error_msg = f"Failed to initiate call: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    return {"error": error_msg}
                    
        except Exception as e:
            logger.error(f"Error making call: {e}")
            return {"error": str(e)}
    
    async def _monitor_call(self, call_id: str, callback: Callable):
        """
        Monitor call progress and events.
        
        Args:
            call_id: Call identifier
            callback: Callback function for events
        """
        try:
            # WebSocket connection for real-time call monitoring
            # This is a simplified implementation
            logger.info(f"Monitoring call {call_id}")
            
            # In a real implementation, you'd connect to VAPI's WebSocket endpoint
            # and listen for call events like: started, ended, speech, etc.
            
            await asyncio.sleep(1)  # Placeholder for actual monitoring
            
        except Exception as e:
            logger.error(f"Error monitoring call {call_id}: {e}")
    
    async def get_call_status(self, call_id: str) -> Dict[str, Any]:
        """
        Get current call status.
        
        Args:
            call_id: Call identifier
            
        Returns:
            Call status information
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/call/{call_id}",
                    headers=self.headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {"error": f"Failed to get call status: {response.status_code}"}
                    
        except Exception as e:
            logger.error(f"Error getting call status: {e}")
            return {"error": str(e)}
    
    async def end_call(self, call_id: str) -> bool:
        """
        End an active call.
        
        Args:
            call_id: Call identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{self.base_url}/call/{call_id}",
                    json={"status": "ended"},
                    headers=self.headers,
                    timeout=10.0
                )
                
                return response.status_code == 200
                
        except Exception as e:
            logger.error(f"Error ending call {call_id}: {e}")
            return False
