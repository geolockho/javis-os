"""Bao cao CPU/RAM request/usage cua node pool va namespace tu Prometheus.

Chi dung stdlib. Chi DOC Prometheus, khong goi kubectl, khong sua cum.

  python resource_report.py snapshot            # tin 2 tieng, in text ra stdout
  python resource_report.py daily               # tong ket tu 00:00 hom nay toi bay gio + de xuat nen
  python resource_report.py daily --date 2026-10-27   # ca ngay 27/10

Mac dinh cho fsel-prod; doi bang --prom / --ns / --node-role.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

TZ = timezone(timedelta(hours=7))
# Prometheus scrape 2 ban kube-state-metrics (Helm + Lens) -> chi lay 1 ban de khoi nhan doi.
KSM = 'service="monitoring-prometheus-kube-state-metrics"'
CTR = 'container!="",container!="POD"'
STEP = 300  # 5 phut
SLACK_MAX = 4800  # Slack gioi han 5000 ky tu moi khoi text
WARN, CRIT, WASTE = 80.0, 90.0, 20.0
DATA_DIR = Path(__file__).resolve().parents[3] / "workspace" / "k8s-resource-report"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


class Prom:
    def __init__(self, base: str):
        self.base = base.rstrip("/")
        if not self.base.startswith("http"):
            self.base = "https://" + self.base

    def _get(self, path: str, params: dict) -> list:
        url = f"{self.base}{path}?{urllib.parse.urlencode(params)}"
        try:
            with urllib.request.urlopen(url, timeout=90) as r:
                body = json.load(r)
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"Prometheus HTTP {e.code}: {e.read()[:300]!r} | query={params.get('query', '')[:200]}") from None
        if body.get("status") != "success":
            raise RuntimeError(f"Prometheus loi: {body}")
        return body["data"]["result"]

    def query(self, q: str, at: float | None = None) -> list:
        p = {"query": q}
        if at:
            p["time"] = at
        return self._get("/api/v1/query", p)

    def scalar(self, q: str, at: float | None = None) -> float:
        res = self.query(q, at)
        return float(res[0]["value"][1]) if res else 0.0

    def by(self, q: str, label: str, at: float | None = None) -> dict:
        return {r["metric"].get(label, ""): float(r["value"][1]) for r in self.query(q, at)}

    def range(self, q: str, start: float, end: float, label: str) -> dict:
        res = self._get("/api/v1/query_range", {"query": q, "start": start, "end": end, "step": STEP})
        return {r["metric"].get(label, ""): {float(t): float(v) for t, v in r["values"]} for r in res}


# ---------- ten service ----------
RS_RE = re.compile(r"^(.+)-[a-z0-9]{5,10}$")
POD_DEPLOY_RE = re.compile(r"^(.+)-[a-z0-9]{6,10}-[a-z0-9]{5}$")
POD_STS_RE = re.compile(r"^(.+)-\d+$")


def service_map(prom: Prom, ns: str) -> dict:
    """pod -> ten workload (Deployment/StatefulSet/...) qua kube_pod_owner + kube_replicaset_owner."""
    rs_owner = {}
    for r in prom.query(f'kube_replicaset_owner{{{KSM},namespace="{ns}"}}'):
        m = r["metric"]
        rs_owner[m.get("replicaset", "")] = m.get("owner_name") or m.get("replicaset", "")
    out = {}
    for r in prom.query(f'kube_pod_owner{{{KSM},namespace="{ns}"}}'):
        m = r["metric"]
        pod, kind, name = m.get("pod", ""), m.get("owner_kind", ""), m.get("owner_name", "")
        if kind == "ReplicaSet":
            out[pod] = rs_owner.get(name) or (RS_RE.match(name).group(1) if RS_RE.match(name) else name)
        elif kind == "Job":
            out[pod] = re.sub(r"-\d{6,}$", "", name)  # job cua CronJob -> ten CronJob
        elif name and name != "<none>":
            out[pod] = name
    return out


def svc_of(pod: str, smap: dict) -> str:
    if pod in smap:
        return smap[pod]
    for rx in (POD_DEPLOY_RE, POD_STS_RE):
        m = rx.match(pod)
        if m:
            return m.group(1)
    return pod


# ---------- dinh dang ----------
def cores(v: float) -> str:
    return f"{v:.2f}" if v < 10 else f"{v:.1f}"


def gib(v: float) -> str:
    return f"{v / 2**30:.1f}"


def mcpu(v: float) -> str:
    return f"{v * 1000:.0f}m" if v < 1 else f"{v:.2f}"


def mib(v: float) -> str:
    return f"{v / 2**20:.0f}Mi" if v < 2**30 else f"{v / 2**30:.1f}Gi"


def pct(a: float, b: float) -> float | None:
    return a / b * 100 if b else None


def fp(v: float | None, d: int = 0) -> str:
    return "-" if v is None else f"{v:.{d}f}%"


def quantile(vals: list, q: float) -> float:
    if not vals:
        return 0.0
    s = sorted(vals)
    k = (len(s) - 1) * q
    lo, hi = math.floor(k), math.ceil(k)
    return s[lo] + (s[hi] - s[lo]) * (k - lo)


# ---------- truy van ----------
def node_list(prom: Prom, role: str) -> list:
    res = prom.query(f'count by (node) (container_memory_working_set_bytes{{id="/",node_role="{role}"}})')
    return sorted(r["metric"]["node"] for r in res)


def running_filter(ns_sel: str) -> str:
    return f'on(namespace,pod) group_left() (max by(namespace,pod)(kube_pod_status_phase{{{KSM},{ns_sel}phase="Running"}}) == 1)'


def node_summary(prom: Prom, nodes: list, start: float, end: float) -> dict:
    nre = "|".join(nodes)  # ten node chi gom [a-z0-9-], khong escape vi PromQL string khong nhan "\-"
    nsel = f'node=~"{nre}"'
    run = running_filter("")
    s = {
        "nodes": len(nodes),
        "alloc_cpu": prom.scalar(f'sum(kube_node_status_allocatable{{{KSM},{nsel},resource="cpu"}})'),
        "alloc_mem": prom.scalar(f'sum(kube_node_status_allocatable{{{KSM},{nsel},resource="memory"}})'),
        "req_cpu": prom.scalar(f'sum(kube_pod_container_resource_requests{{{KSM},{nsel},resource="cpu"}} * {run})'),
        "req_mem": prom.scalar(f'sum(kube_pod_container_resource_requests{{{KSM},{nsel},resource="memory"}} * {run})'),
        "use_cpu": prom.scalar(f'sum(rate(container_cpu_usage_seconds_total{{id="/",{nsel}}}[5m]))'),
        "use_mem": prom.scalar(f'sum(container_memory_working_set_bytes{{id="/",{nsel}}})'),
    }
    cpu_r = prom.range(f'sum(rate(container_cpu_usage_seconds_total{{id="/",{nsel}}}[5m]))', start, end, "x")
    mem_r = prom.range(f'sum(container_memory_working_set_bytes{{id="/",{nsel}}})', start, end, "x")
    cv = list(next(iter(cpu_r.values()), {}).values())
    mv = list(next(iter(mem_r.values()), {}).values())
    s["cpu_avg"], s["cpu_max"] = (sum(cv) / len(cv), max(cv)) if cv else (0, 0)
    s["mem_avg"], s["mem_max"] = (sum(mv) / len(mv), max(mv)) if mv else (0, 0)
    return s


def hpa_info(prom: Prom, ns: str) -> dict:
    sel = f'{KSM},namespace="{ns}"'
    target = {}
    for r in prom.query(f"kube_horizontalpodautoscaler_info{{{sel}}}"):
        m = r["metric"]
        target[m["horizontalpodautoscaler"]] = m.get("scaletargetref_name") or m["horizontalpodautoscaler"]
    mins = prom.by(f"kube_horizontalpodautoscaler_spec_min_replicas{{{sel}}}", "horizontalpodautoscaler")
    maxs = prom.by(f"kube_horizontalpodautoscaler_spec_max_replicas{{{sel}}}", "horizontalpodautoscaler")
    cur = prom.by(f"kube_horizontalpodautoscaler_status_current_replicas{{{sel}}}", "horizontalpodautoscaler")
    out = {}
    for name in set(mins) | set(target):
        out[target.get(name, name)] = {"hpa": name, "min": int(mins.get(name, 0)),
                                       "max": int(maxs.get(name, 0)), "current": int(cur.get(name, 0))}
    for r in prom.query(f"kube_horizontalpodautoscaler_spec_target_metric{{{sel}}}"):
        m = r["metric"]
        svc = target.get(m["horizontalpodautoscaler"], m["horizontalpodautoscaler"])
        if svc in out:
            out[svc][f"target_{m.get('metric_name', '?')}"] = int(float(r["value"][1]))
    return out


def service_stats(prom: Prom, ns: str, start: float, end: float) -> dict:
    smap = service_map(prom, ns)
    nsel = f'namespace="{ns}"'
    run = running_filter(f"{nsel},")
    req = {res: prom.by(f'sum by (pod) (kube_pod_container_resource_requests{{{KSM},{nsel},resource="{res}"}} * {run})', "pod")
           for res in ("cpu", "memory")}
    lim = {res: prom.by(f'sum by (pod) (kube_pod_container_resource_limits{{{KSM},{nsel},resource="{res}"}} * {run})', "pod")
           for res in ("cpu", "memory")}
    cpu_now = prom.by(f"sum by (pod) (rate(container_cpu_usage_seconds_total{{{nsel},{CTR}}}[5m]))", "pod")
    mem_now = prom.by(f"sum by (pod) (container_memory_working_set_bytes{{{nsel},{CTR}}})", "pod")
    cpu_rng = prom.range(f"sum by (pod) (rate(container_cpu_usage_seconds_total{{{nsel},{CTR}}}[5m]))", start, end, "pod")
    mem_rng = prom.range(f"sum by (pod) (container_memory_working_set_bytes{{{nsel},{CTR}}})", start, end, "pod")

    running_pods = set(req["cpu"]) | set(req["memory"]) | set(cpu_now)
    svcs: dict = {}

    def s(name):
        return svcs.setdefault(name, {"pods": 0, "req_cpu": 0.0, "req_mem": 0.0, "lim_cpu": 0.0, "lim_mem": 0.0,
                                      "pod_req_cpu": 0.0, "pod_req_mem": 0.0, "pod_lim_cpu": 0.0, "pod_lim_mem": 0.0,
                                      "use_cpu": 0.0, "use_mem": 0.0, "no_metrics": 0})

    for pod in running_pods:
        d = s(svc_of(pod, smap))
        d["pods"] += 1
        for k, src in (("req_cpu", req["cpu"]), ("req_mem", req["memory"]), ("lim_cpu", lim["cpu"]), ("lim_mem", lim["memory"])):
            v = src.get(pod, 0.0)
            d[k] += v
            d["pod_" + k] = max(d["pod_" + k], v)
        if pod in cpu_now:
            d["use_cpu"] += cpu_now[pod]
            d["use_mem"] += mem_now.get(pod, 0.0)
        else:
            d["no_metrics"] += 1

    # chuoi thoi gian: tong theo service + gia tri tung pod
    for metric, rng in (("cpu", cpu_rng), ("mem", mem_rng)):
        tot: dict = {}
        per_pod: dict = {}
        count: dict = {}
        for pod, series in rng.items():
            name = svc_of(pod, smap)
            for t, v in series.items():
                tot.setdefault(name, {}).setdefault(t, 0.0)
                tot[name][t] += v
                count.setdefault(name, {}).setdefault(t, 0)
                count[name][t] += 1
                per_pod.setdefault(name, []).append(v)
        for name, series in tot.items():
            d = s(name)
            vals = list(series.values())
            d[f"{metric}_avg"] = sum(vals) / len(vals)
            d[f"{metric}_max"] = max(vals)
            d[f"{metric}_p95"] = quantile(vals, 0.95)
            d[f"pod_{metric}_p95"] = quantile(per_pod[name], 0.95)
            d[f"pod_{metric}_max"] = max(per_pod[name])
            reps = list(count[name].values())
            d["replicas_min"], d["replicas_max"] = min(reps), max(reps)
    return svcs


# ---------- de xuat nen (agent duyet lai) ----------
def round_cpu(v: float) -> float:
    step = 0.01 if v < 1 else 0.05
    return max(0.05, math.ceil(v / step) * step)


def round_mem(v: float) -> float:
    step = 64 * 2**20
    return max(128 * 2**20, math.ceil(v / step) * step)


def baseline(d: dict, hpa: dict | None) -> dict:
    """request = p95 tung pod x1.3 (co HPA thi khong de p95 vuot 85% target), limit = max tung pod x1.5.
    Chi danh dau khi lech > 20%. Day la goi y THO, agent phai duyet lai."""
    if "pod_cpu_p95" not in d:
        return {}
    sug = {
        "req_cpu": round_cpu(d["pod_cpu_p95"] * 1.3),
        "req_mem": round_mem(d["pod_mem_p95"] * 1.3),
        "lim_cpu": round_cpu(d["pod_cpu_max"] * 1.5),
        "lim_mem": round_mem(d["pod_mem_max"] * 1.5),
    }
    # RAM khong nen duoc: request khong duoi dinh that cua pod, kenh bi evict khi node thieu RAM.
    sug["req_mem"] = max(sug["req_mem"], round_mem(d["pod_mem_max"]))
    # Co HPA: p95 sau khi doi request phai nam duoi 85% target, kenh khong HPA scale lien tuc.
    if hpa:
        if hpa.get("target_cpu"):
            sug["req_cpu"] = max(sug["req_cpu"], round_cpu(d["pod_cpu_p95"] / (hpa["target_cpu"] / 100 * 0.85)))
        if hpa.get("target_memory"):
            sug["req_mem"] = max(sug["req_mem"], round_mem(d["pod_mem_p95"] / (hpa["target_memory"] / 100 * 0.85)))
    flags = []
    for k, cur_k, floor in (("req_cpu", "pod_req_cpu", 0.05), ("req_mem", "pod_req_mem", 128 * 2**20)):
        cur = d[cur_k]
        if cur == 0:
            flags.append(f"{k}: chua dat request")
        elif abs(sug[k] - cur) / cur > 0.2 and abs(sug[k] - cur) >= floor:
            flags.append(f"{k}: {'giam' if sug[k] < cur else 'tang'}")
    # lim phai >= req de xuat
    sug["lim_cpu"] = max(sug["lim_cpu"], sug["req_cpu"])
    sug["lim_mem"] = max(sug["lim_mem"], sug["req_mem"])
    out = {"suggest": sug, "flags": flags,
           "util_p95_cpu_now": pct(d["pod_cpu_p95"], d["pod_req_cpu"]),
           "util_p95_mem_now": pct(d["pod_mem_p95"], d["pod_req_mem"]),
           "util_p95_cpu_new": pct(d["pod_cpu_p95"], sug["req_cpu"]),
           "util_p95_mem_new": pct(d["pod_mem_p95"], sug["req_mem"])}
    if hpa:
        out["hpa_pinned_at_min"] = d.get("replicas_max", 0) <= hpa["min"]
        out["hpa_hit_max"] = d.get("replicas_max", 0) >= hpa["max"]
    return out


# ---------- de xuat giam cho service dung duoi 50% request (script tinh, khong de LLM uoc luong) ----------
LOW = 50.0
HPA_TARGET_FLOOR = {"cpu": 70, "memory": 80}  # target HPA thap hon muc nay thi de xuat nang de giam request them
VALUES_DIR = Path(r"D:\argocd-deploy-clean\values\fsel-prod")


def values_index(root: Path) -> dict:
    """fullnameOverride -> thu muc + autoscaling.enabled. Chi doc values.yaml, KHONG mo templates/ (co mat khau)."""
    out = {}
    if not root.is_dir():
        return out
    for f in root.glob("*/values.yaml"):
        txt = f.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"""^\s*fullnameOverride:\s*["']?([\w.-]+)""", txt, re.M)
        if not m:
            continue
        a = re.search(r"^\s*autoscaling:\s*\n\s*enabled:\s*(\w+)", txt, re.M)
        out[m.group(1)] = {"dir": f.parent.name, "hpa_in_git": bool(a and a.group(1).lower() == "true")}
    return out


def proposals(svcs: dict, week: dict, hpas: dict, vidx: dict) -> list:
    """Service co p95 moi pod trong N ngay < 50% request (CPU hoac RAM) -> request moi, target HPA moi.
    request moi = p95 x1.3 (RAM khong duoi dinh that cua pod); co HPA thi p95 phai < 85% target.
    Nang target HPA len 70% CPU / 80% RAM chi khi nho vay request giam them duoc."""
    out = []
    specs = (("cpu", "pod_req_cpu", round_cpu, 0.05), ("memory", "pod_req_mem", round_mem, 128 * 2**20))
    for name, d in svcs.items():
        w = week.get(name, {})
        if d["pods"] == 0 or "pod_cpu_p95" not in w:
            continue
        h = hpas.get(name) or {}
        item = {"service": name, "pods": d["pods"], "hpa": h.get("hpa"), "values": vidx.get(name), "changed": []}
        for res, key, rnd, floor in specs:
            m = "cpu" if res == "cpu" else "mem"
            cur, p95, peak = d[key], w[f"pod_{m}_p95"], w[f"pod_{m}_max"]
            t = h.get(f"target_{res}")
            r = {"cur": cur, "p95": p95, "util": pct(p95, cur), "new": cur, "target": t, "target_new": t}
            if r["util"] is not None and r["util"] < LOW:
                def req_for(target):
                    v = p95 * 1.3
                    if res == "memory":
                        v = max(v, peak)
                    if target:
                        v = max(v, p95 / (target / 100 * 0.85))
                    return rnd(v)
                new = req_for(t)
                if t and t < HPA_TARGET_FLOOR[res] and req_for(HPA_TARGET_FLOOR[res]) < new:
                    r["target_new"] = HPA_TARGET_FLOOR[res]
                    new = req_for(r["target_new"])
                if new < cur and (cur - new) / cur > 0.2 and cur - new >= floor:
                    r["new"] = new
                    item["changed"].append(res)
                else:
                    r["target_new"] = t
            r["util_new"] = pct(p95, r["new"])
            item[res] = r
        if item["changed"]:
            item["save_cpu"] = (item["cpu"]["cur"] - item["cpu"]["new"]) * d["pods"]
            item["save_mem"] = (item["memory"]["cur"] - item["memory"]["new"]) * d["pods"]
            out.append(item)
    out.sort(key=lambda x: -(x["save_cpu"] + x["save_mem"] / 2**30 / 2))  # ~1 core ngang 2 GiB
    return out


def render_proposals(props: list, svcs: dict, hpas: dict, rec_days: float) -> str:
    live = [d for d in svcs.values() if d["pods"] > 0]
    ns_cpu, ns_mem = sum(d["req_cpu"] for d in live), sum(d["req_mem"] for d in live)
    head = [f"*Đề xuất cấu hình: service dùng dưới {LOW:.0f}% request* (p95 mỗi pod trong {rec_days:g} ngày)"]
    if not props:
        return head[0] + f"\nKhông service nào dưới {LOW:.0f}% request đủ để giảm (lệch > 20%)."
    sc, sm = sum(p["save_cpu"] for p in props), sum(p["save_mem"] for p in props)
    head.append(f"Áp dụng hết: giải phóng *{cores(sc)} core* ({fp(pct(sc, ns_cpu))}) và *{gib(sm)} GiB* "
                f"({fp(pct(sm, ns_mem))}) request của namespace. Số trong ngoặc = p95 / request.")

    def cell(r, fmt):
        cur = f"{fmt(r['p95'])} ({fp(r['util'])})"
        new = f"{fmt(r['new'])} ({fp(r['util_new'])})" if r["new"] != r["cur"] else "-"
        return [fmt(r["cur"]), cur, new]

    def tgt(r):
        if not r["target"]:
            return "-"
        return f"{r['target']}→{r['target_new']}" if r["target_new"] != r["target"] else f"{r['target']}"

    def where(p):
        v = p["values"]
        if not v:
            return "ngoài repo"
        hpa_cluster = p["hpa"] and not v["hpa_in_git"] and any(p[r]["target_new"] != p[r]["target"] for r in ("cpu", "memory"))
        return v["dir"] + (" + HPA cụm" if hpa_cluster else "")

    hdr = ["SERVICE", "POD", "CPU req", "p95", "đề xuất", "RAM req", "p95", "đề xuất", "HPA CPU", "HPA RAM", "sửa ở"]
    rows = [[p["service"], f"{p['pods']}" + ("*" if p["hpa"] else ""), *cell(p["cpu"], mcpu), *cell(p["memory"], mib),
             tgt(p["cpu"]), tgt(p["memory"]), where(p)] for p in props]
    foot = ["Request: `values/fsel-prod/<sửa ở>/values.yaml`, key `fsel.resources.requests.cpu|memory`. "
            "\"HPA cụm\" = HPA không nằm trong git, đổi `spec.metrics[].resource.target.averageUtilization` bằng "
            "`kubectl --context fsel-prod -n fsel-prod edit hpa <tên>`.",
            "Limit giữ nguyên. Xếp theo lượng tài nguyên giải phóng. * = có HPA.",
            "_Chỉ là đề xuất, chưa áp dụng gì lên cụm hay repo._"]

    def table(rs):
        return (["| " + " | ".join(hdr) + " |", "|:---|" + "---:|" * (len(hdr) - 2) + ":---|"]
                + ["| " + " | ".join(r) + " |" for r in rs])

    keep = len(rows)
    while keep > 0 and len("\n".join(head + table(rows[:keep]) + foot)) + 60 > SLACK_MAX:
        keep -= 1
    if keep < len(rows):
        foot.insert(0, f"_Ẩn {len(rows) - keep} đề xuất nhỏ nhất cho vừa giới hạn Slack._")
    return "\n".join(head + table(rows[:keep]) + foot)


# ---------- render ----------
def render(title: str, ns: str, role: str, n: dict, svcs: dict, hpas: dict, window_label: str, daily: bool,
           table: str = "md") -> str:
    L = []
    L.append(f"*{title}*  (node_role={role}, ns={ns})")
    L.append(f"Nodes: {n['nodes']} | Total CPU: {cores(n['alloc_cpu'])} cores | Total RAM: {gib(n['alloc_mem'])} GiB")
    L.append(f"CPU Request: {fp(pct(n['req_cpu'], n['alloc_cpu']), 1)} | RAM Request: {fp(pct(n['req_mem'], n['alloc_mem']), 1)}")
    L.append(f"CPU Usage: {pct(n['use_cpu'], n['alloc_cpu']):.1f}% (TB {window_label}: {pct(n['cpu_avg'], n['alloc_cpu']):.1f}%, "
             f"max: {pct(n['cpu_max'], n['alloc_cpu']):.1f}%)")
    L.append(f"RAM Usage: {pct(n['use_mem'], n['alloc_mem']):.1f}% (TB {window_label}: {pct(n['mem_avg'], n['alloc_mem']):.1f}%, "
             f"max: {pct(n['mem_max'], n['alloc_mem']):.1f}%)")

    live = {k: v for k, v in svcs.items() if v["pods"] > 0}
    t = {k: sum(v[k] for v in live.values()) for k in ("pods", "req_cpu", "req_mem", "use_cpu", "use_mem")}
    L.append(f"Namespace {ns}: {t['pods']} pod / {len(live)} service | CPU req {cores(t['req_cpu'])} core, "
             f"dùng {cores(t['use_cpu'])} ({fp(pct(t['use_cpu'], t['req_cpu']))}) | RAM req {gib(t['req_mem'])} GiB, "
             f"dùng {gib(t['use_mem'])} ({fp(pct(t['use_mem'], t['req_mem']))})")

    alerts, waste = [], []
    for name, d in live.items():
        for lab, u, r in (("CPU", d["use_cpu"], d["req_cpu"]), ("RAM", d["use_mem"], d["req_mem"])):
            p = pct(u, r)
            if p is None:
                continue
            if p >= CRIT:
                alerts.append(f":red_circle: {name} {lab} {p:.0f}% request (NGHIÊM TRỌNG)")
            elif p >= WARN:
                alerts.append(f":warning: {name} {lab} {p:.0f}% request")
        pc, pm = pct(d.get("cpu_max", d["use_cpu"]), d["req_cpu"]), pct(d.get("mem_max", d["use_mem"]), d["req_mem"])
        if pc is not None and pm is not None and pc < WASTE and pm < WASTE:
            waste.append(name)
    norq = [k for k, d in live.items() if d["req_cpu"] == 0 or d["req_mem"] == 0]
    nomet = sum(d["no_metrics"] for d in live.values())
    alerts.sort(key=lambda x: (not x.startswith(":red"), x))
    if alerts:
        L.append("*Vượt ngưỡng usage/request:*")
        L.extend(alerts)
    else:
        L.append(f"Không service nào vượt {WARN:.0f}% request.")
    if norq:
        L.append("Thiếu request: " + ", ".join(sorted(norq)))
    if nomet:
        L.append(f"{nomet} pod chưa có số liệu usage.")
    if waste:
        L.append(f"Dùng dưới {WASTE:.0f}% request cả CPU lẫn RAM (theo max {window_label}): " + ", ".join(sorted(waste)))

    def ratio_key(kv):
        # Tang dan theo trung binh %CPU va %RAM (dung/request): service request nhieu ma it dung len dau.
        # Khong lay % thap hon vi service vuot RAM (vd 109%) nhung CPU 0% se bi day len dau sai y.
        # Cung ti le thi service request nhieu CPU hon dung truoc. Thieu request xuong cuoi bang.
        d = kv[1]
        ps = [p for p in (pct(d["use_cpu"], d["req_cpu"]), pct(d["use_mem"], d["req_mem"])) if p is not None]
        return (sum(ps) / len(ps) if ps else math.inf, -d["req_cpu"])

    rows = []
    for name, d in sorted(live.items(), key=ratio_key):
        pods = f"{d['pods']}" + ("*" if hpas.get(name) else "")
        rows.append([name, pods, mcpu(d["req_cpu"]), mcpu(d["use_cpu"]), fp(pct(d["use_cpu"], d["req_cpu"])),
                     mcpu(d.get("cpu_max", 0)), mib(d["req_mem"]), mib(d["use_mem"]),
                     fp(pct(d["use_mem"], d["req_mem"])), mib(d.get("mem_max", 0))])
    hdr = ["SERVICE", "POD", "CPU req", "dùng", "%", "max", "RAM req", "dùng", "%", "max"]

    def table_lines(rs):
        if table == "code":
            w = [34, 4, 9, 8, 5, 8, 9, 8, 5, 8]
            fmt = lambda r: f"{r[0][:33]:<{w[0]}}" + "".join(f"{c:>{n}}" for c, n in zip(r[1:], w[1:]))
            return ["```\n" + "\n".join(fmt(r) for r in [hdr] + rs) + "\n```"]
        # Bang markdown: Slack ve thanh bang that, chu co tin nhan thuong (to hon code block 1 co).
        return (["| " + " | ".join(hdr) + " |", "|:---|" + "---:|" * (len(hdr) - 1)]
                + ["| " + " | ".join(r) + " |" for r in rs])

    foot = [f"_Sắp xếp: trung bình %CPU và %RAM (dùng/request) thấp nhất lên đầu = request nhiều mà ít dùng._",
            f"_* = có HPA. max = đỉnh tổng service trong {window_label}. Nguồn: Prometheus._"]
    # Qua gioi han Slack thi bo bot dong cuoi bang (service dung sat request nhat, it can xem nhat).
    keep = len(rows)
    while keep > 0 and len("\n".join(L + table_lines(rows[:keep]) + foot)) + 60 > SLACK_MAX:
        keep -= 1
    if keep < len(rows):
        foot.insert(0, f"_Ẩn {len(rows) - keep} service dùng sát request nhất cho vừa giới hạn Slack._")
    return "\n".join(L + table_lines(rows[:keep]) + foot)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["snapshot", "daily", "proposals"])
    ap.add_argument("--prom", default="https://prometheus-prod.fsel.edu.vn")
    ap.add_argument("--ns", default="fsel-prod")
    ap.add_argument("--node-role", default="appnodes-prod2")
    ap.add_argument("--hours", type=float, default=2.0, help="cua so cho snapshot")
    ap.add_argument("--date", help="daily: YYYY-MM-DD (mac dinh hom nay, tu 00:00 toi bay gio)")
    ap.add_argument("--table", choices=["md", "code"], default="md",
                    help="md = bang Slack (chu to), code = bang chu deu trong code block nhu ban cu")
    ap.add_argument("--rec-days", type=float, default=7, help="daily: so ngay du lieu de tinh goi y")
    args = ap.parse_args()

    prom = Prom(args.prom)
    now = datetime.now(TZ)
    if args.mode == "snapshot":
        end = now.timestamp()
        start = end - args.hours * 3600
        label = f"{args.hours:g}h"
        title = f"fsel-prod tài nguyên | {now:%d/%m %H:%M}"
    else:
        day = datetime.strptime(args.date, "%Y-%m-%d").replace(tzinfo=TZ) if args.date else now.replace(hour=0, minute=0, second=0, microsecond=0)
        start = day.timestamp()
        end = min(now.timestamp(), (day + timedelta(days=1)).timestamp())
        label = "ngày"
        title = f"fsel-prod TỔNG KẾT NGÀY {day:%d/%m} ({day:%H:%M}-{datetime.fromtimestamp(end, TZ):%H:%M})"

    if args.mode == "proposals":
        # Chi phan de xuat (hoi nhanh trong chat): so lieu hien tai + rec_days ngay toi bay gio.
        end = now.timestamp()
        svcs = service_stats(prom, args.ns, end - 3600, end)
        week = service_stats(prom, args.ns, end - args.rec_days * 86400, end)
        hpas = hpa_info(prom, args.ns)
        print(render_proposals(proposals(svcs, week, hpas, values_index(VALUES_DIR)), svcs, hpas, args.rec_days))
        return

    nodes = node_list(prom, args.node_role)
    if not nodes:
        print(f"LỖI: không tìm thấy node nào có node_role={args.node_role} trong Prometheus.")
        sys.exit(2)
    n = node_summary(prom, nodes, start, end)
    svcs = service_stats(prom, args.ns, start, end)
    hpas = hpa_info(prom, args.ns)
    print(render(title, args.ns, args.node_role, n, svcs, hpas, label, args.mode == "daily", args.table))

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    rec = {"at": now.isoformat(timespec="seconds"), "mode": args.mode, "ns": args.ns, "node_role": args.node_role,
           "nodes": nodes, "node_summary": n, "window": [start, end]}
    if args.mode == "snapshot":
        with open(DATA_DIR / f"snapshots-{now:%Y-%m-%d}.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    else:
        # goi y tinh tren rec_days ngay (Prometheus giu 90 ngay), so lieu hom nay giu de doi chieu
        week = service_stats(prom, args.ns, end - args.rec_days * 86400, end)
        rec["rec_days"] = args.rec_days
        rec["services"] = {k: {"today": v, f"last_{args.rec_days:g}d": week.get(k, {}), "hpa": hpas.get(k),
                               "baseline": baseline({**v, **{x: y for x, y in week.get(k, {}).items() if x.startswith(("pod_cpu", "pod_mem", "replicas"))}}, hpas.get(k))}
                           for k, v in svcs.items() if v["pods"] > 0}
        props = proposals(svcs, week, hpas, values_index(VALUES_DIR))
        rec["proposals"] = props
        # Tin thu 2 (reply trong thread cua tin tong ket), gui nguyen van.
        print("\n===DE_XUAT===")
        print(render_proposals(props, svcs, hpas, args.rec_days))
        path = DATA_DIR / f"daily-{datetime.fromtimestamp(start, TZ):%Y-%m-%d}.json"
        path.write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\nDATA_JSON: {path}")


if __name__ == "__main__":
    main()
