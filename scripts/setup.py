#!/usr/bin/env python3
"""
Setup script for Camera Feed Query System
Handles installation, configuration, and initial setup
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def run_command(command: str, description: str = ""):
    """Run a shell command with error handling"""
    print(f"🔧 {description or command}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(f"   ✅ {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error: {e.stderr.strip()}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"   ❌ Python {version.major}.{version.minor} is not supported. Please use Python 3.8+")
        return False
    print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_dependencies():
    """Install required Python packages"""
    print("📦 Installing dependencies...")
    if not run_command("pip install -r requirements.txt", "Installing Python packages"):
        print("   ⚠️  Some packages may have failed to install. Please check manually.")
        return False
    return True

def setup_environment():
    """Set up environment configuration"""
    print("🔧 Setting up environment...")
    
    env_file = Path(".env")
    env_example = Path("env_example.txt")
    
    if not env_file.exists() and env_example.exists():
        # Copy example to .env
        with open(env_example, 'r') as f:
            content = f.read()
        with open(env_file, 'w') as f:
            f.write(content)
        print("   ✅ Created .env file from template")
        print("   ⚠️  Please edit .env and add your OPENAI_API_KEY")
    elif env_file.exists():
        print("   ✅ .env file already exists")
    else:
        print("   ⚠️  No environment template found")
    
    return True

def generate_sample_data():
    """Generate sample data if not present"""
    print("📊 Generating sample data...")
    
    data_dir = Path("data")
    camera_feeds_file = data_dir / "camera_feeds.json"
    
    if not camera_feeds_file.exists():
        if run_command("python3 data/sample_data_generator.py", "Generating camera feed data"):
            print("   ✅ Sample data generated successfully")
        else:
            print("   ❌ Failed to generate sample data")
            return False
    else:
        print("   ✅ Sample data already exists")
    
    return True

def verify_installation():
    """Verify that the installation is working"""
    print("🔍 Verifying installation...")
    
    try:
        # Test imports
        sys.path.append(str(Path.cwd()))
        
        from src.tools.data_retrieval import DataRetrievalTools
        from src.tools.analysis_tools import AnalysisTools
        
        # Test data tools
        data_tools = DataRetrievalTools()
        stats = data_tools.get_statistics()
        
        print(f"   ✅ Data tools working - {stats['total_cameras']} cameras loaded")
        
        # Test analysis tools
        analysis_tools = AnalysisTools()
        health = analysis_tools.get_health_status_report()
        
        print(f"   ✅ Analysis tools working - Health score: {health['system_health']['health_score']:.1f}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Verification failed: {e}")
        return False

def show_next_steps():
    """Show next steps for the user"""
    print("\n🎉 Setup Complete!")
    print("=" * 40)
    
    print("\n📋 Next Steps:")
    print("1. Edit .env file and add your OPENAI_API_KEY")
    print("2. Test the system with: python main.py --info")
    print("3. Run demonstration: python main.py --demo")
    print("4. Start interactive mode: python main.py --interactive")
    print("5. Launch web interface: python main.py --streamlit")
    print("6. Start API server: python main.py --api")
    
    print("\n💡 Example Queries:")
    print("• 'What are the camera IDs capturing Pacific area with best clarity?'")
    print("• 'Show me cameras with high bandwidth usage'")
    print("• 'What's the overall system health?'")
    print("• 'Compare performance across different regions'")
    
    print("\n📚 Documentation:")
    print("• README.md - Complete documentation")
    print("• demo_examples.py - Comprehensive demonstrations")
    print("• API docs at http://localhost:8000/docs (when running API)")

def main():
    """Main setup function"""
    print("🚀 Camera Feed Query System - Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("⚠️  Dependency installation had issues. Please check manually.")
    
    # Setup environment
    setup_environment()
    
    # Generate sample data
    if not generate_sample_data():
        print("⚠️  Sample data generation failed. Please run manually:")
        print("   python3 data/sample_data_generator.py")
    
    # Verify installation
    if verify_installation():
        show_next_steps()
    else:
        print("\n❌ Setup verification failed. Please check the errors above.")
        print("You may need to:")
        print("1. Check your Python installation")
        print("2. Install dependencies manually: pip install -r requirements.txt")
        print("3. Generate sample data: python3 data/sample_data_generator.py")

if __name__ == "__main__":
    main()
