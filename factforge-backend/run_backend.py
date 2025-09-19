#!/usr/bin/env python3
"""
Script to run FactForge backend services
"""
import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def check_docker():
    """Check if Docker is running"""
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker is available")
            return True
        else:
            print("❌ Docker is not available")
            return False
    except FileNotFoundError:
        print("❌ Docker is not installed")
        return False

def check_docker_compose():
    """Check if Docker Compose is available"""
    try:
        result = subprocess.run(['docker-compose', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker Compose is available")
            return True
        else:
            print("❌ Docker Compose is not available")
            return False
    except FileNotFoundError:
        print("❌ Docker Compose is not installed")
        return False

def setup_environment():
    """Setup environment file if it doesn't exist"""
    env_file = Path(".env")
    env_sample = Path("infra/env.sample")
    
    if not env_file.exists() and env_sample.exists():
        print("📝 Creating .env file from sample...")
        subprocess.run(['cp', str(env_sample), str(env_file)])
        print("✅ Environment file created")
    elif env_file.exists():
        print("✅ Environment file already exists")
    else:
        print("❌ Environment sample file not found")

def start_services():
    """Start all services using Docker Compose"""
    print("🚀 Starting FactForge backend services...")
    
    # Change to infra directory
    os.chdir("infra")
    
    try:
        # Start services
        result = subprocess.run([
            'docker-compose', 'up', '--build', '-d'
        ], check=True)
        
        print("✅ Services started successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start services: {e}")
        return False

def wait_for_services():
    """Wait for services to be ready"""
    print("⏳ Waiting for services to be ready...")
    
    max_attempts = 30
    attempt = 0
    
    while attempt < max_attempts:
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ API is ready")
                return True
        except requests.exceptions.RequestException:
            pass
        
        attempt += 1
        time.sleep(2)
        print(f"⏳ Attempt {attempt}/{max_attempts}...")
    
    print("❌ Services did not start within expected time")
    return False

def show_status():
    """Show service status"""
    print("\n📊 Service Status:")
    print("=" * 50)
    
    services = [
        ("API", "http://localhost:8000/health"),
        ("API Docs", "http://localhost:8000/docs"),
        ("PgAdmin", "http://localhost:5050"),
        ("RabbitMQ Management", "http://localhost:15672"),
    ]
    
    for name, url in services:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: {url}")
            else:
                print(f"⚠️  {name}: {url} (Status: {response.status_code})")
        except requests.exceptions.RequestException:
            print(f"❌ {name}: {url} (Not accessible)")

def test_api():
    """Test API with sample request"""
    print("\n🧪 Testing API...")
    
    test_claim = {
        "claim_text": "Send ₹1000 to UPI abc@upi to claim your lottery prize!",
        "language": "en"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/check",
            json=test_claim,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API test successful")
            print(f"   Verdict: {result['verdict']}")
            print(f"   Trust Score: {result['trust_score']}")
            print(f"   Latency: {result['latency_ms']}ms")
        else:
            print(f"❌ API test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ API test failed: {e}")

def main():
    """Main function"""
    print("🎯 FactForge Backend Launcher")
    print("=" * 40)
    
    # Check prerequisites
    if not check_docker():
        print("\n❌ Please install Docker first")
        sys.exit(1)
    
    if not check_docker_compose():
        print("\n❌ Please install Docker Compose first")
        sys.exit(1)
    
    # Setup environment
    setup_environment()
    
    # Start services
    if not start_services():
        print("\n❌ Failed to start services")
        sys.exit(1)
    
    # Wait for services
    if not wait_for_services():
        print("\n❌ Services did not start properly")
        sys.exit(1)
    
    # Show status
    show_status()
    
    # Test API
    test_api()
    
    print("\n🎉 FactForge backend is running!")
    print("\n📚 Next steps:")
    print("1. Visit http://localhost:8000/docs for API documentation")
    print("2. Visit http://localhost:5050 for database management (admin@factforge.com / admin)")
    print("3. Visit http://localhost:15672 for message queue management (guest / guest)")
    print("4. Check logs with: docker-compose -f infra/docker-compose.yml logs")
    print("5. Stop services with: docker-compose -f infra/docker-compose.yml down")

if __name__ == "__main__":
    main()
