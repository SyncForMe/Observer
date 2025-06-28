#!/usr/bin/env python3
import requests
import json
import os
import sys
from dotenv import load_dotenv
import io
import tempfile
import wave
import numpy as np
import time

# Load environment variables from frontend/.env
load_dotenv('/app/frontend/.env')

# Get the backend URL from environment variables
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    print("Error: REACT_APP_BACKEND_URL not found in environment variables")
    sys.exit(1)

# Ensure the URL ends with /api
API_URL = f"{BACKEND_URL}/api"
print(f"Using API URL: {API_URL}")

# Load JWT secret from backend/.env for testing
load_dotenv('/app/backend/.env')
JWT_SECRET = os.environ.get('JWT_SECRET')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

if not JWT_SECRET:
    print("Warning: JWT_SECRET not found in environment variables. Some tests may fail.")

if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here":
    print("Warning: OPENAI_API_KEY not set or using default value. Transcription will likely fail.")
else:
    print(f"Using OPENAI_API_KEY: {OPENAI_API_KEY[:4]}...{OPENAI_API_KEY[-4:]}")

def create_simple_wav_file():
    """Create a simple WAV file with a sine wave"""
    # Parameters
    duration = 2  # seconds
    sample_rate = 44100  # Hz
    frequency = 440  # Hz (A4 note)
    
    # Generate sine wave
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    sine_wave = np.sin(2 * np.pi * frequency * t)
    
    # Normalize to 16-bit range
    audio = sine_wave * 32767 / np.max(np.abs(sine_wave))
    audio = audio.astype(np.int16)
    
    # Create a temporary file
    temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    temp_file_path = temp_file.name
    temp_file.close()
    
    # Write WAV file
    with wave.open(temp_file_path, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio.tobytes())
    
    print(f"Created simple WAV file at {temp_file_path}")
    return temp_file_path

def test_login():
    """Login with admin credentials to get auth token"""
    login_data = {
        "email": "dino@cytonic.com",
        "password": "Observerinho8"
    }
    
    url = f"{API_URL}/auth/login"
    print(f"Logging in with admin credentials: {url}")
    
    try:
        response = requests.post(url, json=login_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            auth_token = response_data.get("access_token")
            user_data = response_data.get("user", {})
            user_id = user_data.get("id")
            print(f"Login successful. User ID: {user_id}")
            print(f"JWT Token: {auth_token}")
            return auth_token
        else:
            print(f"Login failed: {response.text}")
            
            # Try test login as fallback
            print("Trying test login endpoint...")
            test_url = f"{API_URL}/auth/test-login"
            test_response = requests.post(test_url)
            
            if test_response.status_code == 200:
                test_data = test_response.json()
                test_token = test_data.get("access_token")
                test_user = test_data.get("user", {})
                test_id = test_user.get("id")
                print(f"Test login successful. User ID: {test_id}")
                print(f"JWT Token: {test_token}")
                return test_token
            else:
                print(f"Test login failed: {test_response.text}")
                return None
    except Exception as e:
        print(f"Error during login: {e}")
        return None

def test_transcribe_with_wav_file(auth_token):
    """Test the transcribe-scenario endpoint with a simple WAV file"""
    if not auth_token:
        print("Cannot test transcription without authentication")
        return False
    
    # Create a simple WAV file
    wav_file_path = create_simple_wav_file()
    
    # Prepare the request
    url = f"{API_URL}/speech/transcribe-scenario"
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    print(f"\nTesting transcribe-scenario endpoint with WAV file: {url}")
    print(f"Headers: {headers}")
    
    try:
        with open(wav_file_path, 'rb') as f:
            files = {'audio': ('test.wav', f, 'audio/wav')}
            
            # Send the request
            print("Sending request...")
            start_time = time.time()
            response = requests.post(url, headers=headers, files=files)
            end_time = time.time()
            
            print(f"Status Code: {response.status_code}")
            print(f"Response Time: {end_time - start_time:.2f} seconds")
            
            # Print response headers
            print("Response Headers:")
            for key, value in response.headers.items():
                print(f"  {key}: {value}")
            
            # Try to parse JSON response
            try:
                response_data = response.json()
                print(f"Response: {json.dumps(response_data, indent=2)}")
                
                # Check for success
                if response.status_code == 200 and response_data.get("success"):
                    print("✅ Transcription successful!")
                    return True
                else:
                    print("❌ Transcription failed with error response")
                    return False
            except json.JSONDecodeError:
                print(f"Response is not JSON: {response.text}")
                return False
    except Exception as e:
        print(f"Error during transcription test: {e}")
        return False
    finally:
        # Clean up the temporary file
        if os.path.exists(wav_file_path):
            os.unlink(wav_file_path)
            print(f"Deleted temporary WAV file: {wav_file_path}")

def test_transcribe_with_invalid_format(auth_token):
    """Test the transcribe-scenario endpoint with an invalid file format"""
    if not auth_token:
        print("Cannot test transcription without authentication")
        return False
    
    # Create a text file instead of audio
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
        temp_file.write(b"This is not an audio file")
        temp_file_path = temp_file.name
    
    # Prepare the request
    url = f"{API_URL}/speech/transcribe-scenario"
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    print(f"\nTesting transcribe-scenario endpoint with invalid file format: {url}")
    
    try:
        with open(temp_file_path, 'rb') as f:
            files = {'audio': ('test.txt', f, 'text/plain')}
            
            # Send the request
            response = requests.post(url, headers=headers, files=files)
            
            print(f"Status Code: {response.status_code}")
            
            # Try to parse JSON response
            try:
                response_data = response.json()
                print(f"Response: {json.dumps(response_data, indent=2)}")
                
                # Check for expected error
                if response.status_code == 400 and "Invalid audio format" in str(response_data):
                    print("✅ Invalid format correctly rejected with 400 status code")
                    return True
                else:
                    print("❌ Invalid format not properly rejected")
                    return False
            except json.JSONDecodeError:
                print(f"Response is not JSON: {response.text}")
                return False
    except Exception as e:
        print(f"Error during invalid format test: {e}")
        return False
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

def test_transcribe_without_auth():
    """Test the transcribe-scenario endpoint without authentication"""
    # Prepare the request
    url = f"{API_URL}/speech/transcribe-scenario"
    
    print(f"\nTesting transcribe-scenario endpoint without authentication: {url}")
    
    try:
        # Create a simple text file as dummy data
        with tempfile.NamedTemporaryFile(suffix='.txt') as temp_file:
            temp_file.write(b"Test data")
            temp_file.flush()
            
            with open(temp_file.name, 'rb') as f:
                files = {'audio': ('test.txt', f, 'text/plain')}
                
                # Send the request without auth header
                response = requests.post(url, files=files)
                
                print(f"Status Code: {response.status_code}")
                
                # Try to parse JSON response
                try:
                    response_data = response.json()
                    print(f"Response: {json.dumps(response_data, indent=2)}")
                    
                    # Check for expected error
                    if response.status_code == 403:
                        print("✅ Unauthenticated request correctly rejected with 403 status code")
                        return True
                    else:
                        print("❌ Unauthenticated request not properly rejected")
                        return False
                except json.JSONDecodeError:
                    print(f"Response is not JSON: {response.text}")
                    if response.status_code == 403:
                        print("✅ Unauthenticated request correctly rejected with 403 status code")
                        return True
                    return False
    except Exception as e:
        print(f"Error during unauthenticated test: {e}")
        return False

def check_openai_api_key():
    """Check if the OpenAI API key is properly set"""
    print("\nChecking OpenAI API key configuration:")
    
    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY not found in environment variables")
        return False
    
    if OPENAI_API_KEY == "your_openai_api_key_here":
        print("❌ OPENAI_API_KEY is set to the default placeholder value")
        return False
    
    print(f"✅ OPENAI_API_KEY is set: {OPENAI_API_KEY[:4]}...{OPENAI_API_KEY[-4:]}")
    return True

def check_pydub_installation():
    """Check if pydub is installed and working"""
    print("\nChecking pydub installation:")
    
    try:
        import pydub
        print(f"✅ pydub is installed")
        
        # Check if ffmpeg is available
        try:
            # Create a simple silent audio segment
            silent_audio = pydub.AudioSegment.silent(duration=100)
            print("✅ pydub can create audio segments")
            
            # Check if ffmpeg is available by running a command
            import subprocess
            result = subprocess.run(['which', 'ffmpeg'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ ffmpeg found at: {result.stdout.strip()}")
                return True
            else:
                print("❌ ffmpeg not found in PATH")
                return False
        except Exception as e:
            print(f"❌ ffmpeg not properly configured: {e}")
            return False
    except ImportError:
        print("❌ pydub is not installed")
        return False
    except Exception as e:
        print(f"❌ Error checking pydub: {e}")
        return False

def main():
    """Run all tests"""
    print("="*80)
    print("VOICE TRANSCRIPTION DEBUGGING TESTS")
    print("="*80)
    
    # Check dependencies
    openai_key_ok = check_openai_api_key()
    pydub_ok = check_pydub_installation()
    
    # Login to get auth token
    auth_token = test_login()
    
    # Run tests
    if auth_token:
        # Test with invalid format
        invalid_format_test = test_transcribe_with_invalid_format(auth_token)
        
        # Test without authentication
        no_auth_test = test_transcribe_without_auth()
        
        # Only test with WAV file if dependencies are OK
        if openai_key_ok and pydub_ok:
            wav_test = test_transcribe_with_wav_file(auth_token)
        else:
            print("\n❌ Skipping WAV file test due to missing dependencies")
            wav_test = False
        
        # Print summary
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        print(f"OpenAI API Key: {'✅ OK' if openai_key_ok else '❌ Missing or invalid'}")
        print(f"pydub Installation: {'✅ OK' if pydub_ok else '❌ Issues detected'}")
        print(f"Authentication: {'✅ OK' if auth_token else '❌ Failed'}")
        print(f"Invalid Format Test: {'✅ Passed' if invalid_format_test else '❌ Failed'}")
        print(f"No Authentication Test: {'✅ Passed' if no_auth_test else '❌ Failed'}")
        if openai_key_ok and pydub_ok:
            print(f"WAV File Test: {'✅ Passed' if wav_test else '❌ Failed'}")
        
        # Overall result
        if (invalid_format_test and no_auth_test and 
            ((openai_key_ok and pydub_ok and wav_test) or not (openai_key_ok and pydub_ok))):
            print("\n✅ All applicable tests passed!")
        else:
            print("\n❌ Some tests failed!")
    else:
        print("\n❌ Authentication failed, cannot run tests!")

if __name__ == "__main__":
    main()