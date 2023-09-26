from azEnvJson import convert

with open("test.json") as f:
    print(convert.toEnv(f))