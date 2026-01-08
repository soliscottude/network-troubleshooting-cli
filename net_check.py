import argparse
import logging
import socket
import time
import urllib.request
import urllib.error


# ---- logging: terminal + app.log ----
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

file_handler = logging.FileHandler("app.log", encoding="utf-8")
file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logger.addHandler(file_handler)


def dns_lookup(host):
    start = time.time()
    try:
        ip = socket.gethostbyname(host)
        ms = int((time.time() - start) * 1000)
        logger.info("DNS OK: host=%s ip=%s latency=%dms", host, ip, ms)
        return ip
    except socket.gaierror as e:
        logger.error("DNS FAIL: host=%s error=%s", host, e, exc_info=True)
        return None


def tcp_connect(host, port, timeout):
    start = time.time()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((host, port))
        ms = int((time.time() - start) * 1000)
        logger.info("TCP OK: %s:%d connected in %dms", host, port, ms)
        return True
    except (socket.timeout, OSError) as e:
        logger.error("TCP FAIL: %s:%d error=%s", host, port, e, exc_info=True)
        return False
    finally:
        try:
            s.close()
        except Exception:
            pass


def http_get(url, timeout):
    start = time.time()
    req = urllib.request.Request(url, headers={"User-Agent": "net-check/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = getattr(resp, "status", None)
            ms = int((time.time() - start) * 1000)
            logger.info("HTTP OK: url=%s status=%s latency=%dms", url, status, ms)
            return True
    except urllib.error.HTTPError as e:
        ms = int((time.time() - start) * 1000)
        logger.error(
            "HTTP FAIL: url=%s status=%s latency=%dms", url, e.code, ms, exc_info=True
        )
        return False
    except (urllib.error.URLError, socket.timeout) as e:
        logger.error("HTTP FAIL: url=%s error=%s", url, e, exc_info=True)
        return False


def run_with_retries(label, func, retries, delay):
    attempt = 1
    while attempt <= retries:
        logger.info("%s: attempt %d/%d", label, attempt, retries)
        ok = func()
        if ok:
            return ok
        if attempt < retries:
            logger.warning("%s: failed, retrying in %ss", label, delay)
            time.sleep(delay)
        attempt += 1
    return ok


def analyze_results(dns_ok, tcp_ok, http_ok, skipped_http):

    if not dns_ok:
        cause = "DNS resolution failed. The hostname could not be resolved to an IP."
        steps = (
            "1) Verify the hostname is correct.\n"
            "2) Check local DNS settings / resolver (e.g., try another network or DNS).\n"
            "3) If on AWS: verify Route 53 record and VPC DNS settings (enableDnsSupport/enableDnsHostnames)."
        )
        return cause, steps

    if dns_ok and not tcp_ok:
        cause = (
            "TCP connection failed. The host resolved, but the port is not reachable."
        )
        steps = (
            "1) Verify the destination port is correct and service is listening.\n"
            "2) Check firewall/security rules on the path.\n"
            "3) If on AWS: check Security Group, NACL, route table, and any proxy/egress controls."
        )
        return cause, steps

    if skipped_http:
        cause = "HTTP check was skipped by user."
        steps = (
            "Run again without --skip-http to validate application-layer connectivity."
        )
        return cause, steps

    # HTTP check ran
    if tcp_ok and not http_ok:
        cause = "HTTP request failed. Network path is likely OK, but application/URL/permissions may be an issue."
        steps = (
            "1) Confirm the URL path and protocol (http vs https).\n"
            "2) Check HTTP status/error in logs.\n"
            "3) If on AWS: check ALB/CloudFront/WAF rules, TLS settings, and origin health."
        )
        return cause, steps

    cause = "All checks passed (DNS, TCP, HTTP)."
    steps = (
        "If you still see issues in your app:\n"
        "1) Check application logs and latency metrics.\n"
        "2) Re-run with --retries and consider increasing --timeout.\n"
        "3) If on AWS: review CloudWatch metrics/logs and upstream dependency health."
    )
    return cause, steps


def main():
    parser = argparse.ArgumentParser(
        description="Minimal Network Troubleshooting Script"
    )
    parser.add_argument(
        "--host", default="example.com", help="Host to check (DNS + TCP)"
    )
    parser.add_argument("--port", type=int, default=443, help="TCP port to test")
    parser.add_argument(
        "--url", default="https://example.com", help="URL to test via HTTP GET"
    )
    parser.add_argument(
        "--timeout", type=float, default=5.0, help="Timeout seconds for TCP/HTTP"
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--skip-http", action="store_true", help="Skip HTTP check")
    parser.add_argument(
        "--retries", type=int, default=1, help="Retry times for each check (>=1)"
    )
    parser.add_argument(
        "--delay", type=float, default=1.0, help="Delay seconds between retries"
    )

    options = parser.parse_args()

    if options.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")

    logger.info("=== NET CHECK START ===")
    logger.info(
        "Input: host=%s port=%d url=%s timeout=%ss",
        options.host,
        options.port,
        options.url,
        options.timeout,
    )

    ip = dns_lookup(options.host)

    def tcp_job():
        return tcp_connect(options.host, options.port, options.timeout)

    tcp_ok = run_with_retries("TCP", tcp_job, options.retries, options.delay)

    if options.skip_http:
        logger.info("HTTP CHECK SKIPPED")
        http_ok = None
    else:

        def http_job():
            return http_get(options.url, options.timeout)

        http_ok = run_with_retries("HTTP", http_job, options.retries, options.delay)

    if http_ok is None:
        http_status = "SKIPPED"
    else:
        http_status = "OK" if http_ok else "FAIL"

    logger.info(
        "Summary: dns=%s tcp=%s http=%s",
        "OK" if ip else "FAIL",
        "OK" if tcp_ok else "FAIL",
        http_status,
    )
    logger.info("=== NET CHECK END ===")

    skipped_http = http_ok is None

    dns_ok = ip is not None

    likely_cause, next_steps = analyze_results(
        dns_ok, tcp_ok, (http_ok is True), skipped_http
    )

    logger.info("Likely cause: %s", likely_cause)
    logger.info("Next steps:\n%s", next_steps)


if __name__ == "__main__":
    main()
