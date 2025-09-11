#!/usr/bin/env python3
"""
CLI interface for Camera Feed Query System
Handles demonstrations, interactive mode, and queries
"""

import os
import sys
import argparse
import json
from dotenv import load_dotenv

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from services.system_service import SystemService
from services.demo_service import DemoService

load_dotenv()

def main():
    """CLI interface for demonstrations and queries"""
    parser = argparse.ArgumentParser(
        description="Camera Feed Query System - CLI Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/cli.py --demo                    # Run demonstration queries
  python scripts/cli.py --interactive            # Start interactive mode
  python scripts/cli.py --query "Show me Pacific cameras with best clarity"
  python scripts/cli.py --info                   # Show system information
        """
    )
    
    parser.add_argument(
        "--demo", 
        action="store_true", 
        help="Run demonstration queries"
    )
    
    parser.add_argument(
        "--interactive", "-i", 
        action="store_true", 
        help="Start interactive query mode"
    )
    
    parser.add_argument(
        "--query", "-q", 
        type=str, 
        help="Process a single query"
    )
    
    parser.add_argument(
        "--info", 
        action="store_true", 
        help="Show system information"
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize services
        system_service = SystemService()
        demo_service = DemoService(system_service)
        
        # Handle different modes
        if args.demo:
            demo_service.run_demonstration()
        
        elif args.interactive:
            demo_service.interactive_mode()
        
        elif args.query:
            print(f"🔍 Processing query: {args.query}")
            response = system_service.process_query(args.query)
            print(f"🤖 Response: {response}")
        
        elif args.info:
            info = system_service.get_system_info()
            print("📊 System Information:")
            print(json.dumps(info, indent=2))
        
        else:
            # Default: show help
            print("📹 Camera Feed Query System - CLI")
            print("=" * 40)
            print("\n💡 Usage:")
            print("  python scripts/cli.py --demo        # Run demonstration")
            print("  python scripts/cli.py --interactive # Interactive mode")
            print("  python scripts/cli.py --query 'your question'")
            print("  python scripts/cli.py --info        # System info")
            print("  python scripts/cli.py --help        # Show all options")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
