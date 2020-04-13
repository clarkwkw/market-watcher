serverless:
	$(eval SET_WEBHOOK_ADDRESS=$(shell serverless deploy --aws_profile | tee /dev/tty | grep -o "https://.*/set_webhook"))
	curl -X POST $(SET_WEBHOOK_ADDRESS)

clean:
	rm -rf node_modules package-lock.json .serverless