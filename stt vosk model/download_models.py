#!/usr/bin/env python3
"""
Model downloader for Vosk STT Application
Downloads and extracts required language models
"""

import os
import sys
import urllib.request
import zipfile
from pathlib import Path


class ModelDownloader:
    """Downloads and manages Vosk language models"""
    
    def __init__(self):
        """Initialize the model downloader"""
        self.models_dir = Path("models")
        self.models_config = {
            "en": {
                "name": "English (Small)",
                "url": "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip",
                "filename": "vosk-model-small-en-us-0.15.zip",
                "extracted_dir": "vosk-model-small-en-us-0.15"
            },
            "hi": {
                "name": "Hindi",
                "url": "https://alphacephei.com/vosk/models/vosk-model-hi-0.22.zip",
                "filename": "vosk-model-hi-0.22.zip", 
                "extracted_dir": "vosk-model-hi-0.22"
            },
            "mr": {
                "name": "Marathi",
                "url": "https://alphacephei.com/vosk/models/vosk-model-mr-0.22.zip",
                "filename": "vosk-model-mr-0.22.zip",
                "extracted_dir": "vosk-model-mr-0.22"
            },
            "ta": {
                "name": "Tamil", 
                "url": "https://alphacephei.com/vosk/models/vosk-model-ta-0.22.zip",
                "filename": "vosk-model-ta-0.22.zip",
                "extracted_dir": "vosk-model-ta-0.22"
            }
        }
        
    def create_models_directory(self):
        """Create models directory if it doesn't exist"""
        self.models_dir.mkdir(exist_ok=True)
        print(f"📁 Models directory: {self.models_dir.absolute()}")
        
    def download_file(self, url, filename):
        """Download a file with progress indication"""
        filepath = self.models_dir / filename
        
        def progress_hook(block_num, block_size, total_size):
            downloaded = block_num * block_size
            if total_size > 0:
                percent = min(100, (downloaded * 100) // total_size)
                print(f"\r📥 Downloading: {percent}% ({downloaded // (1024*1024)}MB / {total_size // (1024*1024)}MB)", end="")
            else:
                print(f"\r📥 Downloaded: {downloaded // (1024*1024)}MB", end="")
                
        try:
            urllib.request.urlretrieve(url, filepath, progress_hook)
            print()  # New line after progress
            return filepath
        except Exception as e:
            print(f"\n❌ Download failed: {e}")
            return None
            
    def extract_model(self, zip_path, expected_dir):
        """Extract model zip file"""
        try:
            print(f"📦 Extracting {zip_path.name}...")
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.models_dir)
                
            # Verify extraction
            extracted_path = self.models_dir / expected_dir
            if extracted_path.exists():
                print(f"✅ Extracted to: {extracted_path}")
                # Clean up zip file
                zip_path.unlink()
                return True
            else:
                print(f"❌ Expected directory not found: {extracted_path}")
                return False
                
        except Exception as e:
            print(f"❌ Extraction failed: {e}")
            return False
            
    def is_model_installed(self, model_code):
        """Check if a model is already installed"""
        config = self.models_config[model_code]
        model_path = self.models_dir / config["extracted_dir"]
        
        if not model_path.exists():
            return False
            
        # Check for required files
        required_files = ['am', 'final.mdl', 'global_cmvn.stats', 'mfcc.conf', 'words.txt']
        for file in required_files:
            if not (model_path / file).exists():
                return False
                
        return True
        
    def download_model(self, model_code):
        """Download and install a specific model"""
        if model_code not in self.models_config:
            print(f"❌ Unknown model code: {model_code}")
            return False
            
        config = self.models_config[model_code]
        
        # Check if already installed
        if self.is_model_installed(model_code):
            print(f"✅ {config['name']} model already installed")
            return True
            
        print(f"\n🔄 Downloading {config['name']} model...")
        print(f"📍 URL: {config['url']}")
        
        # Download
        zip_path = self.download_file(config['url'], config['filename'])
        if not zip_path:
            return False
            
        # Extract
        if self.extract_model(zip_path, config['extracted_dir']):
            print(f"✅ {config['name']} model installed successfully!")
            return True
        else:
            return False
            
    def download_all_models(self):
        """Download all available models"""
        print("🚀 Downloading all language models...")
        
        success_count = 0
        for model_code in self.models_config:
            if self.download_model(model_code):
                success_count += 1
                
        print(f"\n📊 Summary: {success_count}/{len(self.models_config)} models installed")
        return success_count == len(self.models_config)
        
    def list_models(self):
        """List available models and their status"""
        print("\n📋 Available Models:")
        print("-" * 50)
        
        for code, config in self.models_config.items():
            status = "✅ Installed" if self.is_model_installed(code) else "❌ Not installed"
            print(f"{code.upper()}: {config['name']} - {status}")
            
    def interactive_download(self):
        """Interactive model selection and download"""
        while True:
            self.list_models()
            print("\n🎯 Options:")
            print("  all - Download all models")
            print("  en/hi/mr/ta - Download specific language")
            print("  quit - Exit")
            
            choice = input("\nEnter your choice: ").lower().strip()
            
            if choice == "quit":
                break
            elif choice == "all":
                self.download_all_models()
                break
            elif choice in self.models_config:
                self.download_model(choice)
            else:
                print("❌ Invalid choice. Please try again.")
                
    def run(self):
        """Main entry point"""
        print("=" * 60)
        print("📥 Vosk Model Downloader")
        print("=" * 60)
        
        # Create models directory
        self.create_models_directory()
        
        # Check command line arguments
        if len(sys.argv) > 1:
            if sys.argv[1] == "all":
                self.download_all_models()
            elif sys.argv[1] in self.models_config:
                self.download_model(sys.argv[1])
            else:
                print(f"❌ Unknown argument: {sys.argv[1]}")
                print("Usage: python download_models.py [all|en|hi|mr|ta]")
        else:
            # Interactive mode
            self.interactive_download()
            
        print("\n👋 Download complete!")


def main():
    """Main function"""
    downloader = ModelDownloader()
    downloader.run()


if __name__ == "__main__":
    main()
