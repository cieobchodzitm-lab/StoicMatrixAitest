#!/usr/bin/env python3
"""
StoicMatrix Performance Benchmark Suite

Measures:
- API response times
- Database query performance
- Memory usage
- Throughput
- Cache effectiveness
"""

import asyncio
import time
import psutil
import json
from typing import Dict, List
from datetime import datetime
import httpx
import statistics


class PerformanceBenchmark:
    def __init__(self, base_url: str = "http://localhost:7860"):
        self.base_url = base_url
        self.results = {}
        self.process = psutil.Process()

    async def measure_api_latency(
        self,
        endpoint: str,
        method: str = "GET",
        iterations: int = 100
    ) -> Dict:
        """
        Measure API endpoint latency
        """
        url = f"{self.base_url}{endpoint}"
        latencies = []

        async with httpx.AsyncClient() as client:
            for _ in range(iterations):
                start = time.time()
                try:
                    response = await client.request(method, url, timeout=30.0)
                    latency = (time.time() - start) * 1000  # Convert to ms
                    latencies.append(latency)
                except Exception as e:
                    print(f"Request failed: {e}")

        return {
            "endpoint": endpoint,
            "method": method,
            "iterations": iterations,
            "min_ms": min(latencies),
            "max_ms": max(latencies),
            "mean_ms": statistics.mean(latencies),
            "median_ms": statistics.median(latencies),
            "stdev_ms": statistics.stdev(latencies) if len(latencies) > 1 else 0,
            "p95_ms": sorted(latencies)[int(len(latencies) * 0.95)],
            "p99_ms": sorted(latencies)[int(len(latencies) * 0.99)]
        }

    async def measure_throughput(
        self,
        endpoint: str,
        concurrent_requests: int = 100,
        duration_seconds: int = 30
    ) -> Dict:
        """
        Measure requests per second (throughput)
        """
        url = f"{self.base_url}{endpoint}"
        request_count = 0
        error_count = 0
        start_time = time.time()

        async def make_request(client):
            nonlocal request_count, error_count
            try:
                await client.get(url, timeout=10.0)
                request_count += 1
            except Exception:
                error_count += 1

        async with httpx.AsyncClient() as client:
            while time.time() - start_time < duration_seconds:
                tasks = [
                    make_request(client)
                    for _ in range(concurrent_requests)
                ]
                await asyncio.gather(*tasks)

        elapsed = time.time() - start_time
        throughput = request_count / elapsed

        return {
            "endpoint": endpoint,
            "concurrent_requests": concurrent_requests,
            "duration_seconds": duration_seconds,
            "total_requests": request_count,
            "total_errors": error_count,
            "requests_per_second": throughput,
            "error_rate": error_count / (request_count + error_count)
        }

    def measure_memory_usage(self) -> Dict:
        """
        Measure current memory usage
        """
        memory_info = self.process.memory_info()

        return {
            "rss_mb": memory_info.rss / 1024 / 1024,  # Resident set size
            "vms_mb": memory_info.vms / 1024 / 1024,  # Virtual memory
            "percent": self.process.memory_percent(),
            "available_mb": psutil.virtual_memory().available / 1024 / 1024
        }

    def measure_cpu_usage(self, interval: float = 1.0) -> Dict:
        """
        Measure CPU usage
        """
        cpu_percent = self.process.cpu_percent(interval=interval)

        return {
            "percent": cpu_percent,
            "num_threads": self.process.num_threads(),
            "num_fds": self.process.num_fds() if hasattr(self.process, 'num_fds') else None
        }

    async def run_full_benchmark(self) -> Dict:
        """
        Run complete performance benchmark suite
        """
        print("🚀 Starting Performance Benchmark Suite")
        print("=" * 50)

        endpoints = [
            "/api/health",
            "/api/cnota/profile/1",
            "/api/cnota/leaderboard",
            "/api/passport/1"
        ]

        results = {
            "timestamp": datetime.now().isoformat(),
            "base_url": self.base_url,
            "latency": {},
            "throughput": {},
            "resources": {}
        }

        # Measure latency
        print("\n📊 Measuring API Latency...")
        for endpoint in endpoints:
            print(f"  Testing {endpoint}...")
            latency_result = await self.measure_api_latency(endpoint)
            results["latency"][endpoint] = latency_result
            print(f"    Mean: {latency_result['mean_ms']:.2f}ms, P95: {latency_result['p95_ms']:.2f}ms")

        # Measure throughput
        print("\n📈 Measuring Throughput...")
        for endpoint in endpoints:
            print(f"  Testing {endpoint}...")
            throughput_result = await self.measure_throughput(
                endpoint,
                concurrent_requests=50,
                duration_seconds=10
            )
            results["throughput"][endpoint] = throughput_result
            print(f"    {throughput_result['requests_per_second']:.2f} req/s")

        # Measure resources
        print("\n💾 Measuring Resource Usage...")
        results["resources"]["memory"] = self.measure_memory_usage()
        results["resources"]["cpu"] = self.measure_cpu_usage()
        print(f"  Memory: {results['resources']['memory']['rss_mb']:.2f}MB")
        print(f"  CPU: {results['resources']['cpu']['percent']:.2f}%")

        return results

    def generate_report(self, results: Dict) -> str:
        """
        Generate human-readable benchmark report
        """
        report = []
        report.append("\n" + "=" * 60)
        report.append("📋 PERFORMANCE BENCHMARK REPORT")
        report.append("=" * 60)
        report.append(f"\nTimestamp: {results['timestamp']}")
        report.append(f"Base URL: {results['base_url']}")

        # Latency Summary
        report.append("\n" + "-" * 60)
        report.append("API LATENCY (milliseconds)")
        report.append("-" * 60)
        report.append(f"{'Endpoint':<30} {'Mean':>10} {'P95':>10} {'P99':>10}")
        report.append("-" * 60)

        for endpoint, metrics in results["latency"].items():
            report.append(
                f"{endpoint:<30} "
                f"{metrics['mean_ms']:>10.2f} "
                f"{metrics['p95_ms']:>10.2f} "
                f"{metrics['p99_ms']:>10.2f}"
            )

        # Throughput Summary
        report.append("\n" + "-" * 60)
        report.append("THROUGHPUT (requests/second)")
        report.append("-" * 60)
        report.append(f"{'Endpoint':<30} {'RPS':>15} {'Error Rate':>10}")
        report.append("-" * 60)

        for endpoint, metrics in results["throughput"].items():
            report.append(
                f"{endpoint:<30} "
                f"{metrics['requests_per_second']:>15.2f} "
                f"{metrics['error_rate']:>10.2%}"
            )

        # Resource Summary
        report.append("\n" + "-" * 60)
        report.append("RESOURCE USAGE")
        report.append("-" * 60)
        report.append(f"Memory: {results['resources']['memory']['rss_mb']:.2f}MB")
        report.append(f"CPU: {results['resources']['cpu']['percent']:.2f}%")
        report.append(f"Threads: {results['resources']['cpu']['num_threads']}")

        report.append("\n" + "=" * 60)

        return "\n".join(report)


async def main():
    """
    Run benchmark suite
    """
    benchmark = PerformanceBenchmark()

    try:
        # Run benchmark
        results = await benchmark.run_full_benchmark()

        # Generate report
        report = benchmark.generate_report(results)
        print(report)

        # Save results
        with open("benchmark_results.json", "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n✅ Results saved to benchmark_results.json")

    except Exception as e:
        print(f"\n❌ Benchmark failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
