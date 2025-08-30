# AVM Execution Engine

**API-based Code Execution for AI Agents**

AVM (Agents Virtual Machine) is a decentralized platform designed specifically for AI Agents code execution. This API-based execution engine provides secure, isolated, and scalable code interpretation capabilities using a VM library.

## 🚀 Features

- **Multi-language Support**: Execute Python, TypeScript, and PHP code
- **API-based**: REST API for code execution
- **VM Library**: Uses VM library for code execution
- **Input/Output Handling**: Support for structured data input and output
- **Real-time Processing**: Fast code interpretation and execution
- **Cloud-Ready**: Designed for deployment in any cloud infrastructure

## 🏗️ Architecture

The AVM execution engine runs as a Flask API server that uses a VM library for code execution. This allows you to:

- Deploy on your own cloud infrastructure
- Maintain full control over your code execution environment
- Scale horizontally based on demand
- Integrate seamlessly with existing API-based workflows

## 🛠️ Quick Start

### Using Docker

1. **Build the container:**

   ```bash
   docker build -t avm-executor .
   ```

2. **Run the container:**

   ```bash
   docker run -p 8080:8080 avm-executor
   ```

3. **Test the execution engine:**
   ```bash
   curl -XPOST "http://localhost:8080/execute" \
     -H "Content-Type: application/json" \
     -d '{
           "language": "python",
           "code": "print(\"Hello, AVM!\")"
         }'
   ```

### Using Podman or Docker

```bash
podman build -t avm-executor .
podman run -p 9000:8080 avm-executor
```

```bash
docker build -t avm-executor .
docker run -p 9000:8080 avm-executor
```

## 📖 API Usage

### Basic Code Execution

Execute simple code without input:

```bash
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" \
  -H "Content-Type: application/json" \
  -d '{
        "language": "python",
        "code": "print(\"hello world\")"
      }'
```

### Code Execution with Input Variables

Pass input data to your code:

```bash
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
```

### Structured Output

Generate structured output from your code:

```bash
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
```

### Code Execution with Environment Variables

Pass environment variables to your code:

```bash
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
```

## 🌐 Supported Languages

- **Python**: Full Python runtime with standard library
- **TypeScript**: Node.js-based TypeScript execution
- **PHP**: Complete PHP interpreter

## 📋 API Reference

### Request Format

```json
{
  "language": "python|typescript|php",
  "code": "your_code_here",
  "input": {
    "key": "value"
  },
  "env": {
    "key": "value"
  }
}
```

### Parameters

- `language` (required): The programming language to execute
- `code` (required): The source code to execute
- `input` (optional): Input variables available to the code
- `env` (optional): Environment variables available to the code

### Response Format

The response contains the execution results, including any output, return values, or errors generated during code execution.

## 🔧 Configuration

The execution engine is designed to work out-of-the-box with minimal configuration. For production deployments, consider:

- Resource limits and quotas
- Network security and isolation
- Logging and monitoring
- Auto-scaling policies

## 🌟 Use Cases

- **AI Agent Code Execution**: Enable AI agents to execute code dynamically
- **Serverless Functions**: Deploy custom serverless functions
- **Code Sandboxing**: Safely execute untrusted code
- **Educational Platforms**: Provide code execution environments for learning
- **API Backends**: Create dynamic API endpoints with code execution

## 🔗 Resources

- **Official Website**: [avm.codes](https://avm.codes)
- **Documentation**: [docs.avm.codes](https://docs.avm.codes)
- **Managed Platform**: [platform.avm.codes](https://platform.avm.codes)

## ⚡ No Infrastructure Setup?

Don't want to manage your own infrastructure? Sign up for our managed platform at [platform.avm.codes](https://platform.avm.codes) and start executing code immediately without any setup.

## 🤝 Contributing

We welcome contributions to the AVM execution engine! Please visit our documentation for contribution guidelines and development setup instructions.

## 📄 License

This project is part of the AVM ecosystem. Please refer to the license file for usage terms and conditions.

---

**Ready to get started?** Visit [docs.avm.codes](https://docs.avm.codes) for comprehensive documentation and tutorials.
