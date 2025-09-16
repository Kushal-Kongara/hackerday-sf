"""
Base Agent Class for Strands Multi-Agent Architecture
====================================================

Base class that all agents in the system inherit from.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """Agent execution status."""
    IDLE = "idle"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class AgentTask:
    """Represents a task for an agent to execute."""
    id: str
    type: str
    data: Dict[str, Any]
    priority: int = 1
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class AgentResult:
    """Result of agent task execution."""
    task_id: str
    agent_id: str
    status: AgentStatus
    data: Dict[str, Any] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    
    def __post_init__(self):
        if self.data is None:
            self.data = {}


class BaseAgent(ABC):
    """Base class for all agents in the system."""
    
    def __init__(self, agent_id: str, name: str):
        """
        Initialize base agent.
        
        Args:
            agent_id: Unique identifier for the agent
            name: Human-readable name for the agent
        """
        self.agent_id = agent_id
        self.name = name
        self.status = AgentStatus.IDLE
        self.tasks_queue = []
        self.results_cache = {}
        
        logger.info(f"Initialized agent: {self.name} ({self.agent_id})")
    
    @abstractmethod
    async def process_task(self, task: AgentTask) -> AgentResult:
        """
        Process a given task.
        
        Args:
            task: Task to process
            
        Returns:
            Result of task execution
        """
        pass
    
    async def execute_task(self, task: AgentTask) -> AgentResult:
        """
        Execute a task with status tracking and error handling.
        
        Args:
            task: Task to execute
            
        Returns:
            Task execution result
        """
        import time
        
        start_time = time.time()
        self.status = AgentStatus.PROCESSING
        
        try:
            logger.info(f"Agent {self.name} starting task {task.id}")
            
            result = await self.process_task(task)
            result.execution_time = time.time() - start_time
            
            # Cache successful results
            if result.status == AgentStatus.COMPLETED:
                self.results_cache[task.id] = result
            
            self.status = AgentStatus.COMPLETED
            logger.info(f"Agent {self.name} completed task {task.id} in {result.execution_time:.2f}s")
            
            return result
            
        except Exception as e:
            error_msg = f"Agent {self.name} failed task {task.id}: {str(e)}"
            logger.error(error_msg)
            
            self.status = AgentStatus.ERROR
            
            return AgentResult(
                task_id=task.id,
                agent_id=self.agent_id,
                status=AgentStatus.ERROR,
                error=error_msg,
                execution_time=time.time() - start_time
            )
    
    def add_task(self, task: AgentTask):
        """
        Add a task to the agent's queue.
        
        Args:
            task: Task to add
        """
        self.tasks_queue.append(task)
        logger.debug(f"Added task {task.id} to agent {self.name}")
    
    def get_cached_result(self, task_id: str) -> Optional[AgentResult]:
        """
        Get cached result for a task.
        
        Args:
            task_id: Task identifier
            
        Returns:
            Cached result if available, None otherwise
        """
        return self.results_cache.get(task_id)
    
    def clear_cache(self):
        """Clear the results cache."""
        self.results_cache.clear()
        logger.debug(f"Cleared cache for agent {self.name}")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current agent status.
        
        Returns:
            Status information dictionary
        """
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": self.status.value,
            "queued_tasks": len(self.tasks_queue),
            "cached_results": len(self.results_cache)
        }
