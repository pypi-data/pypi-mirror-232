from azEnvJson import convert

with open("test.env") as f:
    print(convert.toJson(f))