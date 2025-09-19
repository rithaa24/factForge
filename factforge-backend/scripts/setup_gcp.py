#!/usr/bin/env python3
"""
Setup script for Google Cloud Platform integration
"""
import os
import json
import subprocess
import sys
from pathlib import Path

def check_gcp_cli():
    """Check if gcloud CLI is installed"""
    try:
        result = subprocess.run(['gcloud', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Google Cloud CLI is installed")
            return True
        else:
            print("❌ Google Cloud CLI is not installed")
            return False
    except FileNotFoundError:
        print("❌ Google Cloud CLI is not installed")
        return False

def install_gcp_cli():
    """Install Google Cloud CLI"""
    print("Installing Google Cloud CLI...")
    
    if sys.platform == "win32":
        print("Please install Google Cloud CLI manually from: https://cloud.google.com/sdk/docs/install")
        return False
    elif sys.platform == "darwin":
        # macOS
        try:
            subprocess.run(['brew', 'install', 'google-cloud-sdk'], check=True)
            print("✅ Google Cloud CLI installed via Homebrew")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install via Homebrew. Please install manually.")
            return False
    else:
        # Linux
        try:
            subprocess.run(['curl', 'https://sdk.cloud.google.com', '|', 'bash'], shell=True, check=True)
            print("✅ Google Cloud CLI installed")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install. Please install manually.")
            return False

def setup_authentication():
    """Setup GCP authentication"""
    print("\n🔐 Setting up GCP authentication...")
    
    # Check if already authenticated
    try:
        result = subprocess.run(['gcloud', 'auth', 'list'], capture_output=True, text=True)
        if "ACTIVE" in result.stdout:
            print("✅ Already authenticated with Google Cloud")
            return True
    except:
        pass
    
    # Authenticate
    print("Please authenticate with Google Cloud...")
    try:
        subprocess.run(['gcloud', 'auth', 'login'], check=True)
        print("✅ Authentication successful")
        return True
    except subprocess.CalledProcessError:
        print("❌ Authentication failed")
        return False

def create_service_account():
    """Create service account for FactForge"""
    print("\n👤 Creating service account...")
    
    project_id = input("Enter your GCP Project ID: ").strip()
    if not project_id:
        print("❌ Project ID is required")
        return False, None
    
    service_account_name = "factforge-service-account"
    service_account_email = f"{service_account_name}@{project_id}.iam.gserviceaccount.com"
    
    try:
        # Create service account
        subprocess.run([
            'gcloud', 'iam', 'service-accounts', 'create',
            service_account_name,
            '--display-name=FactForge Service Account',
            '--description=Service account for FactForge backend'
        ], check=True)
        print(f"✅ Service account created: {service_account_email}")
        
        # Grant necessary roles
        roles = [
            'roles/aiplatform.user',
            'roles/storage.objectViewer',
            'roles/storage.objectCreator'
        ]
        
        for role in roles:
            subprocess.run([
                'gcloud', 'projects', 'add-iam-policy-binding', project_id,
                '--member', f'serviceAccount:{service_account_email}',
                '--role', role
            ], check=True)
            print(f"✅ Granted role: {role}")
        
        return True, project_id
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create service account: {e}")
        return False, None

def create_credentials_file(project_id):
    """Create credentials file"""
    print("\n🔑 Creating credentials file...")
    
    service_account_name = "factforge-service-account"
    service_account_email = f"{service_account_name}@{project_id}.iam.gserviceaccount.com"
    
    try:
        # Create key file
        key_file = f"{service_account_name}-key.json"
        subprocess.run([
            'gcloud', 'iam', 'service-accounts', 'keys', 'create',
            key_file,
            '--iam-account', service_account_email
        ], check=True)
        
        # Move to project directory
        project_root = Path(__file__).parent.parent
        credentials_path = project_root / "credentials" / key_file
        credentials_path.parent.mkdir(exist_ok=True)
        
        import shutil
        shutil.move(key_file, credentials_path)
        
        print(f"✅ Credentials file created: {credentials_path}")
        return str(credentials_path)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create credentials file: {e}")
        return None

def update_env_file(project_id, credentials_path):
    """Update environment file with GCP settings"""
    print("\n📝 Updating environment file...")
    
    project_root = Path(__file__).parent.parent
    env_file = project_root / "infra" / "env.sample"
    
    if not env_file.exists():
        print("❌ Environment file not found")
        return False
    
    # Read current content
    with open(env_file, 'r') as f:
        content = f.read()
    
    # Update GCP settings
    gcp_settings = f"""
# Google Cloud Platform Configuration
GCP_PROJECT_ID={project_id}
GCP_REGION=us-central1
GCP_CREDENTIALS_PATH={credentials_path}
VERTEX_AI_MODEL=gemini-1.5-pro
VERTEX_AI_TEMPERATURE=0.1
VERTEX_AI_MAX_TOKENS=1000

# LLM Provider Selection (vertex_ai, ollama)
LLM_PROVIDER=vertex_ai
"""
    
    # Add GCP settings if not present
    if "GCP_PROJECT_ID" not in content:
        content += gcp_settings
    
    # Write updated content
    with open(env_file, 'w') as f:
        f.write(content)
    
    print("✅ Environment file updated")
    return True

def enable_apis(project_id):
    """Enable required GCP APIs"""
    print("\n🔌 Enabling required APIs...")
    
    apis = [
        'aiplatform.googleapis.com',
        'storage.googleapis.com',
        'cloudresourcemanager.googleapis.com'
    ]
    
    for api in apis:
        try:
            subprocess.run([
                'gcloud', 'services', 'enable', api,
                '--project', project_id
            ], check=True)
            print(f"✅ Enabled API: {api}")
        except subprocess.CalledProcessError:
            print(f"⚠️ Failed to enable API: {api}")

def main():
    """Main setup function"""
    print("🚀 Setting up Google Cloud Platform integration for FactForge")
    print("=" * 60)
    
    # Check if gcloud CLI is installed
    if not check_gcp_cli():
        if not install_gcp_cli():
            print("❌ Please install Google Cloud CLI manually and run this script again")
            return False
    
    # Setup authentication
    if not setup_authentication():
        print("❌ Authentication failed. Please try again.")
        return False
    
    # Create service account
    success, project_id = create_service_account()
    if not success:
        print("❌ Failed to create service account")
        return False
    
    # Create credentials file
    credentials_path = create_credentials_file(project_id)
    if not credentials_path:
        print("❌ Failed to create credentials file")
        return False
    
    # Update environment file
    if not update_env_file(project_id, credentials_path):
        print("❌ Failed to update environment file")
        return False
    
    # Enable APIs
    enable_apis(project_id)
    
    print("\n" + "=" * 60)
    print("✅ Google Cloud Platform setup completed!")
    print("\nNext steps:")
    print("1. Copy infra/env.sample to .env")
    print("2. Update .env with your specific settings")
    print("3. Run: docker-compose -f infra/docker-compose.yml up --build")
    print("4. Test the API: curl http://localhost:8000/api/check")
    
    return True

if __name__ == "__main__":
    main()
