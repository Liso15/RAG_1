import json
import argparse
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from models import RAGSystem, Document
from context_assembler import ContextAssembler

console = Console()

def load_corpus(file_path: str) -> list[Document]:
    """Load documents from JSON corpus"""
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    return [Document(item['id'], item['content']) for item in data]

def display_budget_usage(usage_stats):
    """Display budget usage in a formatted table"""
    table = Table(title="Context Budget Usage")
    table.add_column("Section", style="cyan")
    table.add_column("Used", style="green")
    table.add_column("Limit", style="yellow") 
    table.add_column("Remaining", style="blue")
    table.add_column("Usage %", style="red")
    
    for section, stats in usage_stats.items():
        percentage_color = "red" if stats['percentage'] > 90 else "yellow" if stats['percentage'] > 70 else "green"
        table.add_row(
            section.title(),
            str(stats['used']),
            str(stats['limit']),
            str(stats['remaining']),
            f"[{percentage_color}]{stats['percentage']}%[/{percentage_color}]"
        )
    
    console.print(table)

def main():
    parser = argparse.ArgumentParser(description="Context-Aware RAG System")
    parser.add_argument("--query", required=True, help="Query for retrieval")
    parser.add_argument("--instructions", default="You are a helpful operations assistant.", help="System instructions")
    parser.add_argument("--goal", default="Help the user with operational procedures and troubleshooting.", help="Current goal")
    parser.add_argument("--corpus", default="data/sample_corpus.json", help="Path to corpus file")
    parser.add_argument("--verbose", action="store_true", help="Show detailed budget breakdown")
    
    args = parser.parse_args()
    
    # Initialize system
    console.print("[bold blue]Initializing Context-Aware RAG System...[/bold blue]")
    
    rag_system = RAGSystem()
    assembler = ContextAssembler(rag_system)
    
    # Load corpus
    documents = load_corpus(args.corpus)
    rag_system.add_documents(documents)
    console.print(f"[green]Loaded {len(documents)} documents into vector store[/green]")
    
    # Simulate some session memory
    assembler.update_memory("user_pref", "CLI")
    assembler.update_memory("last_action", "restart")
    
    # Assemble context
    context = assembler.assemble_context(args.instructions, args.goal, args.query)
    
    if args.verbose:
        console.print("\n[bold yellow]Budget Usage Analysis:[/bold yellow]")
        usage_stats = assembler.get_budget_usage(context)
        display_budget_usage(usage_stats)
        
        console.print("\n[bold yellow]Context Sections:[/bold yellow]")
        
        # Display each section with character counts
        sections = [
            ("Instructions", context.instructions, 255),
            ("Goal", context.goal, 1500),
            ("Memory", context.memory, 55),
            ("Retrieval", context.retrieval, 550),
            ("Tool Outputs", context.tool_outputs, 855)
        ]
        
        for name, content, limit in sections:
            used = len(content)
            color = "red" if used > limit * 0.9 else "yellow" if used > limit * 0.7 else "green"
            
            panel = Panel(
                content,
                title=f"[bold]{name}[/bold] ({used}/{limit} chars)",
                border_style=color
            )
            console.print(panel)
    
    # Display final context window
    console.print("\n[bold green]Final Context Window:[/bold green]")
    final_context = assembler.format_context_window(context)
    
    context_panel = Panel(
        final_context,
        title="Agent Context Window",
        border_style="bright_blue"
    )
    console.print(context_panel)
    
    # Show total character count
    total_chars = len(final_context)
    console.print(f"\n[bold]Total Context Size: {total_chars} characters[/bold]")

if __name__ == "__main__":
    main()