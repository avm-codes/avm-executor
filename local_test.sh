#podman build -t executor .
#podman run -p 9000:8080 executor
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" \
  -H "Content-Type: application/json" \
  -d '{
        "language": "python",
        "code": "print(\"hello world\")"
      }'

echo "\n--------------------------------\n"
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" \
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
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" \
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
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" \
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
