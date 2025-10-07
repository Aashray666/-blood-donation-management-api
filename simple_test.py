#!/usr/bin/env python3
"""
Simple integration test for Windows compatibility
"""

import asyncio
import aiohttp
import json
import sys
import subprocess
import time

BASE_URL = "http://localhost:8004"

async def run_simple_test():
    """Run a simple integration test"""
    
    # Initialize database
    print("Initializing database...")
    try:
        subprocess.run([sys.executable, "init_db.py"], check=True)
        print("[SUCCESS] Database ready")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Database setup failed: {e}")
        return False
    
    # Start server
    print("Starting server...")
    server_process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", "main:app", 
        "--host", "127.0.0.1", "--port", "8004"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    try:
        # Wait for server
        time.sleep(4)
        
        # Test with session
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            
            # Test health check
            print("Testing health check...")
            try:
                async with session.get(f"{BASE_URL}/health") as response:
                    if response.status == 200:
                        print("[SUCCESS] Health check passed")
                    else:
                        print(f"[ERROR] Health check failed: {response.status}")
                        return False
            except Exception as e:
                print(f"[ERROR] Health check failed: {e}")
                return False
            
            # Test donor creation
            print("Testing donor creation...")
            donor_data = {
                "name": "Test Donor",
                "blood_group": "O+",
                "city": "Test City",
                "contact_number": "1234567890",
                "email": "test@example.com"
            }
            
            try:
                async with session.post(f"{BASE_URL}/api/donors", json=donor_data) as response:
                    if response.status == 201:
                        donor = await response.json()
                        donor_id = donor["id"]
                        print(f"[SUCCESS] Donor created (ID: {donor_id})")
                    else:
                        text = await response.text()
                        print(f"[ERROR] Donor creation failed: {response.status} - {text}")
                        return False
            except Exception as e:
                print(f"[ERROR] Donor creation failed: {e}")
                return False
            
            # Test blood request creation
            print("Testing blood request creation...")
            request_data = {
                "patient_name": "Test Patient",
                "blood_group": "O+",
                "city": "Test City",
                "urgency": "High",
                "hospital_name": "Test Hospital",
                "contact_number": "0987654321"
            }
            
            try:
                async with session.post(f"{BASE_URL}/api/requests", json=request_data) as response:
                    if response.status == 201:
                        request = await response.json()
                        request_id = request["id"]
                        print(f"[SUCCESS] Blood request created (ID: {request_id})")
                    else:
                        text = await response.text()
                        print(f"[ERROR] Blood request creation failed: {response.status} - {text}")
                        return False
            except Exception as e:
                print(f"[ERROR] Blood request creation failed: {e}")
                return False
            
            # Test matching
            print("Testing donor matching...")
            try:
                async with session.get(f"{BASE_URL}/api/requests/{request_id}/matches") as response:
                    if response.status == 200:
                        matches = await response.json()
                        print(f"[SUCCESS] Found {len(matches)} matching donors")
                    else:
                        text = await response.text()
                        print(f"[ERROR] Matching failed: {response.status} - {text}")
                        return False
            except Exception as e:
                print(f"[ERROR] Matching failed: {e}")
                return False
            
            # Cleanup
            print("Cleaning up...")
            try:
                # Delete request
                async with session.delete(f"{BASE_URL}/api/requests/{request_id}") as response:
                    if response.status == 204:
                        print("[SUCCESS] Request deleted")
                    else:
                        print(f"[WARNING] Request deletion status: {response.status}")
                
                # Delete donor
                async with session.delete(f"{BASE_URL}/api/donors/{donor_id}") as response:
                    if response.status == 204:
                        print("[SUCCESS] Donor deleted")
                    else:
                        print(f"[WARNING] Donor deletion status: {response.status}")
                        
            except Exception as e:
                print(f"[WARNING] Cleanup failed: {e}")
            
            print("\n[SUCCESS] All tests completed successfully!")
            return True
            
    finally:
        # Stop server
        print("Stopping server...")
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()
        print("[SUCCESS] Server stopped")

async def main():
    """Main function"""
    try:
        success = await run_simple_test()
        return success
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        print(f"\nTest result: {'PASSED' if success else 'FAILED'}")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1)