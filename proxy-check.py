import socket
import socks
import threading
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

class SOCKS5Checker:
    def __init__(self, timeout=5, max_workers=10):
        self.timeout = timeout
        self.max_workers = max_workers
        self.results = []
        self.lock = threading.Lock()

    def check_proxy(self, proxy_str):
        """Verifica um proxy SOCKS5 individual"""
        try:
            parts = proxy_str.strip().split(':')
            if len(parts) < 2:
                return {
                    'proxy': proxy_str,
                    'status': 'ERRO',
                    'tempo': 0,
                    'msg': 'Formato inválido (use host:porta)'
                }

            host = parts[0]
            try:
                port = int(parts[1])
            except ValueError:
                return {
                    'proxy': proxy_str,
                    'status': 'ERRO',
                    'tempo': 0,
                    'msg': 'Porta deve ser um número'
                }

            # Testa conexão SOCKS5
            inicio = time.time()
            
            sock = socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
            sock.set_proxy(socks.SOCKS5, host, port)
            sock.settimeout(self.timeout)

            # Tenta conectar a um servidor público (Google DNS)
            sock.connect(('8.8.8.8', 53))
            sock.close()

            tempo = (time.time() - inicio) * 1000

            return {
                'proxy': proxy_str,
                'status': 'OK',
                'tempo': tempo,
                'msg': f'Conectado com sucesso'
            }

        except socks.ProxyConnectionError as e:
            return {
                'proxy': proxy_str,
                'status': 'FALHA',
                'tempo': 0,
                'msg': f'Erro de conexão: {str(e)[:50]}'
            }
        except socket.timeout:
            return {
                'proxy': proxy_str,
                'status': 'TIMEOUT',
                'tempo': self.timeout * 1000,
                'msg': 'Timeout na conexão'
            }
        except Exception as e:
            return {
                'proxy': proxy_str,
                'status': 'FALHA',
                'tempo': 0,
                'msg': f'{type(e).__name__}: {str(e)[:40]}'
            }

    def check_proxies(self, proxies_list):
        """Verifica múltiplos proxies em paralelo"""
        self.results = []
        
        print(f"\n{'='*70}")
        print(f"{'SOCKS5 PROXY CHECKER':^70}")
        print(f"{'='*70}\n")
        print(f"Total de proxies para verificar: {len(proxies_list)}")
        print(f"Workers paralelos: {self.max_workers}")
        print(f"Timeout: {self.timeout}s\n")
        print(f"{'PROXY':<25} {'STATUS':<10} {'TEMPO':<12} {'MENSAGEM':<30}")
        print(f"{'-'*70}")

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self.check_proxy, proxy): proxy 
                for proxy in proxies_list
            }

            completed = 0
            for future in as_completed(futures):
                result = future.result()
                with self.lock:
                    self.results.append(result)
                    completed += 1

                # Exibe resultado
                tempo_str = f"{result['tempo']:.0f}ms" if result['tempo'] > 0 else "-"
                msg_truncado = result['msg'][:28]
                
                # Cores para terminal
                status = result['status']
                if status == 'OK':
                    cor = '\033[92m'  # Verde
                elif status == 'TIMEOUT':
                    cor = '\033[93m'  # Amarelo
                else:
                    cor = '\033[91m'  # Vermelho
                reset = '\033[0m'

                print(f"{result['proxy']:<25} {cor}{status:<10}{reset} {tempo_str:<12} {msg_truncado:<30}")

                # Barra de progresso
                progresso = (completed / len(proxies_list)) * 100
                if completed % max(1, len(proxies_list) // 10) == 0 or completed == len(proxies_list):
                    print(f"Progresso: {progresso:.0f}% ({completed}/{len(proxies_list)})")

        self.exibir_resumo()

    def exibir_resumo(self):
        """Exibe resumo das verificações"""
        total = len(self.results)
        ok = sum(1 for r in self.results if r['status'] == 'OK')
        timeout = sum(1 for r in self.results if r['status'] == 'TIMEOUT')
        falha = sum(1 for r in self.results if r['status'] == 'FALHA')
        erro = sum(1 for r in self.results if r['status'] == 'ERRO')

        tempo_medio = sum(r['tempo'] for r in self.results if r['tempo'] > 0)
        tempo_medio = tempo_medio / ok if ok > 0 else 0

        print(f"\n{'='*70}")
        print(f"{'RESUMO':<35} {'TOTAL':<35}")
        print(f"{'-'*70}")
        print(f"{'Total verificados:':<35} {total}")
        print(f"\033[92m{'✓ Funcionando:':<35} {ok} ({ok/total*100:.1f}%)\033[0m")
        print(f"\033[93m{'⏱ Timeout:':<35} {timeout} ({timeout/total*100:.1f}%)\033[0m")
        print(f"\033[91m{'✗ Falhando:':<35} {falha} ({falha/total*100:.1f}%)\033[0m")
        print(f"{'⚠ Erro de formato:':<35} {erro}")
        print(f"Tempo médio de resposta: {tempo_medio:.2f}ms")
        print(f"{'='*70}\n")

    def salvar_resultados(self, filename='resultados_proxies.txt'):
        """Salva resultados em arquivo"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Verificação de SOCKS5 Proxies - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*70}\n\n")
            
            # Proxies OK
            ok_proxies = [r['proxy'] for r in self.results if r['status'] == 'OK']
            if ok_proxies:
                f.write("PROXIES FUNCIONANDO:\n")
                for proxy in ok_proxies:
                    f.write(f"  {proxy}\n")
                f.write("\n")

            # Todos os resultados
            f.write("RELATÓRIO COMPLETO:\n")
            f.write(f"{'PROXY':<25} {'STATUS':<10} {'TEMPO':<12} {'MENSAGEM':<30}\n")
            f.write(f"{'-'*70}\n")
            for result in self.results:
                tempo_str = f"{result['tempo']:.0f}ms" if result['tempo'] > 0 else "-"
                f.write(f"{result['proxy']:<25} {result['status']:<10} {tempo_str:<12} {result['msg']:<30}\n")

        print(f"Resultados salvos em: {filename}")


def carregar_proxies_de_arquivo(filename):
    """Carrega proxies de um arquivo"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            proxies = [linha.strip() for linha in f if linha.strip()]
        return proxies
    except FileNotFoundError:
        print(f"Arquivo '{filename}' não encontrado!")
        return None
    except Exception as e:
        print(f"Erro ao ler arquivo: {e}")
        return None


def main():
    print("\n╔══════════════════════════════════════╗")
    print("║   SOCKS5 PROXY CHECKER - PYTHON     ║")
    print("╚══════════════════════════════════════╝\n")

    # Escolher origem dos proxies
    print("Escolha a origem dos proxies:")
    print("1. Digitar manualmente")
    print("2. Carregar de arquivo\n")

    opcao = input("Opção (1 ou 2): ").strip()

    proxies = []

    if opcao == "2":
        # Carregar de arquivo
        filename = input("Digite o caminho do arquivo (ex: proxies.txt): ").strip()
        proxies = carregar_proxies_de_arquivo(filename)
        if not proxies:
            return
    else:
        # Entrada manual
        print("\nDigite os proxies (um por linha, formato: host:porta)")
        print("Deixe em branco e pressione Enter 2x para finalizar:\n")

        linhas_vazias = 0

        while True:
            linha = input().strip()
            if not linha:
                linhas_vazias += 1
                if linhas_vazias >= 2:
                    break
            else:
                linhas_vazias = 0
                proxies.append(linha)

    if not proxies:
        print("Nenhum proxy foi adicionado!")
        return

    # Configurações
    timeout = 5
    max_workers = 10

    try:
        max_workers = int(input(f"\nQuantidade de workers paralelos (padrão {max_workers}): ") or max_workers)
    except ValueError:
        pass

    # Executa verificação
    checker = SOCKS5Checker(timeout=timeout, max_workers=max_workers)
    checker.check_proxies(proxies)

    # Opção de salvar
    salvar = input("\nSalvar resultados em arquivo? (s/n): ").lower()
    if salvar == 's':
        checker.salvar_resultados()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nVerificação cancelada pelo usuário.")
    except Exception as e:
        print(f"\nErro: {e}")
        print("Certifique-se de instalar: pip install pysocks")