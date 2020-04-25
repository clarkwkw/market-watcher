serverless:
	$(eval SET_WEBHOOK_ADDRESS=$(shell serverless deploy --aws_profile | tee /dev/tty | grep -o "https://.*/set-webhook"))
	curl -X POST $(SET_WEBHOOK_ADDRESS)
lint:
	flake8 market_watch
	mypy --ignore-missing-imports market_watch
clean:
	rm -rf node_modules package-lock.json .serverless