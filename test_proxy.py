#!/usr/bin/env python3
"""
Test script for the OpenAI proxy server.
This script sends a simple request to test if the proxy is working correctly.
"""

import asyncio
import aiohttp
import argparse
import json
import sys

async def test_proxy(proxy_host: str, proxy_port: int):
    """Test the proxy server with a simple OpenAI API request"""
    
    # Test URL - using the models endpoint as it doesn't require specific API keys
    test_url = f"http://{proxy_host}:{proxy_port}/v1/models"
    
    print(f"Testing proxy at {proxy_host}:{proxy_port}")
    print(f"Target URL: {test_url}")
    print("-" * 50)
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test GET request
            print("Testing GET request...")
            async with session.get(test_url) as response:
                print(f"Status: {response.status}")
                print(f"Headers: {dict(response.headers)}")
                
                if response.status == 200:
                    data = await response.json()
                    print("✅ Proxy is working correctly!")
                    print(f"Response contains {len(data.get('data', []))} models")
                elif response.status == 401:
                    print("✅ Proxy is working (got 401 - authentication required)")
                    print("This is expected without a valid API key")
                else:
                    print(f"⚠️  Proxy returned status {response.status}")
                    text = await response.text()
                    print(f"Response: {text[:200]}...")
                
    except aiohttp.ClientConnectorError as e:
        print(f"❌ Connection failed: {e}")
        print("Make sure the proxy server is running")
    except Exception as e:
        print(f"❌ Test failed: {e}")

async def test_cors(proxy_host: str, proxy_port: int):
    """Test CORS preflight request"""
    
    test_url = f"http://{proxy_host}:{proxy_port}/v1/chat/completions"
    
    print("\nTesting CORS preflight request...")
    print("-" * 50)
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test OPTIONS request (CORS preflight)
            headers = {
                'Origin': 'http://localhost:3000',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'content-type,authorization'
            }
            
            async with session.options(test_url, headers=headers) as response:
                print(f"CORS Status: {response.status}")
                cors_headers = {k: v for k, v in response.headers.items() 
                               if k.lower().startswith('access-control')}
                print(f"CORS Headers: {cors_headers}")
                
                if response.status == 200 and 'access-control-allow-origin' in response.headers:
                    print("✅ CORS is working correctly!")
                else:
                    print("⚠️  CORS might not be configured properly")
                
    except Exception as e:
        print(f"❌ CORS test failed: {e}")

def main():
    parser = argparse.ArgumentParser(description='Test OpenAI Proxy Server')
    parser.add_argument('--host', type=str, default='localhost',
                       help='Proxy server host (default: localhost)')
    parser.add_argument('--port', type=int, default=8080,
                       help='Proxy server port (default: 8080)')
    
    args = parser.parse_args()
    
    print("OpenAI Proxy Server Test")
    print("=" * 50)
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Run tests
        loop.run_until_complete(test_proxy(args.host, args.port))
        loop.run_until_complete(test_cors(args.host, args.port))
        
        print("\n" + "=" * 50)
        print("Test completed!")
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    finally:
        loop.close()

if __name__ == '__main__':
    main()
