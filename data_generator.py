"""
Command-line interface (CLI) for the ride-hailing data generator.
"""

import argparse

from generator.modes import generate, historical, eventhub


def _build_parser():
    parser = argparse.ArgumentParser(
        description="...",
    )
    subparsers = parser.add_subparsers(
        dest = "command",
        metavar = "MODE"
    )

    # --- generate ---
    parser_generate = subparsers.add_parser(
        "generate", 
        help = 'Generates ride records based on CLI arguments and prints them as JSON.'
    )
    parser_generate.add_argument(
        "--count", type = int, default = 1, metavar = "N",
        help = "Number of records to generate (default: 1)."
    )
    parser_generate.add_argument(
        "--debug",
        action = "store_true",
        default = False,
        help = "Enable debug logs for geocoding."
    )

    # --- historical ---
    parser_historical = subparsers.add_parser(
        "historical", 
        help = 'Create ride record'
    )
    parser_historical.add_argument(
        "--count", type = int, default = 1, metavar = "N",
        help = "Number of records to generate (default: 1)."
    )
    parser_historical.add_argument(
        "--format", choices = ["json", "csv"],
        required = True,
        help = "Output format: json , csv"
    )
    parser_historical.add_argument(
        "--duration",
        metavar = "START:END",
        required = True,
        help = "Date range for generated timestamps. Format: YYYY-MM-DD:YYYY-MM-DD (e.g. 2024-01-01:2025-01-01)."
    )
    parser_historical.add_argument(
        "--driver-pool",
        metavar = "PATH",
        default = None,
        help = "Path to a pre-generated driver pool JSON file. If omitted, builds pool in memory."
    )
    parser_historical.add_argument(
        "--customer-pool",
        metavar = "PATH",
        default = None,
        help = "Path to a pre-generated customer pool JSON file. If omitted, builds pool in memory."
    )

    # --- eventhub ---
    parser_eventhub = subparsers.add_parser(
        "eventhub",
        help="Send ride records to Azure Event Hub."
    )
    parser_eventhub.add_argument(
        "--mode", choices=["single", "stream"],
        required=True,
        help="single: send one record. stream: send continuously."
    )
    parser_eventhub.add_argument(
        "--interval", type=float, default=1.0,
        help="Seconds between sends in stream mode (default: 1.0)."
    )
    parser_eventhub.add_argument(
        "--count", type=int, default=0, metavar="N",
        help="Number of records to stream. 0 means run until Ctrl+C (default: 0)."
    )
    parser_eventhub.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Enable debug logs for geocoding."
    )

    return parser


def main():
    parser = _build_parser()
    args = parser.parse_args()

    _command_map = {
        "generate"  : generate.run,
        "historical": historical.run,
        "eventhub"  : eventhub.run,
    }
    _command_map[args.command](args)

if __name__ == "__main__":
    main()
