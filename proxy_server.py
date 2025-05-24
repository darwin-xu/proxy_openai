#!/usr/bin/env python3
"""
OpenAI API Proxy Server

This server acts as a proxy between your local development environment
and the OpenAI API. It forwards all requests to api.openai.com while
preserving headers, method, and body content.

Usage:
    python proxy_server.py [--port PORT] [--host HOST]

Environment Variables:
    PROXY_PORT: Port to run the proxy server on (default: 8080)
    PROXY_HOST: Host to bind the server to (default: 0.0.0.0)
"""

import asyncio
import aiohttp
import argparse
import logging
import os
import sys
from aiohttp import web, ClientSession
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('proxy.log')
    ]
)
logger = logging.getLogger(__name__)

# OpenAI API base URL
OPENAI_API_BASE = "https://api.openai.com"

class OpenAIProxy:
    def __init__(self):
        self.session: Optional[ClientSession] = None
    
    async def create_session(self):
        """Create aiohttp client session with proper configuration"""
        timeout = aiohttp.ClientTimeout(total=300, connect=30)
        connector = aiohttp.TCPConnector(
            limit=100,
            limit_per_host=30,
            keepalive_timeout=30,
            enable_cleanup_closed=True
        )
        self.session = ClientSession(
            timeout=timeout,
            connector=connector,
            headers={'User-Agent': 'OpenAI-Proxy/1.0'}
        )
    
    async def close_session(self):
        """Clean up the client session"""
        if self.session:
            await self.session.close()
    
    async def proxy_request(self, request: web.Request) -> web.Response:
        """
        Proxy the incoming request to OpenAI API
        """
        try:
            # Construct the target URL
            path = request.path_qs
            target_url = f"{OPENAI_API_BASE}{path}"
            
            # Prepare headers (exclude hop-by-hop headers)
            headers = dict(request.headers)
            
            # Remove hop-by-hop headers that shouldn't be forwarded
            hop_by_hop_headers = {
                'connection', 'keep-alive', 'proxy-authenticate',
                'proxy-authorization', 'te', 'trailers', 'transfer-encoding',
                'upgrade', 'host'
            }
            headers = {k: v for k, v in headers.items() 
                      if k.lower() not in hop_by_hop_headers}
            
            # Read request body
            body = None
            if request.can_read_body:
                body = await request.read()
            
            logger.info(f"Proxying {request.method} {target_url}")
            logger.debug(f"Headers: {dict(headers)}")
            
            # Make the request to OpenAI
            async with self.session.request(
                method=request.method,
                url=target_url,
                headers=headers,
                data=body,
                allow_redirects=False
            ) as response:
                
                # Prepare response headers
                resp_headers = dict(response.headers)
                
                # Remove hop-by-hop headers from response
                resp_headers = {k: v for k, v in resp_headers.items() 
                               if k.lower() not in hop_by_hop_headers}
                
                # Add CORS headers for browser compatibility
                resp_headers['Access-Control-Allow-Origin'] = '*'
                resp_headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
                resp_headers['Access-Control-Allow-Headers'] = '*'
                
                # Read response body
                response_body = await response.read()
                
                logger.info(f"Response: {response.status} for {request.method} {target_url}")
                
                # Create and return the response
                return web.Response(
                    body=response_body,
                    status=response.status,
                    headers=resp_headers
                )
                
        except aiohttp.ClientError as e:
            logger.error(f"Client error proxying request: {e}")
            return web.Response(
                text=f"Proxy error: {str(e)}",
                status=502,
                headers={'Access-Control-Allow-Origin': '*'}
            )
        except Exception as e:
            logger.error(f"Unexpected error proxying request: {e}")
            return web.Response(
                text=f"Internal proxy error: {str(e)}",
                status=500,
                headers={'Access-Control-Allow-Origin': '*'}
            )
    
    async def handle_options(self, request: web.Request) -> web.Response:
        """Handle CORS preflight requests"""
        return web.Response(
            headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': '*',
                'Access-Control-Max-Age': '86400'
            }
        )

async def create_app() -> web.Application:
    """Create and configure the web application"""
    proxy = OpenAIProxy()
    await proxy.create_session()
    
    app = web.Application()
    
    # Add routes
    app.router.add_route('OPTIONS', '/{path:.*}', proxy.handle_options)
    app.router.add_route('*', '/{path:.*}', proxy.proxy_request)
    
    # Cleanup function
    async def cleanup_session(app):
        await proxy.close_session()
    
    app.on_cleanup.append(cleanup_session)
    
    return app

async def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(description='OpenAI API Proxy Server')
    parser.add_argument('--port', type=int, 
                       default=int(os.getenv('PROXY_PORT', 8080)),
                       help='Port to run the server on (default: 8080)')
    parser.add_argument('--host', type=str,
                       default=os.getenv('PROXY_HOST', '0.0.0.0'),
                       help='Host to bind the server to (default: 0.0.0.0)')
    
    args = parser.parse_args()
    
    app = await create_app()
    
    logger.info(f"Starting OpenAI proxy server on {args.host}:{args.port}")
    logger.info(f"Proxying requests to {OPENAI_API_BASE}")
    
    try:
        # Run the server
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, args.host, args.port)
        await site.start()
        
        logger.info("Proxy server started successfully")
        logger.info("Press Ctrl+C to stop the server")
        
        # Keep the server running
        while True:
            await asyncio.sleep(3600)
            
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        await runner.cleanup()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Failed to start server: {e}")
        sys.exit(1)
