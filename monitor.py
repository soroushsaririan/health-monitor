import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional
import requests
from colorama import Fore, Style, init
from report_gen import save_health_results

init(autoreset=True)
SLOW_THRESHOLD_MS = 2000


class WebsiteMonitor:
    def __init__(
        self,
        config_path: str = "config.json",
        timeout: int = 5,
        max_workers: int = 10,
    ) -> None:
        self.timeout = timeout
        self.max_workers = max_workers
        self.urls: List[str] = self._load_urls(config_path)

    def _load_urls(self, config_path: str) -> List[str]:
        try:
            with open(config_path) as f:
                data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found: '{config_path}'")
        except json.JSONDecodeError:
            raise ValueError(f"Malformed JSON in '{config_path}'")
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and "urls" in data:
            return data["urls"]
        raise ValueError("Config must be a list of urls or a dict with a 'urls' key.")

    def _check(self, url: str) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "url": url,
            "status": "down",
            "status_code": None,
            "response_time": None,
            "error": None,
        }

        try:
            start = time.perf_counter()
            response = requests.get(url, timeout=self.timeout, allow_redirects=True)
            elapsed = round((time.perf_counter() - start) * 1000, 2)
            result["status_code"] = response.status_code
            result["response_time"] = elapsed
            if response.status_code == 200:
                result["status"] = "warn" if elapsed > SLOW_THRESHOLD_MS else "up"
            else:
                result["status"] = "down"
        except requests.exceptions.RequestException as e:
            result["error"] = str(e)
        return result

    def _print_result(self, result: Dict[str, Any]) -> None:
        status = result["status"]
        url = result["url"]
        if status == "up":
            tag = f"{Fore.GREEN}[ UP ]{Style.RESET_ALL}"
            detail = f"{result['response_time']}ms"
        elif status == "warn":
            tag = f"{Fore.YELLOW}[WARN]{Style.RESET_ALL}"
            detail = f"{result['response_time']}ms — slow response"
        else:
            tag = f"{Fore.RED}[DOWN]{Style.RESET_ALL}"
            detail = result.get("error") or f"HTTP {result.get('status_code', 'N/A')}"
        print(f"  {tag}  {url}  ({detail})")

    def _print_summary(self, results: List[Dict[str, Any]]) -> None:
        up   = sum(1 for r in results if r["status"] == "up")
        warn = sum(1 for r in results if r["status"] == "warn")
        down = sum(1 for r in results if r["status"] == "down")
        print(f"\n{Fore.CYAN}{'─' * 52}{Style.RESET_ALL}")
        print(
            f"  {Fore.GREEN}{up} up{Style.RESET_ALL}  "
            f"{Fore.YELLOW}{warn} slow{Style.RESET_ALL}  "
            f"{Fore.RED}{down} down{Style.RESET_ALL}  "
            f"/ {len(results)} total"
        )
        print(f"{Fore.CYAN}{'─' * 52}{Style.RESET_ALL}\n")

    def run(self) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        print(f"\n{Fore.CYAN}Scanning {len(self.urls)} target(s)...{Style.RESET_ALL}\n")
        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            futures = {pool.submit(self._check, url): url for url in self.urls}
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                self._print_result(result)

        self._print_summary(results)
        return results

def main() -> None:
    try:
        monitor = WebsiteMonitor()
        results = monitor.run()
        report_path = save_health_results(results)
        print(f"{Fore.CYAN}Report saved → {report_path}{Style.RESET_ALL}\n")
    except (FileNotFoundError, ValueError) as e:
        print(f"{Fore.RED}Configuration error: {e}{Style.RESET_ALL}")
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Scan interrupted.{Style.RESET_ALL}\n")

if __name__ == "__main__":
    main()
