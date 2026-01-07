from typing import Dict, Optional
from config import ContextBudget
from models import RAGSystem

class ContextAssembler:
    def __init__(self, rag_system: RAGSystem):
        self.rag_system = rag_system
        self.session_memory = {}
    
    def update_memory(self, key: str, value: str):
        """Update session memory with compression for 55-char limit"""
        # Compress memory entries to fit budget
        compressed = f"{key}:{value}"
        self.session_memory[key] = compressed
    
    def get_memory_string(self) -> str:
        """Format memory within 55-char budget"""
        if not self.session_memory:
            return "[No session memory]"
        
        memory_items = []
        char_count = 0
        
        for key, value in self.session_memory.items():
            item = f"{key}:{value}"
            if char_count + len(item) + 1 <= 55:  # +1 for separator
                memory_items.append(item)
                char_count += len(item) + 1
            else:
                break
        
        return ";".join(memory_items) if memory_items else "[Memory full]"
    
    def simulate_tool_outputs(self) -> str:
        """Simulate realistic tool outputs within 855-char budget"""
        outputs = [
            "search_logs: Found 3 ERROR entries in last 24h",
            "check_status: Service running, CPU 45%, Memory 67%", 
            "get_config: timeout=30s, retry=3, debug=false"
        ]
        
        combined = " | ".join(outputs)
        if len(combined) <= 855:
            return combined
        
        # Truncate if needed
        return combined[:852] + "..."
    
    def assemble_context(self, instructions: str, goal: str, query: str) -> ContextBudget:
        """Assemble complete context within all budget constraints"""
        
        # Enforce instruction limit
        if len(instructions) > 255:
            instructions = instructions[:252] + "..."
        
        # Enforce goal limit  
        if len(goal) > 1500:
            goal = goal[:1497] + "..."
        
        # Get memory within budget
        memory = self.get_memory_string()
        
        # Retrieve relevant content within budget
        retrieval = self.rag_system.retrieve(query, max_chars=550)
        
        # Get tool outputs within budget
        tool_outputs = self.simulate_tool_outputs()
        
        return ContextBudget(
            instructions=instructions,
            goal=goal,
            memory=memory,
            retrieval=retrieval,
            tool_outputs=tool_outputs
        )
    
    def format_context_window(self, context: ContextBudget) -> str:
        """Format the final context window for agent consumption"""
        return f"""INSTRUCTIONS: {context.instructions}

GOAL: {context.goal}

MEMORY: {context.memory}

RETRIEVAL: {context.retrieval}

TOOL_OUTPUTS: {context.tool_outputs}"""
    
    def get_budget_usage(self, context: ContextBudget) -> Dict[str, Dict[str, int]]:
        """Return budget usage statistics"""
        limits = {'instructions': 255, 'goal': 1500, 'memory': 55, 'retrieval': 550, 'tool_outputs': 855}
        usage = {}
        
        for field, limit in limits.items():
            actual = len(getattr(context, field))
            usage[field] = {
                'used': actual,
                'limit': limit,
                'remaining': limit - actual,
                'percentage': round((actual / limit) * 100, 1)
            }
        
        return usage