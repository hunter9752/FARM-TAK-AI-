#!/usr/bin/env python3
"""
Test script for the Real-time STT Application
Tests core functionality without requiring actual models
"""

import unittest
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add current directory to path to import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from realtime_stt import RealtimeSTT
from download_models import ModelDownloader


class TestRealtimeSTT(unittest.TestCase):
    """Test cases for RealtimeSTT class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.stt = RealtimeSTT()
        
    def test_initialization(self):
        """Test STT application initialization"""
        self.assertIsNotNone(self.stt.language_models)
        self.assertEqual(len(self.stt.language_models), 4)
        self.assertIn('en', self.stt.language_models)
        self.assertIn('hi', self.stt.language_models)
        self.assertIn('mr', self.stt.language_models)
        self.assertIn('ta', self.stt.language_models)
        
    def test_language_models_structure(self):
        """Test language models have correct structure"""
        for lang_code, lang_info in self.stt.language_models.items():
            self.assertIn('name', lang_info)
            self.assertIn('model_path', lang_info)
            self.assertIn('sample_rate', lang_info)
            self.assertEqual(lang_info['sample_rate'], 16000)
            
    def test_model_path_check(self):
        """Test model existence checking"""
        # Test with non-existent path
        result = self.stt.check_model_exists("non_existent_path")
        self.assertFalse(result)
        
    @patch('builtins.input', return_value='en')
    def test_language_selection_valid(self, mock_input):
        """Test valid language selection"""
        result = self.stt.select_language()
        self.assertTrue(result)
        self.assertEqual(self.stt.selected_language, 'en')
        
    @patch('builtins.input', side_effect=['invalid', 'hi'])
    def test_language_selection_invalid_then_valid(self, mock_input):
        """Test invalid then valid language selection"""
        with patch('builtins.print'):  # Suppress print output
            result = self.stt.select_language()
        self.assertTrue(result)
        self.assertEqual(self.stt.selected_language, 'hi')
        
    def test_audio_configuration(self):
        """Test audio configuration parameters"""
        self.assertEqual(self.stt.sample_rate, 16000)
        self.assertEqual(self.stt.block_size, 8000)
        self.assertIsInstance(self.stt.audio_queue, type(self.stt.audio_queue))


class TestModelDownloader(unittest.TestCase):
    """Test cases for ModelDownloader class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.downloader = ModelDownloader()
        
    def test_initialization(self):
        """Test downloader initialization"""
        self.assertIsNotNone(self.downloader.models_config)
        self.assertEqual(len(self.downloader.models_config), 4)
        
    def test_models_config_structure(self):
        """Test models configuration structure"""
        for model_code, config in self.downloader.models_config.items():
            self.assertIn('name', config)
            self.assertIn('url', config)
            self.assertIn('filename', config)
            self.assertIn('extracted_dir', config)
            self.assertTrue(config['url'].startswith('https://'))
            self.assertTrue(config['filename'].endswith('.zip'))
            
    def test_model_installation_check(self):
        """Test model installation checking"""
        # Test with non-existent model
        result = self.downloader.is_model_installed('en')
        self.assertFalse(result)
        
    def test_models_directory_creation(self):
        """Test models directory creation"""
        # This should not raise an exception
        self.downloader.create_models_directory()
        self.assertTrue(self.downloader.models_dir.exists())


class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def test_language_codes_consistency(self):
        """Test that language codes are consistent between STT and downloader"""
        stt = RealtimeSTT()
        downloader = ModelDownloader()
        
        stt_languages = set(stt.language_models.keys())
        downloader_languages = set(downloader.models_config.keys())
        
        self.assertEqual(stt_languages, downloader_languages)
        
    def test_model_paths_consistency(self):
        """Test that model paths are consistent"""
        stt = RealtimeSTT()
        downloader = ModelDownloader()
        
        for lang_code in stt.language_models:
            stt_path = stt.language_models[lang_code]['model_path']
            expected_dir = downloader.models_config[lang_code]['extracted_dir']
            
            # Check that STT path ends with the expected directory
            self.assertTrue(stt_path.endswith(expected_dir))


def run_functionality_test():
    """Run a basic functionality test"""
    print("🧪 Running Functionality Tests")
    print("=" * 50)
    
    # Test 1: Import modules
    try:
        from realtime_stt import RealtimeSTT
        from download_models import ModelDownloader
        print("✅ Module imports successful")
    except Exception as e:
        print(f"❌ Module import failed: {e}")
        return False
        
    # Test 2: Create instances
    try:
        stt = RealtimeSTT()
        downloader = ModelDownloader()
        print("✅ Object instantiation successful")
    except Exception as e:
        print(f"❌ Object instantiation failed: {e}")
        return False
        
    # Test 3: Check configurations
    try:
        assert len(stt.language_models) == 4
        assert len(downloader.models_config) == 4
        print("✅ Configuration validation successful")
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False
        
    # Test 4: Check dependencies
    try:
        import vosk
        import sounddevice
        import queue
        import json
        print("✅ Dependencies check successful")
    except Exception as e:
        print(f"❌ Dependencies check failed: {e}")
        return False
        
    print("\n🎉 All functionality tests passed!")
    return True


def main():
    """Main test function"""
    print("🚀 Starting STT Application Tests")
    print("=" * 60)
    
    # Run functionality tests first
    if not run_functionality_test():
        print("\n❌ Functionality tests failed!")
        return
        
    print("\n🧪 Running Unit Tests")
    print("=" * 50)
    
    # Run unit tests
    unittest.main(verbosity=2, exit=False)
    
    print("\n✅ All tests completed!")


if __name__ == "__main__":
    main()
