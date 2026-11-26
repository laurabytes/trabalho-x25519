#!/usr/bin/env python3
"""benchmark local de x25519 e ml-kem-768."""
import argparse
import json
import platform
try:
    import resource
except ImportError:
    resource = None
import shutil
import statistics
import subprocess
import tempfile
import time
from pathlib import Path


def median_ms(values):
    return round(statistics.median(values), 6)


def run(command):
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError((result.stderr or result.stdout).strip())
    return result


def benchmark_x25519(repetitions):
    from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
    from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

    keygen_times, exchange_times = [], []
    for _ in range(repetitions):
        start = time.perf_counter_ns()
        alice = X25519PrivateKey.generate()
        bob = X25519PrivateKey.generate()
        keygen_times.append((time.perf_counter_ns() - start) / 1e6)

        alice_public = alice.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
        bob_public = bob.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
        start = time.perf_counter_ns()
        secret_a = alice.exchange(bob.public_key())
        secret_b = bob.exchange(alice.public_key())
        exchange_times.append((time.perf_counter_ns() - start) / 1e6)
        if secret_a != secret_b:
            raise RuntimeError("X25519 derivou segredos diferentes.")

    return {
        "available": True,
        "implementation": "Python cryptography",
        "repetitions": repetitions,
        "public_key_bytes": len(alice_public),
        "private_key_raw_bytes": 32,
        "shared_secret_bytes": len(secret_a),
        "keygen_pair_ms_median": median_ms(keygen_times),
        "two_exchanges_ms_median": median_ms(exchange_times),
        "raw_measurements_ms": {
            "keygen_pair": [round(value, 6) for value in keygen_times],
            "two_exchanges": [round(value, 6) for value in exchange_times],
        },
    }


def benchmark_ml_kem(repetitions, openssl):
    keygen_times, encaps_times, decaps_times = [], [], []
    sizes = {}
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        for index in range(repetitions):
            private_key = root / f"private_{index}.pem"
            public_key = root / f"public_{index}.pem"
            ciphertext = root / f"ciphertext_{index}.bin"
            secret_enc = root / f"secret_enc_{index}.bin"
            secret_dec = root / f"secret_dec_{index}.bin"

            start = time.perf_counter_ns()
            run([openssl, "genpkey", "-algorithm", "ML-KEM-768", "-out", str(private_key)])
            run([openssl, "pkey", "-in", str(private_key), "-pubout", "-out", str(public_key)])
            keygen_times.append((time.perf_counter_ns() - start) / 1e6)

            start = time.perf_counter_ns()
            run([openssl, "pkeyutl", "-encap", "-pubin", "-inkey", str(public_key),
                 "-out", str(ciphertext), "-secret", str(secret_enc)])
            encaps_times.append((time.perf_counter_ns() - start) / 1e6)

            start = time.perf_counter_ns()
            run([openssl, "pkeyutl", "-decap", "-inkey", str(private_key),
                 "-in", str(ciphertext), "-secret", str(secret_dec)])
            decaps_times.append((time.perf_counter_ns() - start) / 1e6)

            if secret_enc.read_bytes() != secret_dec.read_bytes():
                raise RuntimeError("ML-KEM-768 derivou segredos diferentes.")
            sizes = {
                "public_key_bytes": public_key.stat().st_size,
                "private_key_pem_bytes": private_key.stat().st_size,
                "ciphertext_bytes": ciphertext.stat().st_size,
                "shared_secret_bytes": secret_enc.stat().st_size,
            }

    return {
        "available": True,
        "implementation": "OpenSSL CLI",
        "repetitions": repetitions,
        **sizes,
        "keygen_ms_median": median_ms(keygen_times),
        "encaps_ms_median": median_ms(encaps_times),
        "decaps_ms_median": median_ms(decaps_times),
        "secret_match": True,
        "note": "KeyGen inclui geração e exportação da chave pública; tempos incluem overhead do processo CLI.",
        "raw_measurements_ms": {
            "keygen": [round(value, 6) for value in keygen_times],
            "encaps": [round(value, 6) for value in encaps_times],
            "decaps": [round(value, 6) for value in decaps_times],
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Compara X25519 e ML-KEM-768.")
    parser.add_argument("--repetitions", type=int, default=30)
    parser.add_argument("--output", default="data/benchmark_pqc.json")
    args = parser.parse_args()
    if args.repetitions < 1:
        parser.error("--repetitions deve ser positivo.")

    openssl = shutil.which("openssl")
    result = {
        "platform": platform.platform(),
        "python": platform.python_version(),
        "openssl": None,
        "repetitions": args.repetitions,
    }
    if openssl:
        version = run([openssl, "version"]).stdout.strip()
        result["openssl"] = version
    try:
        result["x25519"] = benchmark_x25519(args.repetitions)
    except Exception as error:
        result["x25519"] = {"available": False, "reason": str(error)}
    try:
        if not openssl:
            raise RuntimeError("Executável openssl não encontrado.")
        result["ml_kem_768"] = benchmark_ml_kem(args.repetitions, openssl)
    except Exception as error:
        result["ml_kem_768"] = {"available": False, "reason": str(error)}

    if resource is None:
        result["resource_usage"] = {
            "available": False,
            "note": "Métricas de CPU e RSS indisponíveis nesta plataforma.",
        }
    else:
        own_usage = resource.getrusage(resource.RUSAGE_SELF)
        child_usage = resource.getrusage(resource.RUSAGE_CHILDREN)
        result["resource_usage"] = {
            "available": True,
            "scope": "aggregate benchmark process and OpenSSL child processes",
            "process_cpu_user_seconds": round(own_usage.ru_utime, 6),
            "process_cpu_system_seconds": round(own_usage.ru_stime, 6),
            "process_peak_rss": own_usage.ru_maxrss,
            "children_cpu_user_seconds": round(child_usage.ru_utime, 6),
            "children_cpu_system_seconds": round(child_usage.ru_stime, 6),
            "children_peak_rss": child_usage.ru_maxrss,
            "rss_unit": "bytes" if platform.system() == "Darwin" else "KiB",
            "note": "RSS é pico agregado, não medição por operação.",
        }

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    try:
        import qiskit
        import qiskit_aer
        qiskit_versions = f"Qiskit: {qiskit.__version__}\nQiskit Aer: {qiskit_aer.__version__}"
    except Exception:
        qiskit_versions = "Qiskit: indisponível"
    x = result.get("x25519", {})
    ml = result.get("ml_kem_768", {})
    resource_data = result.get("resource_usage", {})
    environment_lines = [
        "Ambiente de benchmark reproduzido automaticamente",
        f"Python: {result['python']}",
        f"Plataforma: {result['platform']}",
        f"OpenSSL: {result['openssl']}",
        qiskit_versions,
        f"Repetições: {args.repetitions}",
        f"X25519 KeyGen par (mediana ms): {x.get('keygen_pair_ms_median')}",
        f"X25519 duas operações exchange (mediana ms): {x.get('two_exchanges_ms_median')}",
        f"ML-KEM-768 KeyGen + exportação (mediana ms): {ml.get('keygen_ms_median')}",
        f"ML-KEM-768 Encaps (mediana ms): {ml.get('encaps_ms_median')}",
        f"ML-KEM-768 Decaps (mediana ms): {ml.get('decaps_ms_median')}",
    ]
    if resource_data.get("available"):
        environment_lines.extend([
            f"CPU user do processo (s): {resource_data['process_cpu_user_seconds']}",
            f"CPU system do processo (s): {resource_data['process_cpu_system_seconds']}",
            f"Pico RSS do processo: {resource_data['process_peak_rss']} {resource_data['rss_unit']}",
            f"CPU user dos subprocessos (s): {resource_data['children_cpu_user_seconds']}",
            f"CPU system dos subprocessos (s): {resource_data['children_cpu_system_seconds']}",
            f"Pico RSS dos subprocessos: {resource_data['children_peak_rss']} {resource_data['rss_unit']}",
        ])
    else:
        environment_lines.append(resource_data.get("note", "Métricas de recursos indisponíveis."))
    environment_lines.extend([
        "Segredos compartilhados coincidiram nas execuções disponíveis.",
        "Tempos incluem overhead de interfaces diferentes e não são comparação intrínseca das primitivas.",
        "RSS é pico agregado, não medição por operação; energia não foi medida.",
    ])
    Path("data/environment.txt").write_text("\n".join(environment_lines) + "\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
