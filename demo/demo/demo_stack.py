from constructs import Construct
from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_events as _events,
    aws_events_targets as _targets,
    aws_budgets as _budgets,
)

class DemoStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Defines an AWS Lambda resource
        lambda_demofunc1 = _lambda.Function(
            self, 'demofunc1',
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.from_asset('lambda'),
            handler='demofunc1.lambda_handler',
        )

        rule = _events.Rule(
            self, 'schedule_demofunc1',
            schedule=_events.Schedule.cron(minute="0", hour="0", month="*", week_day="*", year="*"),
        )
        rule.add_target(_targets.LambdaFunction(lambda_demofunc1))

        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_budgets/CfnBudget.html
        budget = _budgets.CfnBudget(
            self, 'demoBudget',
            budget=_budgets.CfnBudget.BudgetDataProperty(
                budget_type='COST',
                time_unit='MONTHLY',

                # the properties below are optional
                budget_limit=_budgets.CfnBudget.SpendProperty(
                    amount=10,
                    unit='USD'
                ),
                budget_name='demoBudget',
            ),
        )
