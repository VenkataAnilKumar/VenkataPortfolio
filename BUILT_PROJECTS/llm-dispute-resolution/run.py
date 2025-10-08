#!/usr/bin/env python3

"""
LLM Dispute Resolution System - Setup and Run Script

This script helps set up and run the MVP backend system.
"""

import os
import sys
import subprocess
import asyncio
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8+"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        sys.exit(1)

def setup_environment():
    """Set up environment variables"""
    env_file = Path(".env")
    if not env_file.exists():
        print("🔧 Creating .env file...")
        example_env = Path(".env.example")
        if example_env.exists():
            with open(example_env, "r") as src, open(env_file, "w") as dest:
                content = src.read()
                # Replace sensitive values with placeholders
                content = content.replace("your-api-key", "changeme")
                content = content.replace("your-jwt-secret", "changeme")
                dest.write(content)
        else:
            with open(env_file, "w") as f:
                f.write("# LLM Dispute Resolution System Configuration\n")
                f.write("ENV=dev\n")
                f.write("API_KEY=changeme\n")
                f.write("DB_URL=sqlite+aiosqlite:///./disputes.db\n")
                f.write("REDIS_URL=redis://localhost:6379\n")
                f.write("LLM_PROVIDER=openai\n")
                f.write("OPENAI_API_KEY=changeme\n")
                f.write("TOKEN_BUDGET_PER_CASE=8000\n")
                f.write("ENABLE_PII_REDACTION=1\n")
                f.write("ENABLE_PATTERN_DETECTION=1\n")
                f.write("ENABLE_PROMETHEUS=1\n")
                f.write("ENABLE_AUDIT_LOGGING=1\n")
        print("✅ .env file created")
    else:
        print("✅ .env file already exists")

def verify_components():
    """Verify all system components"""
    print("🔍 Verifying system components...")
    
    # Check required directories
    required_dirs = [
        "app/analytics",
        "app/api",
        "app/core",
        "app/domain",
        "app/infra",
        "app/security",
        "app/services",
        "app/telemetry"
    ]
    
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            print(f"❌ Missing directory: {dir_path}")
            sys.exit(1)
            
    # Check required files
    required_files = [
        "app/main.py",
        "requirements.txt",
        ".env.example",
        "README.md"
    ]
    
    for file_path in required_files:
        if not Path(file_path).exists():
            print(f"❌ Missing file: {file_path}")
            sys.exit(1)
            
    # Verify database URL
    if not os.getenv("DB_URL"):
        print("❌ DB_URL not set in environment")
        sys.exit(1)
        
    print("✅ All components verified")

async def seed_database():
    """Seed the database with sample data"""
    print("🌱 Seeding database with sample transactions...")
    try:
        # Import and run the seed script
        sys.path.insert(0, os.getcwd())
        from scripts.seed_transactions import seed_transactions
        await seed_transactions()
        print("✅ Database seeded successfully")
    except Exception as e:
        print(f"⚠️  Failed to seed database: {e}")
        print("   (This is optional - the system will work without seed data)")

def run_server():
    """Start the FastAPI server"""
    print("🚀 Starting the server...")
    print("   Server will be available at: http://localhost:8000")
    print("   API Documentation: http://localhost:8000/docs")
    print("   Health Check: http://localhost:8000/v1/health")
    print("\n   Press Ctrl+C to stop the server")
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except subprocess.CalledProcessError:
        print("❌ Failed to start server")
        sys.exit(1)

def run_tests():
    """Run the test suite"""
    print("🧪 Running test suite...")
    print("   Make sure the server is running in another terminal!")
    print("   Start server with: python run.py --server")
    
    try:
        subprocess.run([sys.executable, "tests/test_flow.py"], check=True)
    except subprocess.CalledProcessError:
        print("❌ Tests failed")
        sys.exit(1)

def show_help():
    """Show help information"""
    print("""
🤖 LLM Dispute Resolution System

Usage:
    python run.py [command]

Commands:
    --setup     Set up the system (install deps, create .env, seed db)
    --server    Start the FastAPI server
    --test      Run the test suite
    --seed      Seed the database with sample data
    --help      Show this help message

Examples:
    python run.py --setup    # First time setup
    python run.py --server   # Start the server
    python run.py --test     # Run tests (server must be running)

API Endpoints:
    POST /v1/disputes        # Create and process a dispute
    GET  /v1/disputes/{id}   # Get dispute by ID  
    GET  /v1/disputes/{id}/audit  # Get audit log
    GET  /v1/metrics         # Get system metrics
    GET  /v1/health          # Health check

Authentication:
    Include header: x-api-key: changeme
    (Configure in .env file)
""")

async def main():
    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1]

    if command == "--help":
        show_help()
    elif command == "--setup":
        check_python_version()
        install_dependencies()
        setup_environment()
        await seed_database()
        print("\n🎉 Setup complete! Run 'python run.py --server' to start")
    elif command == "--server":
        run_server()
    elif command == "--test":
        run_tests()
    elif command == "--seed":
        await seed_database()
    else:
        print(f"❌ Unknown command: {command}")
        show_help()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())