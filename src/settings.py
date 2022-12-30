from dotenv import dotenv_values

config = dotenv_values("../.env")
vars_length = len(config)

if vars_length == 0:
	raise Exception("Please configure the environment variables first!")