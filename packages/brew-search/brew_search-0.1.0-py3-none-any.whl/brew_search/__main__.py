"""
CLI tool for search packages on Homebrew repository by provided keyword.
Results sorted by downloads count (last 90 days).
"""
import argparse
import asyncio
import json
import time
from pathlib import Path

import httpx
from colorama import Fore, Style


def conv_str_to_int(s: str) -> int:
    return int(s.replace(',', ''))


async def get_statistics(force_update: bool) -> dict:
    cache_time = 60 * 60 * 24 * 7  # 1 week
    now = time.time()
    current_path = Path(__file__).parent.absolute()
    statistics_path = current_path / 'statistics.json'
    if not force_update and statistics_path.exists():
        with open(statistics_path, 'r') as f:
            statistics: dict = json.load(f)
        updated = statistics['updated']
        if now - updated < cache_time:
            return statistics

    urls = [
        'https://formulae.brew.sh/api/formula.json',
        'https://formulae.brew.sh/api/cask.json',
        'https://formulae.brew.sh/api/analytics/install-on-request/90d.json',
        'https://formulae.brew.sh/api/analytics/cask-install/homebrew-cask/90d.json',
    ]
    print('Fetching statistics...')
    async with httpx.AsyncClient() as client:
        futures = [client.get(url) for url in urls]
        responses = await asyncio.gather(*futures)
        formulas, casks, stats_formulas, stats_casks = [resp.json() for resp in responses]

    stats_formulas_by_name = {}
    for row in stats_formulas['items']:
        stats_formulas_by_name[row['formula']] = conv_str_to_int(row['count'])

    stats_casks_by_name = {}
    for rows in stats_casks['formulae'].values():
        for row in rows:
            stats_casks_by_name[row['cask']] = conv_str_to_int(row['count'])

    statistics = {
        'updated': now,
        'formulas': {formula['name']: formula for formula in formulas},
        'casks': {cask['token']: cask for cask in casks},
        'stats_formulas': stats_formulas_by_name,
        'stats_casks': stats_casks_by_name,
    }
    with open(statistics_path, 'w') as f:
        json.dump(statistics, f)
    return statistics


def search(
    statistics: dict, term: str, number: int, cask_only: bool, formula_only: bool,
) -> None:
    formulas = statistics['formulas']
    casks = statistics['casks']
    stats_formulas = statistics['stats_formulas']
    stats_casks = statistics['stats_casks']

    results = []

    if not cask_only:
        for name, formula in formulas.items():
            full_name = formula['full_name']
            desc = formula['desc']
            if term in name.lower() or term in desc.lower():
                results.append({
                    'name': name,
                    'full_name': full_name,
                    'desc': desc,
                    'cask': False,
                    'count': stats_formulas.get(name, 0),
                })
    if not formula_only:
        for name, cask in casks.items():
            full_name = cask['full_token']
            desc = cask['desc'] or ''
            if term in name.lower() or term in desc.lower():
                results.append({
                    'name': name,
                    'full_name': full_name,
                    'desc': desc,
                    'cask': True,
                    'count': stats_casks.get(name, 0),
                })

    results.sort(key=lambda x: x['count'], reverse=True)

    max_count = results[0]['count'] if results else 0
    count_len = len(str(max_count))
    for result in results[:number]:
        name = result['name']
        desc = result['desc']
        count = result['count']
        cask = result['cask']
        if cask:
            print(f'{count:{count_len}d} {Fore.GREEN}{name}{Style.RESET_ALL} - {desc}')
        else:
            print(f'{count:{count_len}d} {Fore.BLUE}{name}{Style.RESET_ALL} - {desc}')


async def main() -> None:
    parser = argparse.ArgumentParser(
        'brew-search',
        description='CLI tool for search packages on Homebrew repository by provided keyword.',
    )
    parser.add_argument('term', help='search term')
    parser.add_argument('--number', '-n', type=int, default=30, help='number of results')
    parser.add_argument('--cask', '-c', action='store_true', help='search casks only')
    parser.add_argument('--formula', '-f', action='store_true', help='search formulas only')
    parser.add_argument('--update', action='store_true', help='force update statistics')
    args = parser.parse_args()

    if args.cask and args.formula:
        print('Cannot specify both --cask and --formula')
        return

    stats = await get_statistics(force_update=args.update)

    search(
        stats,
        term=args.term.lower(),
        number=args.number,
        cask_only=args.cask,
        formula_only=args.formula,
    )


def cli() -> None:
    asyncio.run(main())


if __name__ == '__main__':
    cli()
