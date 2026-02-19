import csv
import os
from datetime import datetime
from typing import Any, Dict, List


FIELDNAMES = ['url', 'status', 'status_code', 'response_time_ms', 'error', 'timestamp']

def save_health_results(results: List[Dict[str, Any]], output_path: str = None) -> str:
    now = datetime.now()
    if output_path is None:
        output_path = f"health_report_{now.strftime('%Y%m%d_%H%M%S')}.csv"
    rows = [
        {
            'url': r['url'],
            'status': r['status'],
            'status_code': r.get('status_code', ''),
            'response_time_ms': r.get('response_time', ''),
            'error': r.get('error', ''),
            'timestamp': now.isoformat(),
        }
        for r in results
    ]

    try:
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(rows)
    except OSError as e:
        raise OSError(f"Couldn't write report to '{output_path}': {e}") from e
    return os.path.abspath(output_path)
