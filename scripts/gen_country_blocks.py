import re
from typing import List
import requests
import argparse
import sys

BANNED_COUNTRY_CODES = [
    "RU",
    "CN",
    "KP"
]
ASN_PARSE = re.compile(r"\/AS(\d+)")


def get_banned_asn_list() -> List[int]:

    output = []

    print("Querying banned countries for ASNs")
    for country in BANNED_COUNTRY_CODES:
        print(f"Querying {country}")
        response = requests.get(f"https://bgp.he.net/country/{country.upper()}", headers={
                                "User-Agent": "AS398057 Config Updater"})

        if response.status_code != 200:
            print(
                f"Failed to get ASN list for {country}. Status code: {response.status_code}")
            continue

        # Parse the ASN list
        for line in response.text.splitlines():
            match = ASN_PARSE.search(line)
            if match:
                output.append(int(match.group(1)))

    # Sort and remove duplicates
    print(f"Found {len(output)} banned ASNs")
    output.sort()
    output = list(dict.fromkeys(output))
    print(f"After deduplication, {len(output)} ASNs remain")

    return output


def main() -> int:
    # Handle program arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--output", help="Output file", type=str, default="blocklists/countries.conf")
    args = ap.parse_args()
    
    # Get a list of banned ASNs
    print("Pulling banned ASN list")
    asn_list = get_banned_asn_list()
    
    # Write bird conf
    print("Writing bird config")
    with open(args.output, "w") as f:
        f.write("# This file is automatically generated by gen_country_blocks.py\n")
        f.write("define BLOCKED_COUNTRY_ASNS = [\n")
        f.write(",\n".join([f"    {asn}" for asn in asn_list]))
        f.write("\n];\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())