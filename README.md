# Market Watcher

[![Build Status](https://travis-ci.com/clarkwkw/market-watcher.svg?branch=master)](https://travis-ci.com/clarkwkw/market-watcher)

This is an application for monitoring products on e-commerce and notifying users when products become available.

## Design

![Sequence diagram](docs/market-watch-sequence.png)

Everything is hosted at AWS Lambda because AWS provides free compute time every month.

Due to the limitation of AWS Lambda where each invocation can only last for 30 seconds at most, the product update process is separated into 3 parts:

1. Crawler workload distributor - retrieves subscribed products from database and enque them to Amazon SQS (message queue)
2. Crawler - triggered by queued products from SQS and retrieve product status from websites. Persists products with updated status and enques notifiable products to another message queue.
3. Notification worker - triggered by queued updated from SQS from #2 and send notification to users who subscribed to them.

## Setup

### Pre-requisite

Please install these before proceding

- Python 3.6
- [Serverless](https://serverless.com/framework/docs/providers/aws/guide/installation/)
- [Docker Desktop](https://www.docker.com/get-started)

### Install dependencies

```bash
python -m venv py36
source py36/bin/activate
pip install -r requirements.txt
pip install -r requirements-test.txt
```

## Lint and Test

```bash
make lint
python -m pytest market_watch
```

## Deployment

### Deploying from local machine to AWS

1. Follow [this guide](https://serverless.com/framework/docs/providers/aws/guide/credentials) to configure your AWS access token and secret access key.
2. Start docker desktop
3. Configure environment variables: `MARKET_WATCH_AWS_REGION_NAME`, `MARKET_WATCH_MONGO_DB_NAME`, `MARKET_WATCH_MONGO_URI`, `MARKET_WATCH_TG_TOKEN`
4. Run `make serverless`
