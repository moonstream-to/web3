# from __future__ import print_function
import argparse
import logging
import os

import json
import base64
import time

from brownie.network.account import Account
from brownie import accounts

from typing import Any, cast, Dict, Optional


import requests

from eip712.messages import EIP712Message

from brownie import network
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = "<>SAMPLE_SPREADSHEET_ID<>"
SAMPLE_SHEET_NAME = "<>SHEET_NAME<>"
SAMPLE_RANGE_NAME = f"{SAMPLE_SHEET_NAME}!A2:B"


BUGOUT_ACCESS_TOKEN = os.environ.get("BUGOUT_ACCESS_TOKEN", None)

if BUGOUT_ACCESS_TOKEN is None:
    raise Exception("BUGOUT_ACCESS_TOKEN is not set")


ACCOUNT_SIGNER = os.environ.get("ACCOUNT_SIGNER", None)

if ACCOUNT_SIGNER is None:
    raise Exception("ACCOUNT_SIGNER is not set")


ACCOUNT_SIGNER_PASSWORD = os.environ.get("ACCOUNT_SIGNER_PASSWORD", None)
print(ACCOUNT_SIGNER_PASSWORD)

if ACCOUNT_SIGNER_PASSWORD is None:
    raise Exception("ACCOUNT_SIGNER_PASSWORD is not set")


BUGOUT_QUERY_URL = os.environ.get("BUGOUT_QUERY_URL", None)

if BUGOUT_QUERY_URL is None:
    raise Exception("BUGOUT_QUERY_URL is not set")

AUTH_FILE = os.environ.get("AUTH_FILE", None)

if AUTH_FILE is None:
    raise Exception("AUTH_FILE is not set")


def sync_claimants_state_handler(args: argparse.Namespace) -> None:

    # Google Sheets API way
    # require: google credentials and add service account(his email) to spreadsheet

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            credentials = service_account.Credentials.from_service_account_file(
                AUTH_FILE, scopes=SCOPES
            )

    try:
        service = build("sheets", "v4", credentials=credentials)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = (
            sheet.values()
            .get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME)
            .execute()
        )
        accounts = result.get("values", [])

        # response
        # rows structure: indexes 0 - address, 1 - amount

        if not accounts:
            print("No data found.")
            return

    except HttpError as err:
        print(err)

    # get database data
    try:

        # Moonstream Query API call
        response = requests.post(
            f"{BUGOUT_QUERY_URL}/update_data",
            headers={
                "Authorization": f"Bearer {BUGOUT_ACCESS_TOKEN}",
                "Content-Type": "application/json",
            },
            json={
                "params": {
                    "claim_id": args.claim_id,
                    # addresses filter removed from query now
                    # workable construction `adderess = ANY(:addresses)` (pretty fast bthw)
                    # "addresses": []
                }
            },
            timeout=10,
        ).json()

        # wait S3 upload
        time.sleep(10)

        # get presigned url
        print(response)
        access_link = response["url"]

        # get s3 data
        # {"block_number": 27809982,
        # "block_timestamp": 1651439839,
        # "data": [{
        #
        # }]
        # }
        s3_response = requests.get(access_link, timeout=10)

        print(s3_response.text)

        data = s3_response.json()["data"]

        transformed_data = {}

        for row in data:
            transformed_data[row["address"]] = row

        data = []

        data.append(
            {
                "range": f"""{SAMPLE_SHEET_NAME}!D1:F1""",
                "values": [["database amount", "transaction_hash", "signature"]],
            }
        )

        for index, row in enumerate(accounts):

            # get address from google sheet

            address = row[0]

            if address in transformed_data:
                # get amount from google sheet
                amount = transformed_data[address]["amount"]

                # get amount from database
                transaction_hash = transformed_data[address]["transaction_hash"]

                signature = transformed_data[address]["signature"]

                data.append(
                    {
                        "range": f"""{SAMPLE_SHEET_NAME}!D{index + 2}:F{index + 2}""",
                        "values": [[amount, transaction_hash, signature]],
                    }
                )
                if index % 100 == 0:
                    body = {"valueInputOption": "RAW", "data": data}
                    result = (
                        service.spreadsheets()
                        .values()
                        .batchUpdate(spreadsheetId=SAMPLE_SPREADSHEET_ID, body=body)
                        .execute()
                    )
                    data = []
                    print("{0} cells updated.".format(result.get("totalUpdatedCells")))

        body = {"valueInputOption": "RAW", "data": data}
        result = (
            service.spreadsheets()
            .values()
            .batchUpdate(spreadsheetId=SAMPLE_SPREADSHEET_ID, body=body)
            .execute()
        )
        print("{0} cells updated.".format(result.get("totalUpdatedCells")))
    except Exception as e:
        print(e)


def main():
    parser = argparse.ArgumentParser(
        description="engine: workers for moonstream-engine"
    )
    parser.set_defaults(func=lambda _: parser.print_help())
    subparsers = parser.add_subparsers()

    parser_dropper = subparsers.add_parser("dropper", description="Dropper workers")
    parser_dropper.set_defaults(func=lambda _: parser_dropper.print_help())

    subparsers_dropper = parser_dropper.add_subparsers(description="Dropper workers")

    parser_dropper_claimants_state = subparsers_dropper.add_parser(
        "sync-claimants-state",
        description="Synhcronize claimants transactions from the blockchain and dropper database",
    )
    parser_dropper_claimants_state.add_argument(
        "--claim-id", type=str, required=True, help="Claim ID to sync",
    )
    parser_dropper_claimants_state.add_argument(
        "--db-claim-id", type=str, required=True, help="Claim ID to sync",
    )
    parser_dropper_claimants_state.add_argument(
        "--otput-file",
        type=str,
        required=True,
        help="Output file if start as http then use as google spreadsheet url",
    )
    parser_dropper_claimants_state.add_argument(
        "--network", type=str, required=True, help="Network to use",
    )

    parser_dropper_claimants_state.set_defaults(func=sync_claimants_state_handler)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
