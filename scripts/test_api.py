#!/usr/bin/env python3
"""
GCP Emotion Decoding Chatbot - API Testing Script
This script tests all API endpoints of the emotion decoding chatbot
"""

import os
import sys
import json
import base64
import requests
from typing import Dict, Optional
from datetime import datetime
import argparse

# ANSI color codes
CLASS = {
    'GREEN': '\033[92m',
    'RED': '\033[91m',
    'YELLOW': '\033[93m',
    'BLUE': '\033[94m',
    'END': '\033[0m'
}

class APITester:
    """
    API Testing class for the Emotion Decoding Chatbot
    """
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.results = []
        
    def log(self, message: str, color: str = 'END'):
        """Print colored log message"""
        print(f"{CLASS.get(color, CLASS['END'])}{message}{CLASS['END']}")
    
    def test_health_check(self) -> bool:
        """
        Test the health check endpoint
        """
        self.log("\n" + "="*60, 'BLUE')
        self.log("Testing Health Check Endpoint", 'BLUE')
        self.log("="*60, 'BLUE')
        
        try:
            url = f"{self.base_url}/api/health"
            self.log(f"GET {url}", 'YELLOW')
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"✓ Health check passed", 'GREEN')
                self.log(f"Response: {json.dumps(data, indent=2)}")
                self.results.append(('Health Check', True))
                return True
            else:
                self.log(f"✗ Health check failed with status {response.status_code}", 'RED')
                self.results.append(('Health Check', False))
                return False
                
        except Exception as e:
            self.log(f"✗ Error: {str(e)}", 'RED')
            self.results.append(('Health Check', False))
            return False
    
    def test_text_analysis(self, text: str) -> bool:
        """
        Test text emotion analysis endpoint
        """
        self.log("\n" + "="*60, 'BLUE')
        self.log("Testing Text Analysis Endpoint", 'BLUE')
        self.log("="*60, 'BLUE')
        
        try:
            url = f"{self.base_url}/api/analyze/text"
            payload = {"text": text}
            
            self.log(f"POST {url}", 'YELLOW')
            self.log(f"Payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"✓ Text analysis successful", 'GREEN')
                self.log(f"Response: {json.dumps(data, indent=2)}")
                self.results.append(('Text Analysis', True))
                return True
            else:
                self.log(f"✗ Text analysis failed with status {response.status_code}", 'RED')
                self.log(f"Response: {response.text}")
                self.results.append(('Text Analysis', False))
                return False
                
        except Exception as e:
            self.log(f"✗ Error: {str(e)}", 'RED')
            self.results.append(('Text Analysis', False))
            return False
    
    def test_image_analysis(self, image_path: Optional[str] = None) -> bool:
        """
        Test image emotion analysis endpoint
        """
        self.log("\n" + "="*60, 'BLUE')
        self.log("Testing Image Analysis Endpoint", 'BLUE')
        self.log("="*60, 'BLUE')
        
        try:
            url = f"{self.base_url}/api/analyze/image"
            
            # If no image path provided, create a simple test payload
            if image_path and os.path.exists(image_path):
                with open(image_path, 'rb') as f:
                    image_data = base64.b64encode(f.read()).decode('utf-8')
                payload = {"image": image_data}
                self.log(f"Using image: {image_path}")
            else:
                # Use a placeholder or skip
                self.log("No valid image provided, skipping image test", 'YELLOW')
                self.results.append(('Image Analysis', None))
                return True
            
            self.log(f"POST {url}", 'YELLOW')
            
            response = requests.post(url, json=payload, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"✓ Image analysis successful", 'GREEN')
                self.log(f"Response: {json.dumps(data, indent=2)}")
                self.results.append(('Image Analysis', True))
                return True
            else:
                self.log(f"✗ Image analysis failed with status {response.status_code}", 'RED')
                self.log(f"Response: {response.text}")
                self.results.append(('Image Analysis', False))
                return False
                
        except Exception as e:
            self.log(f"✗ Error: {str(e)}", 'RED')
            self.results.append(('Image Analysis', False))
            return False
    
    def test_multimodal_analysis(self, text: str, image_path: Optional[str] = None) -> bool:
        """
        Test multimodal emotion analysis endpoint
        """
        self.log("\n" + "="*60, 'BLUE')
        self.log("Testing Multimodal Analysis Endpoint", 'BLUE')
        self.log("="*60, 'BLUE')
        
        try:
            url = f"{self.base_url}/api/analyze/multimodal"
            
            if image_path and os.path.exists(image_path):
                with open(image_path, 'rb') as f:
                    image_data = base64.b64encode(f.read()).decode('utf-8')
                payload = {"text": text, "image": image_data}
                self.log(f"Using image: {image_path}")
            else:
                self.log("No valid image provided, skipping multimodal test", 'YELLOW')
                self.results.append(('Multimodal Analysis', None))
                return True
            
            self.log(f"POST {url}", 'YELLOW')
            self.log(f"Text: {text}")
            
            response = requests.post(url, json=payload, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"✓ Multimodal analysis successful", 'GREEN')
                self.log(f"Response: {json.dumps(data, indent=2)}")
                self.results.append(('Multimodal Analysis', True))
                return True
            else:
                self.log(f"✗ Multimodal analysis failed with status {response.status_code}", 'RED')
                self.log(f"Response: {response.text}")
                self.results.append(('Multimodal Analysis', False))
                return False
                
        except Exception as e:
            self.log(f"✗ Error: {str(e)}", 'RED')
            self.results.append(('Multimodal Analysis', False))
            return False
    
    def print_summary(self):
        """
        Print test results summary
        """
        self.log("\n" + "="*60, 'BLUE')
        self.log("TEST SUMMARY", 'BLUE')
        self.log("="*60, 'BLUE')
        
        passed = sum(1 for _, result in self.results if result is True)
        failed = sum(1 for _, result in self.results if result is False)
        skipped = sum(1 for _, result in self.results if result is None)
        total = len(self.results)
        
        self.log(f"\nTotal Tests: {total}")
        self.log(f"Passed: {passed}", 'GREEN')
        self.log(f"Failed: {failed}", 'RED' if failed > 0 else 'END')
        self.log(f"Skipped: {skipped}", 'YELLOW' if skipped > 0 else 'END')
        
        self.log("\nDetailed Results:")
        for test_name, result in self.results:
            if result is True:
                self.log(f"  ✓ {test_name}", 'GREEN')
            elif result is False:
                self.log(f"  ✗ {test_name}", 'RED')
            else:
                self.log(f"  ○ {test_name} (skipped)", 'YELLOW')
        
        self.log("\n" + "="*60, 'BLUE')
        
        if failed == 0:
            self.log("ALL TESTS PASSED!", 'GREEN')
            return 0
        else:
            self.log(f"{failed} TEST(S) FAILED", 'RED')
            return 1

def main():
    """
    Main function to run API tests
    """
    parser = argparse.ArgumentParser(
        description='Test GCP Emotion Decoding Chatbot API endpoints'
    )
    parser.add_argument(
        '--url',
        default='http://localhost:8080',
        help='Base URL of the API (default: http://localhost:8080)'
    )
    parser.add_argument(
        '--text',
        default='I am feeling incredibly happy and excited today!',
        help='Text to use for testing'
    )
    parser.add_argument(
        '--image',
        help='Path to image file for testing'
    )
    
    args = parser.parse_args()
    
    print(f"\n{CLASS['BLUE']}GCP Emotion Decoding Chatbot - API Test Suite{CLASS['END']}")
    print(f"{CLASS['BLUE']}Target URL: {args.url}{CLASS['END']}")
    print(f"{CLASS['BLUE']}Timestamp: {datetime.now().isoformat()}{CLASS['END']}")
    
    tester = APITester(args.url)
    
    # Run tests
    tester.test_health_check()
    tester.test_text_analysis(args.text)
    tester.test_image_analysis(args.image)
    tester.test_multimodal_analysis(args.text, args.image)
    
    # Print summary and exit
    exit_code = tester.print_summary()
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
