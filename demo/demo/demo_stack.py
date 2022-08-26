from constructs import Construct
from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_events as _events,
    aws_events_targets as _targets,
    aws_budgets as _budgets,
    aws_iam as _iam,
    Duration,
)

import os
from dotenv import load_dotenv

class DemoStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        load_dotenv()
        ACCOUNT_ID = os.environ['ACCOUNT_ID']
        BUDGET_NAME = os.environ['BUDGET_NAME']
        BUDGET_LIMIT_AMOUNT = int(os.environ['BUDGET_LIMIT_AMOUNT'])
        WEBHOOK_URL = os.environ['WEBHOOK_URL']
        BUDGET_ROLE = os.environ['READ_BUDGET_ROLE']

        # Create requests layer
        layer_requests = _lambda.LayerVersion(
            self, 'requests',
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_8],
            code=_lambda.AssetCode('lambda_layer/requests'),
        )

        # Create pytz layer
        layer_pytz = _lambda.LayerVersion(
            self, 'pytz',
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_8],
            code=_lambda.AssetCode('lambda_layer/pytz'),
        )

        # Create submitBudgetsToDiscord Function
        lambda_demofunc1 = _lambda.Function(
            self, 'submitBudgetsToDiscord',
            runtime = _lambda.Runtime.PYTHON_3_8,
            code = _lambda.Code.from_asset('lambda'),
            handler = 'submitBudgetsToDiscord.lambda_handler',
            environment = {
                'ACCOUNT_ID': ACCOUNT_ID,
                'WEBHOOK_URL': WEBHOOK_URL,
                'BUDGET_NAME': BUDGET_NAME,
            },
            timeout = Duration.seconds(300),
            layers = [layer_requests, layer_pytz],
        )

        # Set "budgets:ViewBudget" pocily to Lambda
        lambda_demofunc1.add_to_role_policy(_iam.PolicyStatement(
            effect = _iam.Effect.ALLOW,
            resources=['*'],
            actions=[
                    'budgets:ViewBudget'
                ],
        ))

        # Create EventBridge rule and set trigger to Lambda
        rule_demofunc1 = _events.Rule(
            self, 'schedule_submitBudgetsToDiscord',
            schedule = _events.Schedule.cron(minute='0', hour='0', month='*', week_day='*', year='*'),
        )
        rule_demofunc1.add_target(_targets.LambdaFunction(lambda_demofunc1))

        # Create a Budget referenced by Lambda
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_budgets/CfnBudget.html
        budget_demo1 = _budgets.CfnBudget(
            self, 'discordBudget',
            budget = _budgets.CfnBudget.BudgetDataProperty(
                budget_type = 'COST',
                time_unit = 'MONTHLY',

                # the properties below are optional
                budget_limit = _budgets.CfnBudget.SpendProperty(
                    amount = BUDGET_LIMIT_AMOUNT,
                    unit = 'USD'
                ),
                budget_name = 'discordBudget',
            ),
        )

