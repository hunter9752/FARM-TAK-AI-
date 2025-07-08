#!/usr/bin/env python3
"""
Environment Setup Script for Farmer LLM Assistant
Helps users configure API keys easily
"""

import os
import json
import shutil


def create_env_file():
    """Create .env file from template"""
    template_file = ".env.template"
    env_file = ".env"
    
    if not os.path.exists(template_file):
        print("❌ .env.template file not found!")
        return False
    
    if os.path.exists(env_file):
        response = input("📝 .env file already exists. Overwrite? (y/n): ")
        if response.lower() != 'y':
            print("✅ Keeping existing .env file")
            return True
    
    try:
        shutil.copy(template_file, env_file)
        print(f"✅ Created {env_file} from template")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False


def get_api_key_interactive(provider, description, url):
    """Get API key interactively from user"""
    print(f"\n🔑 {provider.upper()} API Key Setup")
    print(f"Description: {description}")
    print(f"Get key from: {url}")
    print("")
    
    api_key = input(f"Enter your {provider} API key (or press Enter to skip): ").strip()
    
    if api_key and api_key != "your_api_key_here":
        return api_key
    else:
        print(f"⏭️ Skipping {provider}")
        return None


def update_env_file(api_keys):
    """Update .env file with API keys"""
    env_file = ".env"
    
    if not os.path.exists(env_file):
        print("❌ .env file not found!")
        return False
    
    try:
        # Read current .env file
        with open(env_file, "r") as f:
            lines = f.readlines()
        
        # Update lines with new API keys
        updated_lines = []
        for line in lines:
            line_updated = False
            for provider, key in api_keys.items():
                if key and line.strip().startswith(f"{provider.upper()}_API_KEY="):
                    updated_lines.append(f"{provider.upper()}_API_KEY={key}\n")
                    line_updated = True
                    break
            
            if not line_updated:
                updated_lines.append(line)
        
        # Write updated .env file
        with open(env_file, "w") as f:
            f.writelines(updated_lines)
        
        print("✅ Updated .env file with API keys")
        return True
        
    except Exception as e:
        print(f"❌ Failed to update .env file: {e}")
        return False


def test_api_keys():
    """Test if API keys are properly loaded"""
    try:
        # Load .env file
        if os.path.exists(".env"):
            with open(".env", "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip()
                        if value and value != "your_api_key_here":
                            os.environ[key] = value
        
        # Check which APIs are available
        available_apis = []
        api_keys = {
            "groq": os.getenv("GROQ_API_KEY"),
            "openai": os.getenv("OPENAI_API_KEY"),
            "gemini": os.getenv("GEMINI_API_KEY"),
            "huggingface": os.getenv("HUGGINGFACE_API_KEY")
        }
        
        for provider, key in api_keys.items():
            if key:
                available_apis.append(provider)
        
        if available_apis:
            print(f"\n✅ Available LLM APIs: {', '.join(available_apis)}")
            return True
        else:
            print("\n❌ No API keys found!")
            return False
            
    except Exception as e:
        print(f"❌ Error testing API keys: {e}")
        return False


def main():
    """Main setup function"""
    print("🌐 Farmer LLM Assistant - Environment Setup")
    print("=" * 60)
    
    # Step 1: Create .env file
    print("\n📋 Step 1: Creating .env file...")
    if not create_env_file():
        return
    
    # Step 2: Get API keys interactively
    print("\n📋 Step 2: Setting up API keys...")
    print("💡 You need at least one LLM API key to use the system")
    
    api_providers = {
        "groq": {
            "description": "Fast & Free tier - RECOMMENDED",
            "url": "https://console.groq.com/"
        },
        "openai": {
            "description": "High quality - Requires payment",
            "url": "https://platform.openai.com/api-keys"
        },
        "gemini": {
            "description": "Free Google AI model",
            "url": "https://makersuite.google.com/app/apikey"
        },
        "huggingface": {
            "description": "Open-source models - Optional",
            "url": "https://huggingface.co/settings/tokens"
        }
    }
    
    collected_keys = {}
    
    for provider, info in api_providers.items():
        api_key = get_api_key_interactive(provider, info["description"], info["url"])
        if api_key:
            collected_keys[provider] = api_key
    
    if not collected_keys:
        print("\n⚠️ No API keys provided. You can add them later by editing .env file")
        print("💡 At minimum, get a Groq API key from: https://console.groq.com/")
        return
    
    # Step 3: Update .env file
    print("\n📋 Step 3: Updating .env file...")
    if not update_env_file(collected_keys):
        return
    
    # Step 4: Test configuration
    print("\n📋 Step 4: Testing configuration...")
    if test_api_keys():
        print("\n🎉 Setup completed successfully!")
        print("\n🚀 Next steps:")
        print("1. Run: python cloud_llm_assistant.py")
        print("2. Or run complete system: python complete_cloud_farmer_assistant.py")
    else:
        print("\n❌ Setup incomplete. Please check your API keys.")
    
    print("\n💡 You can always edit .env file manually to add/change API keys")


if __name__ == "__main__":
    main()
