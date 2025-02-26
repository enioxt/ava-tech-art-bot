"""
CORE Web Server
Provides web interface for the CORE system
"""

import os
import json
import logging
from typing import Dict, Optional
from decimal import Decimal
from datetime import datetime
from pathlib import Path

from aiohttp import web
from aiohttp_session import setup, get_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from cryptography import fernet

logger = logging.getLogger(__name__)

class CoreWebServer:
    """Web server for CORE system"""
    
    def __init__(self, core_system):
        self.core = core_system
        self.app = web.Application()
        self.setup_routes()
        self.setup_session()
        
    def setup_routes(self):
        """Setup server routes"""
        self.app.router.add_get('/', self.handle_home)
        self.app.router.add_get('/stats', self.handle_stats)
        self.app.router.add_get('/leaderboard', self.handle_leaderboard)
        self.app.router.add_post('/action', self.handle_action)
        self.app.router.add_post('/purchase', self.handle_purchase)
        self.app.router.add_get('/user/{user_id}', self.handle_user)
        
        # Serve static files
        static_path = Path(__file__).parent / 'static'
        self.app.router.add_static('/static', static_path)
        
    def setup_session(self):
        """Setup session handling"""
        fernet_key = fernet.Fernet.generate_key()
        secret_key = base64.urlsafe_b64decode(fernet_key)
        setup(self.app, EncryptedCookieStorage(secret_key))
        
    async def handle_home(self, request: web.Request) -> web.Response:
        """Handle home page request"""
        try:
            session = await get_session(request)
            user_id = session.get('user_id')
            
            template = self.load_template('home.html')
            status = await self.core.get_system_status()
            
            user_stats = None
            if user_id:
                user_stats = await self.core.ethik_integration.get_user_stats(user_id)
                
            return web.Response(
                text=template.render(
                    status=status,
                    user_stats=user_stats
                ),
                content_type='text/html'
            )
            
        except Exception as e:
            logger.error(f"Error handling home request: {e}")
            return web.Response(
                text="Error loading home page",
                status=500
            )
            
    async def handle_stats(self, request: web.Request) -> web.Response:
        """Handle stats page request"""
        try:
            status = await self.core.get_system_status()
            return web.json_response(status)
            
        except Exception as e:
            logger.error(f"Error handling stats request: {e}")
            return web.Response(
                text=json.dumps({"error": str(e)}),
                status=500,
                content_type='application/json'
            )
            
    async def handle_leaderboard(self, request: web.Request) -> web.Response:
        """Handle leaderboard request"""
        try:
            limit = int(request.query.get('limit', 10))
            leaderboard = await self.core.ethik_integration.get_leaderboard(limit)
            return web.json_response(leaderboard)
            
        except Exception as e:
            logger.error(f"Error handling leaderboard request: {e}")
            return web.Response(
                text=json.dumps({"error": str(e)}),
                status=500,
                content_type='application/json'
            )
            
    async def handle_action(self, request: web.Request) -> web.Response:
        """Handle ethical action submission"""
        try:
            session = await get_session(request)
            user_id = session.get('user_id')
            
            if not user_id:
                return web.Response(
                    text=json.dumps({"error": "User not authenticated"}),
                    status=401,
                    content_type='application/json'
                )
                
            data = await request.json()
            action_type = data.get('action_type')
            action_data = data.get('action_data', {})
            
            if not action_type:
                return web.Response(
                    text=json.dumps({"error": "Missing action_type"}),
                    status=400,
                    content_type='application/json'
                )
                
            result = await self.core.process_action(
                user_id=user_id,
                action_type=action_type,
                action_data=action_data
            )
            
            return web.json_response(result)
            
        except Exception as e:
            logger.error(f"Error handling action request: {e}")
            return web.Response(
                text=json.dumps({"error": str(e)}),
                status=500,
                content_type='application/json'
            )
            
    async def handle_purchase(self, request: web.Request) -> web.Response:
        """Handle token purchase request"""
        try:
            session = await get_session(request)
            user_id = session.get('user_id')
            
            if not user_id:
                return web.Response(
                    text=json.dumps({"error": "User not authenticated"}),
                    status=401,
                    content_type='application/json'
                )
                
            data = await request.json()
            pix_amount = Decimal(str(data.get('amount')))
            pix_id = data.get('pix_id')
            
            if not pix_amount or not pix_id:
                return web.Response(
                    text=json.dumps({"error": "Missing amount or pix_id"}),
                    status=400,
                    content_type='application/json'
                )
                
            tx = await self.core.token.process_pix_purchase(
                user_id=user_id,
                pix_amount=pix_amount,
                pix_id=pix_id
            )
            
            if tx:
                return web.json_response({
                    "success": True,
                    "transaction": {
                        "amount": str(tx.amount),
                        "tx_hash": tx.tx_hash,
                        "timestamp": tx.timestamp.isoformat()
                    }
                })
            else:
                return web.Response(
                    text=json.dumps({"error": "Purchase failed"}),
                    status=400,
                    content_type='application/json'
                )
                
        except Exception as e:
            logger.error(f"Error handling purchase request: {e}")
            return web.Response(
                text=json.dumps({"error": str(e)}),
                status=500,
                content_type='application/json'
            )
            
    async def handle_user(self, request: web.Request) -> web.Response:
        """Handle user profile request"""
        try:
            user_id = request.match_info['user_id']
            stats = await self.core.ethik_integration.get_user_stats(user_id)
            return web.json_response(stats)
            
        except Exception as e:
            logger.error(f"Error handling user request: {e}")
            return web.Response(
                text=json.dumps({"error": str(e)}),
                status=500,
                content_type='application/json'
            )
            
    def load_template(self, template_name: str) -> str:
        """Load HTML template"""
        template_path = Path(__file__).parent / 'templates' / template_name
        with open(template_path) as f:
            return f.read()

async def run_server(core_system, host: str = '0.0.0.0', port: int = 5000):
    """Run the CORE web server"""
    server = CoreWebServer(core_system)
    
    # Setup middleware
    server.app.middlewares.append(error_middleware)
    
    # Start server
    runner = web.AppRunner(server.app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    
    logger.info(f"Starting CORE web server at http://{host}:{port}")
    await site.start()
    
@web.middleware
async def error_middleware(request: web.Request, handler) -> web.Response:
    """Global error handling middleware"""
    try:
        return await handler(request)
    except web.HTTPException as ex:
        return web.Response(
            text=json.dumps({"error": str(ex)}),
            status=ex.status,
            content_type='application/json'
        )
    except Exception as e:
        logger.error(f"Unhandled error: {e}")
        return web.Response(
            text=json.dumps({"error": "Internal server error"}),
            status=500,
            content_type='application/json'
        ) 