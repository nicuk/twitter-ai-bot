# Meta Llama API Integration Guide

This document explains how to successfully integrate with the Meta Llama API in the Elion trading bot.

## API Configuration

### Environment Variables
```
AI_ACCESS_TOKEN=QcKYEB9n875ZniLkBgfPf4t8eywevB6CpSKVj7pQrtUvQeWN47fzJwjKAbGtQ3ch
AI_API_URL=https://api-user.ai.aitech.io/api/v1/user/products/209/use/chat/completions
AI_MODEL_NAME=Meta-Llama-3.3-70B-Instruct
```

### Key Points
1. The API URL must include `/chat/completions` at the end
2. Use the exact model name: "Meta-Llama-3.3-70B-Instruct"
3. Include the access token in the Authorization header as a Bearer token

## Request Format

### Headers
```python
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
```

### Request Body
```python
data = {
    "messages": [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": prompt}
    ],
    "model": "Meta-Llama-3.3-70B-Instruct",
    "stop": ["<|eot_id|>"],
    "stream": True,
    "stream_options": {"include_usage": True}
}
```

## Handling Streaming Responses

The API returns responses in a streaming format. Each line starts with "data: " followed by a JSON object. Here's how to handle it:

```python
response = requests.post(
    api_base,
    headers=headers,
    json=data,
    stream=True
)

# Success codes can be either 200 or 201
if response.status_code not in [200, 201]:
    print(f"API Error: {response.status_code} - {response.text}")
    return ""

# Handle streaming response
full_response = ""
for line in response.iter_lines():
    if line:
        line = line.decode('utf-8')
        if line.startswith("data: "):
            try:
                json_str = line[6:]  # Remove "data: " prefix
                if json_str == "[DONE]":
                    continue
                
                chunk = json.loads(json_str)
                if "choices" in chunk and chunk["choices"]:
                    delta = chunk["choices"][0].get("delta", {})
                    if "content" in delta:
                        content = delta["content"]
                        print(content, end="", flush=True)
                        full_response += content
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                continue

print("\n")  # Add newline after streaming
return full_response.strip()
```

## Example Response Format

A successful response will look like this:
```json
data: {
    "choices": [{
        "delta": {
            "content": "Hello!",
            "role": "assistant"
        },
        "finish_reason": null,
        "index": 0,
        "logprobs": null
    }],
    "created": 1737141946,
    "id": "dbec2dea-2cd2-4b4d-a11c-144575b0ebab",
    "model": "Meta-Llama-3.3-70B-Instruct",
    "object": "chat.completion.chunk",
    "system_fingerprint": "fastcoe"
}
```

## Common Issues and Solutions

1. **401 Unauthorized Error**
   - Make sure to include `/chat/completions` in the API URL
   - Verify the access token is correct and properly formatted in the Authorization header

2. **Invalid Response Format**
   - Use the messages array format instead of a single prompt
   - Include both system and user messages

3. **Streaming Response Parsing**
   - Handle each line separately
   - Remove "data: " prefix before parsing JSON
   - Check for "[DONE]" message to end streaming
   - Extract content from the delta object in choices array
