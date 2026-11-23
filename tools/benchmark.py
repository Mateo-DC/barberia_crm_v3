"""Benchmark para Windows: compara intérprete y Nuitka standalone de forma reproducible.

Mide tamaño de distribución, tiempo hasta respuesta HTTP, memoria RSS del árbol
(generalmente 1 proceso) y latencia de endpoints locales. No mide carga LAN real.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from urllib.request import urlopen


def directory_bytes(path: Path) -> int:
    if path.is_file():
        return path.stat().st_size
    return sum(f.stat().st_size for f in path.rglob('*') if f.is_file())


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        return int(sock.getsockname()[1])


def fetch(url: str, timeout: float = 1.0) -> bytes:
    with urlopen(url, timeout=timeout) as response:
        if response.status != 200:
            raise RuntimeError(f'HTTP {response.status}')
        return response.read()


def measure(command: list[str], cwd: Path, label: str, runs: int = 3, wait_s: float = 30) -> dict:
    try:
        import psutil
    except ImportError as exc:
        raise SystemExit('Instala psutil: python -m pip install psutil') from exc
    measurements = []
    for index in range(runs):
        port = free_port()
        with tempfile.TemporaryDirectory(prefix='crm_bench_') as test_data:
            env = os.environ.copy()
            env.update({'CRM_PORT': str(port), 'CRM_DATA_DIR': test_data,
                        'CRM_NO_BROWSER': '1', 'CRM_SEED_DEMO': '0'})
            started = time.perf_counter()
            creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            process = subprocess.Popen(command, cwd=cwd, env=env,
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                        creationflags=creation_flags)
            root = psutil.Process(process.pid)
            reachable = False
            try:
                while (time.perf_counter() - started) < wait_s:
                    if process.poll() is not None:
                        raise RuntimeError(f'{label}: proceso finalizó con código {process.returncode}')
                    try:
                        fetch(f'http://127.0.0.1:{port}/registro')
                        reachable = True
                        break
                    except Exception:
                        time.sleep(0.05)
                if not reachable:
                    raise RuntimeError(f'{label}: no respondió en {wait_s} segundos')
                elapsed_ms = (time.perf_counter() - started) * 1000
                # Medición post-arranque, con estado estable breve.
                time.sleep(0.20)
                samples = []
                for _ in range(5):
                    rss_total = 0
                    for p in [root, *root.children(recursive=True)]:
                        try:
                            rss_total += p.memory_info().rss
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                    samples.append(rss_total)
                    time.sleep(0.03)
                durations = []
                for _ in range(20):
                    req_start = time.perf_counter()
                    fetch(f'http://127.0.0.1:{port}/registro')
                    durations.append((time.perf_counter() - req_start) * 1000)
                measurements.append({'inicio_ms': round(elapsed_ms, 1),
                                     'rss_mb_aprox': round(max(samples, default=0) / 1048576, 2),
                                     'latencia_media_ms': round(sum(durations)/len(durations), 2)})
            finally:
                # Detener solo el servidor creado por este test; no tocar procesos ajenos.
                for child in root.children(recursive=True):
                    try: child.terminate()
                    except (psutil.NoSuchProcess, psutil.AccessDenied): pass
                try: root.terminate()
                except (psutil.NoSuchProcess, psutil.AccessDenied): pass
                try: root.wait(timeout=5)
                except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                    try: root.kill()
                    except (psutil.NoSuchProcess, psutil.AccessDenied): pass
    mean = lambda key: round(sum(x[key] for x in measurements)/len(measurements), 2)
    return {'muestras': measurements, 'inicio_promedio_ms': mean('inicio_ms'),
            'rss_promedio_mb_aprox': mean('rss_mb_aprox'),
            'latencia_promedio_ms': mean('latencia_media_ms')}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--exe', default='build/launcher.dist/BarberiaCRM.exe')
    parser.add_argument('--runs', type=int, default=3)
    parser.add_argument('--timeout', type=float, default=40)
    parser.add_argument('--build-duration-file', default='reports/build_duration_seconds.txt')
    args = parser.parse_args()
    if args.runs < 1 or args.runs > 20:
        parser.error('runs debe estar entre 1 y 20')
    root = Path(__file__).resolve().parent.parent
    exe = (root / args.exe).resolve()
    if not exe.is_file():
        parser.error(f'No existe el .exe: {exe}')
    dist = exe.parent
    reports = root / 'reports'
    reports.mkdir(exist_ok=True)
    try:
        build_duration = float((root / args.build_duration_file).read_text().strip())
    except (ValueError, FileNotFoundError):
        build_duration = None
    results = {
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'equipo': {'plataforma': sys.platform, 'python': sys.version.split()[0]},
        'compilacion_segundos': build_duration,
        'tamano_dist_mb': round(directory_bytes(dist) / 1048576, 2),
        'tamano_exe_mb': round(exe.stat().st_size / 1048576, 2),
        'configuracion': {'repeticiones': args.runs, 'endpoint': '/registro',
                           'datos': 'SQLite temporal nueva en cada medición', 'conexion': 'loopback'},
        'python': measure([sys.executable, 'launcher.py'], root, 'Python', args.runs, args.timeout),
        'nuitka_standalone': measure([str(exe)], dist, 'Nuitka', args.runs, args.timeout),
    }
    (reports/'benchmark.json').write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf8')
    rows = ['# Informe de rendimiento — Barbería CRM', '',
            f"Fecha UTC: {results['timestamp_utc']}", '',
            '| Métrica | Python | Nuitka standalone |', '|---|---:|---:|',
            f"| Inicio hasta HTTP (ms, media) | {results['python']['inicio_promedio_ms']} | {results['nuitka_standalone']['inicio_promedio_ms']} |",
            f"| RSS de proceso (MB, aproximado) | {results['python']['rss_promedio_mb_aprox']} | {results['nuitka_standalone']['rss_promedio_mb_aprox']} |",
            f"| Latencia local de registro GET (ms) | {results['python']['latencia_promedio_ms']} | {results['nuitka_standalone']['latencia_promedio_ms']} |",
            '', f"Tamaño total distribución standalone: **{results['tamano_dist_mb']} MB**.",
            f"Tamaño del archivo exe: **{results['tamano_exe_mb']} MB**.",
            f"Tiempo de compilación registrado: **{build_duration if build_duration is not None else 'no disponible'} s**.",
            '', '## Alcance y limitaciones',
            'Cada muestra inicia su propio SQLite temporal; no se modifican datos reales.',
            'Se mide el tiempo hasta la primera respuesta HTTP, memoria RSS aproximada y latencia de 20 peticiones locales.',
            'Los resultados dependen del equipo, antivirus, cachés y cargas; no son una garantía de producción.',
            'La medición de RSS refleja el máximo observado entre muestras del proceso y sus hijos, no un pico exhaustivo.',
            'No se incluye el consumo del navegador ni pruebas con múltiples dispositivos.', '']
    (reports/'benchmark.md').write_text('\n'.join(rows), encoding='utf8')
    print('\n'.join(rows[:10]))
    print('Reportes:', reports/'benchmark.md', 'y', reports/'benchmark.json')

if __name__ == '__main__':
    main()
