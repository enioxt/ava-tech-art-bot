import os
import sys
import logging
import asyncio
import json
from datetime import datetime
from pathlib import Path
from telegram import Bot

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'logs/connection_test_{datetime.now().strftime("%Y%m%d")}.log')
    ]
)
logger = logging.getLogger(__name__)

class ConnectionTester:
    def __init__(self):
        self.config = self._load_config()
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.test_results = []
        
    def _load_config(self) -> dict:
        """Carrega configuração do monitor."""
        config_path = Path(__file__).parent.parent / 'config' / 'monitor_config.json'
        try:
            with open(config_path) as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar configuração: {str(e)}")
            return {}
            
    async def test_connection(self) -> bool:
        """Testa a conexão com a API do Telegram."""
        try:
            start_time = datetime.now()
            bot = Bot(self.token)
            me = await bot.get_me()
            end_time = datetime.now()
            
            response_time = (end_time - start_time).total_seconds() * 1000
            
            result = {
                'timestamp': start_time.isoformat(),
                'success': True,
                'response_time_ms': response_time,
                'bot_info': {
                    'id': me.id,
                    'username': me.username,
                    'first_name': me.first_name
                }
            }
            
            logger.info(
                f"Conexão OK - Bot: @{me.username} "
                f"(Tempo de resposta: {response_time:.2f}ms)"
            )
            
        except Exception as e:
            result = {
                'timestamp': datetime.now().isoformat(),
                'success': False,
                'error': str(e)
            }
            logger.error(f"Erro de conexão: {str(e)}")
            
        self.test_results.append(result)
        return result['success']
        
    def save_results(self):
        """Salva resultados dos testes."""
        output_file = f'logs/connection_results_{datetime.now().strftime("%Y%m%d")}.json'
        try:
            with open(output_file, 'w') as f:
                json.dump(self.test_results, f, indent=2)
            logger.info(f"Resultados salvos em {output_file}")
        except Exception as e:
            logger.error(f"Erro ao salvar resultados: {str(e)}")
            
    async def run_tests(self, duration: int = 3600):
        """Executa testes por um período determinado."""
        logger.info(f"Iniciando testes de conexão (duração: {duration}s)")
        
        start_time = datetime.now()
        interval = self.config.get('connection', {}).get('check_interval', 60)
        
        try:
            while (datetime.now() - start_time).total_seconds() < duration:
                await self.test_connection()
                await asyncio.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("Testes interrompidos pelo usuário")
            
        except Exception as e:
            logger.error(f"Erro durante os testes: {str(e)}")
            
        finally:
            self.save_results()
            self._print_summary()
            
    def _print_summary(self):
        """Imprime resumo dos testes."""
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r['success'])
        
        if total_tests > 0:
            success_rate = (successful_tests / total_tests) * 100
            avg_response_time = sum(
                r.get('response_time_ms', 0) 
                for r in self.test_results 
                if r['success']
            ) / successful_tests if successful_tests > 0 else 0
            
            print("\n" + "="*50)
            print("RESUMO DOS TESTES")
            print("="*50)
            print(f"Total de testes: {total_tests}")
            print(f"Testes com sucesso: {successful_tests}")
            print(f"Taxa de sucesso: {success_rate:.2f}%")
            print(f"Tempo médio de resposta: {avg_response_time:.2f}ms")
            print("="*50)

async def main():
    tester = ConnectionTester()
    await tester.run_tests()

if __name__ == "__main__":
    asyncio.run(main()) 