# 🌐 Network Troubleshooting CLI Tool

A minimal but production-style **network troubleshooting CLI tool** designed in the mindset of a **Cloud Support Engineer**.

This tool performs layered connectivity checks (DNS → TCP → HTTP), records all steps via structured logging, and automatically provides **Likely Root Cause** and **Recommended Next Steps**, similar to real support ticket workflows.

---

## 🎯 Purpose

This project focuses on **how Cloud Support engineers diagnose connectivity issues**, rather than on complex coding.

It demonstrates how to:

- Narrow down issues by network layer
- Avoid guesswork using evidence-based checks
- Produce logs and conclusions suitable for support tickets or escalation

---

## 🔍 What the Tool Checks

1. **DNS Resolution**
   - Verifies hostname can be resolved to an IP
2. **TCP Connectivity**
   - Tests whether the target port is reachable
3. **HTTP Reachability**
   - Sends an HTTP GET request to confirm application-layer access
4. **Retries & Timeouts**
   - Handles transient network failures realistically
5. **Automated Analysis**
   - Outputs likely root cause and next steps based on results

---

## 🖥️ Usage

### Basic run (default values)

```bash
python3 net_check.py
```

### Check a real endpoint

```bash
python3 net_check.py \
 --host google.com \
 --port 443 \
 --url https://google.com
```

### Enable retries and delay

```bash
python3 net_check.py \
 --host google.com \
 --port 443 \
 --url https://google.com \
 --retries 3 \
 --delay 0.5
```

### Skip HTTP check (network-only)

```bash
python3 net_check.py \
 --host google.com \
 --port 443 \
 --skip-http
```

### Enable debug logging

```bash
python3 net_check.py --debug
```

---

## ⚙️ CLI Arguments

| Argument      | Description                     | Default               |
| ------------- | ------------------------------- | --------------------- |
| `--host`      | Hostname to resolve and connect | `example.com`         |
| `--port`      | TCP port to test                | `443`                 |
| `--url`       | URL for HTTP GET check          | `https://example.com` |
| `--timeout`   | Timeout seconds                 | `5.0`                 |
| `--retries`   | Retry attempts                  | `1`                   |
| `--delay`     | Delay between retries (seconds) | `1.0`                 |
| `--skip-http` | Skip HTTP check                 | `False`               |
| `--debug`     | Enable DEBUG logging            | `False`               |

---

## 🪵 Logging

- Logs are written to:
  - **Terminal**
  - **`app.log` file**
- Logging includes:
  - Timestamps
  - Severity levels
  - Full error tracebacks (when applicable)

Example:

```text
2026-01-08 15:00:33 [INFO] TCP: attempt 1/3
2026-01-08 15:00:34 [INFO] HTTP OK: status=200 latency=1491ms
```

---

## 🧠 Automated Analysis Output

At the end of each run, the tool prints:

- **Likely cause**
- **Recommended next steps**

Example:

```text
Likely cause: All checks passed (DNS, TCP, HTTP).

Next steps:

1. Check application logs and latency metrics.
2. Re-run with retries or increase timeout.
3. # If on AWS: review CloudWatch logs and upstream dependencies.
```

This format mirrors real **Cloud Support ticket summaries**.

---

## ☁️ Cloud Support Mapping

| Tool Check | Cloud Equivalent                  |
| ---------- | --------------------------------- |
| DNS        | Route 53 / VPC DNS                |
| TCP        | Security Groups / NACLs / Routing |
| HTTP       | ALB / CloudFront / WAF            |
| Logging    | CloudWatch Logs                   |
| Retries    | Transient network handling        |

---

## 🧩 What This Project Demonstrates

- Structured troubleshooting instead of trial-and-error
- CLI-driven operational tools
- Logging-first debugging mindset
- Clear escalation-ready output
- Realistic Cloud Support workflows

---

## 🚀 Possible Improvements

- JSON output for automation
- Ticket-style output (`Observation / Impact / Recommendation`)
- Parallel checks
- AWS-native version (Lambda + CloudWatch)

---

## ✨ Final Note

This project represents a shift from:

> “Does it work?”

to:

> **“If it fails, can I prove why?”**

That mindset is the foundation of Cloud Support and DevOps work.

make conflict
