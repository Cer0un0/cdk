import os
from datetime import date

import boto3
import requests
from dateutil.relativedelta import relativedelta

def get_total_cost_date_range():
    today = date.today()
    start_date = today.replace(day=1)  # 範囲の始まり（月初）
    end_date = today  # 範囲の終わり（今日）

    # startとendに同じ日付は指定不可のため、
    # today = 月初なら、「先月月初〜todayの範囲にする
    if start_date == end_date:
        start_date = today + relativedelta(months=-1, day=1)

    return (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))


def lambda_handler(event, context):
    # 変数
    ACCOUNTID = os.environ['ACCOUNT_ID']
    WEBHOOK_URL = os.environ['WEBHOOK_URL']
    BUDGET_NAME = os.environ['BUDGET_NAME']
    USER_NAME = os.environ['USER_NAME']
    AVATAR_URL = os.environ['AVATAR_URL']
    MESSAGE = os.environ['MESSAGE']
    # Budgets
    client = boto3.client("budgets")
    response = client.describe_budget(AccountId=ACCOUNTID, BudgetName=BUDGET_NAME)

    # budget = float(response["Budget"]["BudgetLimit"]["Amount"])  # 予算
    total_cost = float(
        response["Budget"]["CalculatedSpend"]["ActualSpend"]["Amount"]
    )  # 現在までの料金
    forecast_cost = float(
        response["Budget"]["CalculatedSpend"]["ForecastedSpend"]["Amount"]
    )  # 今月の予測料金

    # Cost Explorerから実行月の利用料金を取得
    client = boto3.client("ce")
    (start_date, end_date) = get_total_cost_date_range()
    response = client.get_cost_and_usage(
        TimePeriod={"Start": start_date, "End": end_date},
        Granularity="DAILY",
        Metrics=["AmortizedCost"],
        GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
    )

    # 各サービスの日別料金
    billings = {}
    for rbt in response["ResultsByTime"]:
        day_cost = 0
        for item in rbt["Groups"]:
            service = item["Keys"][0]
            amount = float(item["Metrics"]["AmortizedCost"]["Amount"])
            day_cost += amount

            # 合計料金
            if service in billings:
                billings[service]["amount"] += amount
            else:
                # $0のサービスは無視
                if amount == 0:
                    continue

                billings[service] = {"amount": amount, "diff": 0}

            # Taxは前日比を計算しない
            if service == "Tax":
                continue

            # 前日比の料金を更新
            billings[service]["diff"] = amount

        # Tax
        billings["Tax"]["diff"] = day_cost * 0.1

    # 投稿メッセージ
    content = (
        f"{MESSAGE}\n"
        f"[期間] {start_date} - {end_date}\n"
        f"[料金] ${total_cost:.2f}\n"
        f"[予測] ${forecast_cost:.2f}\n"
        f"\n"
    )

    # 各サービスの料金
    for k, v in billings.items():
        content += f"${v['amount']:.2f} (+${v['diff']:.2f}) {k}\n"

    # Webhook
    data = {
        "username": USER_NAME,
        "avatar_url": AVATAR_URL,
        "content": content,
    }

    # POST
    try:
        requests.post(WEBHOOK_URL, data)
    except requests.exceptions.RequestException as e:
        print(e)


# ローカル用
# lambda_handler(None, None)
