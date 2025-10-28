#!/usr/bin/env python3
"""
GCP Emotion Decoding Chatbot - Main Application
Author: Moataz Alsbak
Description: Multimodal emotion analysis chatbot using Vertex AI Multimodal
License: MIT
"""

import os
import json
import base64
from typing import Dict, List, Optional, Union
from datetime import datetime
import logging

from flask import Flask, request, jsonify, render_template
from google.cloud import aiplatform
from google.cloud import storage
from vertexai.preview.generative_models import GenerativeModel, Part
import vertexai

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configuration from environment variables
PROJECT_ID = os.getenv('GCP_PROJECT_ID', 'your-project-id')
LOCATION = os.getenv('GCP_LOCATION', 'us-central1')
BUCKET_NAME = os.getenv('GCS_BUCKET_NAME', 'emotion-chatbot-assets')
MODEL_NAME = os.getenv('VERTEX_MODEL', 'gemini-pro-vision')

# Initialize Vertex AI
try:
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    logger.info(f"Vertex AI initialized for project: {PROJECT_ID}")
except Exception as e:
    logger.error(f"Failed to initialize Vertex AI: {str(e)}")
    raise

class EmotionDecoder:
    """
    Main class for emotion decoding from multimodal inputs
    """
    
    def __init__(self):
        self.model = GenerativeModel(MODEL_NAME)
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket(BUCKET_NAME)
        
        # Emotion categories
        self.emotions = [
            'joy', 'sadness', 'anger', 'fear', 'surprise', 
            'disgust', 'neutral', 'love', 'excitement', 'anxiety'
        ]
        
    def analyze_text_emotion(self, text: str) -> Dict:
        """
        Analyze emotion from text input
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with emotion analysis results
        """
        try:
            prompt = f"""
            Analyze the emotional content of the following text. 
            Identify the primary emotion and provide:
            1. Primary emotion (from: {', '.join(self.emotions)})
            2. Confidence score (0-100)
            3. Secondary emotions if present
            4. Emotional intensity (low, medium, high)
            5. Brief explanation
            
            Text: "{text}"
            
            Respond in JSON format.
            """
            
            response = self.model.generate_content(prompt)
            result = self._parse_emotion_response(response.text)
            result['input_type'] = 'text'
            result['timestamp'] = datetime.now().isoformat()
            
            logger.info(f"Text emotion analyzed: {result.get('primary_emotion', 'unknown')}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing text emotion: {str(e)}")
            return self._error_response(str(e))
    
    def analyze_image_emotion(self, image_data: Union[str, bytes], 
                            image_uri: Optional[str] = None) -> Dict:
        """
        Analyze emotion from image input (facial expression, body language)
        
        Args:
            image_data: Base64 encoded image or bytes
            image_uri: Optional GCS URI for the image
            
        Returns:
            Dictionary with emotion analysis results
        """
        try:
            prompt = f"""
            Analyze the emotional content in this image. Look for:
            1. Facial expressions
            2. Body language
            3. Environmental context
            
            Provide:
            1. Primary emotion detected
            2. Confidence score (0-100)
            3. Additional emotions if present
            4. Visual cues that led to this analysis
            5. Emotional intensity
            
            Respond in JSON format.
            """
            
            # Prepare image part
            if image_uri:
                image_part = Part.from_uri(image_uri, mime_type="image/jpeg")
            else:
                if isinstance(image_data, str):
                    image_bytes = base64.b64decode(image_data)
                else:
                    image_bytes = image_data
                image_part = Part.from_data(image_bytes, mime_type="image/jpeg")
            
            response = self.model.generate_content([prompt, image_part])
            result = self._parse_emotion_response(response.text)
            result['input_type'] = 'image'
            result['timestamp'] = datetime.now().isoformat()
            
            logger.info(f"Image emotion analyzed: {result.get('primary_emotion', 'unknown')}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing image emotion: {str(e)}")
            return self._error_response(str(e))
    
    def analyze_multimodal_emotion(self, text: str, image_data: Union[str, bytes],
                                  image_uri: Optional[str] = None) -> Dict:
        """
        Analyze emotion from combined text and image inputs
        
        Args:
            text: Text input
            image_data: Image data
            image_uri: Optional GCS URI
            
        Returns:
            Dictionary with combined emotion analysis
        """
        try:
            prompt = f"""
            Analyze the emotional content from both the text and the image provided.
            Consider how the text and visual information complement or contrast each other.
            
            Text: "{text}"
            
            Provide:
            1. Overall primary emotion
            2. Confidence score (0-100)
            3. Text-based emotion
            4. Image-based emotion
            5. Consistency analysis (aligned/misaligned)
            6. Combined emotional interpretation
            7. Intensity assessment
            
            Respond in JSON format.
            """
            
            # Prepare image part
            if image_uri:
                image_part = Part.from_uri(image_uri, mime_type="image/jpeg")
            else:
                if isinstance(image_data, str):
                    image_bytes = base64.b64decode(image_data)
                else:
                    image_bytes = image_data
                image_part = Part.from_data(image_bytes, mime_type="image/jpeg")
            
            response = self.model.generate_content([prompt, image_part])
            result = self._parse_emotion_response(response.text)
            result['input_type'] = 'multimodal'
            result['timestamp'] = datetime.now().isoformat()
            
            logger.info(f"Multimodal emotion analyzed: {result.get('primary_emotion', 'unknown')}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing multimodal emotion: {str(e)}")
            return self._error_response(str(e))
    
    def _parse_emotion_response(self, response_text: str) -> Dict:
        """
        Parse the model's response into structured format
        """
        try:
            # Try to extract JSON from response
            if '```json' in response_text:
                json_str = response_text.split('```json')[1].split('```')[0]
            elif '```' in response_text:
                json_str = response_text.split('```')[1].split('```')[0]
            else:
                json_str = response_text
            
            result = json.loads(json_str.strip())
            return result
        except:
            # Fallback: return raw text
            return {
                'primary_emotion': 'unknown',
                'confidence': 0,
                'explanation': response_text,
                'raw_response': response_text
            }
    
    def _error_response(self, error_msg: str) -> Dict:
        """
        Generate error response
        """
        return {
            'error': True,
            'message': error_msg,
            'primary_emotion': 'error',
            'confidence': 0,
            'timestamp': datetime.now().isoformat()
        }

# Initialize emotion decoder
decoder = EmotionDecoder()

# API Routes
@app.route('/')
def home():
    """
    Home page
    """
    return render_template('index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    """
    return jsonify({
        'status': 'healthy',
        'service': 'GCP Emotion Decoding Chatbot',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/analyze/text', methods=['POST'])
def analyze_text():
    """
    Analyze emotion from text
    
    Request body:
    {
        "text": "Your text here"
    }
    """
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        result = decoder.analyze_text_emotion(text)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in analyze_text endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze/image', methods=['POST'])
def analyze_image():
    """
    Analyze emotion from image
    
    Request body:
    {
        "image": "base64_encoded_image" or "image_uri": "gs://bucket/path"
    }
    """
    try:
        data = request.get_json()
        image_data = data.get('image')
        image_uri = data.get('image_uri')
        
        if not image_data and not image_uri:
            return jsonify({'error': 'Image data or URI is required'}), 400
        
        result = decoder.analyze_image_emotion(image_data, image_uri)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in analyze_image endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze/multimodal', methods=['POST'])
def analyze_multimodal():
    """
    Analyze emotion from text and image combined
    
    Request body:
    {
        "text": "Your text",
        "image": "base64_encoded_image" or "image_uri": "gs://bucket/path"
    }
    """
    try:
        data = request.get_json()
        text = data.get('text', '')
        image_data = data.get('image')
        image_uri = data.get('image_uri')
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        if not image_data and not image_uri:
            return jsonify({'error': 'Image data or URI is required'}), 400
        
        result = decoder.analyze_multimodal_emotion(text, image_data, image_uri)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in analyze_multimodal endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
