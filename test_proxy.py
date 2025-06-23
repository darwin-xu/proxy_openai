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
import os  # Added for OPENAI_API_KEY environment variable


async def test_proxy(proxy_host: str, proxy_port: int, api_key: str):
    """Test the proxy server with a POST request to /v1/chat/completions"""

    test_url = f"http://{proxy_host}:{proxy_port}/v1/chat/completions"

    print(f"Testing proxy at {proxy_host}:{proxy_port}")
    print(f"Target URL: {test_url} (POST)")
    print("-" * 50)

    if not api_key:
        print("⚠️  OPENAI_API_KEY not provided.")
        print("    Please provide it via the --api-key argument or by setting the OPENAI_API_KEY environment variable.")
        print("    Skipping chat completions test.")
        return

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": "gpt-4.1-nano",  # Using a generally available or smaller model for testing
        "messages": [
            {
                "role": "system",  # Standard role for system-level instructions
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": "Hello!"
            }
        ]
    }

    try:
        async with aiohttp.ClientSession() as session:
            print("Testing POST request to /v1/chat/completions...")
            async with session.post(test_url, headers=headers, json=payload) as response:
                print(f"Status: {response.status}")
                # Limit printing of all headers as it can be verbose
                print(f"Content-Type Header: {response.headers.get('Content-Type')}")

                response_text = await response.text()

                if response.status == 200:
                    try:
                        data = json.loads(response_text)
                        print("✅ Proxy is working correctly and API call was successful!")
                        # Print a snippet of the response, e.g., the first choice's message content
                        if data.get("choices") and len(data["choices"]) > 0:
                            first_choice = data["choices"][0]
                            if first_choice.get("message") and first_choice["message"].get("content"):
                                print(f"Assistant's reply: {first_choice['message']['content'][:100]}...")
                            else:
                                print(f"Response (full): {json.dumps(data, indent=2)}")
                        else:
                            print(f"Response (full): {json.dumps(data, indent=2)}")
                    except json.JSONDecodeError:
                        print("⚠️ Proxy returned 200 but response is not valid JSON.")
                        print(f"Response snippet: {response_text[:500]}...")
                elif response.status == 401:
                    print("❌ Proxy is working, but OpenAI API authentication failed (401).")
                    print("   Please check your OPENAI_API_KEY.")
                    print(f"Response snippet: {response_text[:500]}...")
                elif response.status == 429:
                    print("❌ Proxy is working, but OpenAI API rate limit exceeded (429).")
                    print("   You might need to wait or check your usage.")
                    print(f"Response snippet: {response_text[:500]}...")
                elif response.status == 404 and "model_not_found" in response_text:
                    print(f"❌ Proxy is working, but the model '{payload['model']}' was not found (404).")
                    print("   You might need to use a different model name (e.g., gpt-3.5-turbo).")
                    print(f"Response snippet: {response_text[:500]}...")
                else:
                    print(f"⚠️  Proxy returned status {response.status}")
                    print(f"Response snippet: {response_text[:500]}...")

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
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type,authorization",
            }

            async with session.options(test_url, headers=headers) as response:
                print(f"CORS Status: {response.status}")
                cors_headers = {
                    k: v
                    for k, v in response.headers.items()
                    if k.lower().startswith("access-control")
                }
                print(f"CORS Headers: {cors_headers}")

                if (
                    response.status == 200
                    and "access-control-allow-origin" in response.headers
                ):
                    print("✅ CORS is working correctly!")
                else:
                    print("⚠️  CORS might not be configured properly")

    except Exception as e:
        print(f"❌ CORS test failed: {e}")


async def test_ip_restriction(proxy_host: str, proxy_port: int):
    """Test the IP restriction functionality"""
    
    test_url = f"http://{proxy_host}:{proxy_port}/v1/models"
    
    print(f"Testing IP restriction at {proxy_host}:{proxy_port}")
    print(f"Target URL: {test_url} (GET)")
    print("-" * 50)
    
    # Test with custom headers to simulate different client IPs
    test_headers = [
        {"X-Forwarded-For": "192.168.1.100"},
        {"X-Forwarded-For": "10.0.0.50"},
        {"X-Real-IP": "172.16.0.10"},
        {}  # No custom headers (will use actual client IP)
    ]
    
    async with aiohttp.ClientSession() as session:
        for i, headers in enumerate(test_headers):
            print(f"\nTest {i+1}: Headers: {headers if headers else 'None (using actual client IP)'}")
            
            try:
                async with session.get(test_url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    status = response.status
                    response_text = await response.text()
                    
                    if status == 403:
                        print(f"✅ Access correctly denied (403): {response_text[:100]}")
                    elif status == 401:
                        print(f"✅ Reached OpenAI API (401 - need API key): {response_text[:100]}")
                    elif status == 200:
                        print(f"✅ Request successful (200)")
                    else:
                        print(f"⚠️  Unexpected status {status}: {response_text[:100]}")
                        
            except asyncio.TimeoutError:
                print("❌ Request timed out")
            except Exception as e:
                print(f"❌ Request failed: {e}")

    print("\n" + "=" * 50)
    print("IP restriction test completed")
    print("=" * 50)


def main():
    parser = argparse.ArgumentParser(description="Test OpenAI Proxy Server")
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="Proxy server host (default: localhost)",
    )
    parser.add_argument(
        "--port", type=int, default=8080, help="Proxy server port (default: 8080)"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=os.getenv("OPENAI_API_KEY"),
        help="OpenAI API key. Can also be set via OPENAI_API_KEY environment variable."
    )

    args = parser.parse_args()

    print("OpenAI Proxy Server Test")
    print("=" * 50)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        # Run tests
        loop.run_until_complete(test_proxy(args.host, args.port, args.api_key))
        loop.run_until_complete(test_cors(args.host, args.port))
        loop.run_until_complete(test_ip_restriction(args.host, args.port))

        print("\n" + "=" * 50)
        print("Test completed!")

    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    finally:
        loop.close()


if __name__ == "__main__":
    main()
