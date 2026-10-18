# Servidor local SEM cache que serve a pasta web/ (e, no futuro, a API em /api/...).
# Uso, a partir da raiz do projeto:  py servidor/servir.py  (Windows)  |  python3 servidor/servir.py
# Depois abra http://localhost:8000
# (Com "python -m http.server" o navegador pode reaproveitar módulos JS antigos e quebrar o mapa.)
import pathlib
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

WEB = pathlib.Path(__file__).resolve().parent.parent / 'web'


class SemCache(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def log_message(self, fmt, *args):
        # esconde pedidos automáticos do DevTools do navegador (inofensivos, mas poluem o log)
        if '.well-known' in self.path or self.path.endswith('.map'):
            return
        super().log_message(fmt, *args)


if __name__ == '__main__':
    if not WEB.is_dir():
        sys.exit(f'Pasta do site não encontrada: {WEB}')
    servidor = ThreadingHTTPServer(('127.0.0.1', 8000), partial(SemCache, directory=str(WEB)))
    print('Abra http://localhost:8000  (Ctrl+C para encerrar)')
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print('\nServidor encerrado.')
    finally:
        servidor.server_close()
