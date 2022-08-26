
# Get AWS costs regularly and post them on Discord.

To manually create a virtualenv on MacOS and Linux:

```
$ python -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

Store the required libraries in the Lambda layer.

```
$ ./pip-install.sh
```

Create configuration file.

```
$ cp .env.template .env
```

Edit .env with your favorite editor.

| variable            | Example                                                                             | Need Change | Note                                                |
|---------------------|-------------------------------------------------------------------------------------|:-----------:|-----------------------------------------------------|
| ACCOUNT_ID          | XXXXXXXXXXXX                                                                        | ✔          | Deployment destination AWS account ID               |
| BUDGET_NAME         | discordBudget                                                                       | -           | Budget name to create                               |
| BUDGET_LIMIT_AMOUNT | 10                                                                                  | -           | "Budget" of Budget to create                        |
| WEBHOOK_URL         | https://discord.com/api/webhooks/xxxxxxxxxxxxxxxxxx/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx | ✔          | Post destination URL (Discord Webhook URL)          |
| TIMEZONE            | Asia/Tokyo                                                                          | -           | Time zone                                           |
| STARTUP_TIME        | 0, 0, *, *, *                                                                       | -           | Lambda start time (UTC)                             |
| USER_NAME           | ハゲおじ                                                                                | -           | Account name to post on Discord (any value is fine) |
| AVATAR_URL          | https://www.jp.square-enix.com/ffvii_remake/fankit/_img/snsicon/ICON_RUDE.jpg       | -           | Account image to post on Discord                    |
| MESSAGE             | タークスのハゲおじだ。AWSよりティファが好きだ…。                                                          | -           | Set if you want a message before the budget result  |


Confirmation of deployment contents.

```
$ cdk synth
$ cdk diff
```

Create a stack if there is no problem.
```
$ cdk deploy
```

Check the deployment result!