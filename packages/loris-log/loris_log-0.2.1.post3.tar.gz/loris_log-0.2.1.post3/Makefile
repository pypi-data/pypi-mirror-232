test:
	python -m coverage run -m unittest
	python -m coverage html 

example:
	python example/example.py 

pdoc:
	pdoc ./loris_log/boto3Client.py ./loris_log/customLog.py ./loris_log/ftpClient.py ./loris_log/myException.py -o ./doc

.IPHONY: test, example, pdoc