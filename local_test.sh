#podman build -t executor .
#podman run -p 9000:8080 executor

# set the base url
BASE_URL="http://localhost:9000/2015-03-31/functions/function/invocations"

# TypeScript: Simple console.log
curl -XPOST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
        "language": "typescript",
        "code": "console.log(\"hello world\")"
      }'

echo "\n--------------------------------\n"

# TypeScript: Returning an object via output variable
curl -XPOST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
        "language": "typescript",
        "code": "const output = {result: 42};"
      }'

echo "\n--------------------------------\n"

# TypeScript: Using input variables
curl -XPOST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
        "language": "typescript",
        "input": {"a": 5, "b": 7},
        "code": "const output = {sum: a + b};"
      }'

echo "\n--------------------------------\n"

# TypeScript: Using environment variables
curl -XPOST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
        "language": "typescript",
        "env": {"SECRET": "shh"},
        "code": "const output = {envSecret: process.env.SECRET};"
      }'

echo "\n--------------------------------\n"

# TypeScript: Importing a standard library (fs)
curl -XPOST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
        "language": "typescript",
        "code": "import * as fs from \"fs\"; const output = {tmpExists: fs.existsSync(\"/tmp\")};"
      }'

echo "\n--------------------------------\n"

# TypeScript: Error case (invalid code)
curl -XPOST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
        "language": "typescript",
        "code": "const output = {broken: doesNotExist(1, 2)};"
      }'

echo "\n--------------------------------\n"

curl -XPOST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
        "language": "python",
        "input": {
            "a": 1,
            "b": 2
        },
        "code": "print(a + b)"
      }'

echo "\n--------------------------------\n"
curl -XPOST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
        "language": "python",
        "input": {
            "a": 1,
            "b": 2
        },
        "code": "output = {\"result\": a + b}"
      }'


echo "\n--------------------------------\n"
curl -XPOST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
        "language": "python",
        "input": {
            "a": 1,
            "b": 2
        },
        "env": {
            "c": "4"
        },
        "code": "output = {\"result\": a + b + int(os.environ[\"c\"])}"
      }'
