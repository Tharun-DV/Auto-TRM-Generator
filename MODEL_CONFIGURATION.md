# TRM Bot - AI Model Configuration

## Overview
The TRM Bot uses Portkey AI Gateway to connect to various AI models for generating TRM reports. The model is fully configurable via environment variables.

## Default Model
**Claude Sonnet 4.5** (`pilot-poc/claude-sonnet-4-5`)

This model provides:
- ✅ Excellent context understanding
- ✅ Strong structured output generation
- ✅ High-quality summarization
- ✅ Good categorization capabilities

## Configuration

### Setting the Model
```bash
export PORTKEY_MODEL='pilot-poc/claude-sonnet-4-5'
```

### Available Models

#### Anthropic Claude Models
```bash
# Claude Sonnet 4.5 (Default - Recommended)
export PORTKEY_MODEL='pilot-poc/claude-sonnet-4-5'

# Claude 3 Opus (Most capable)
export PORTKEY_MODEL='claude-3-opus-20240229'

# Claude 3 Sonnet (Balanced)
export PORTKEY_MODEL='claude-3-sonnet-20240229'

# Claude 3 Haiku (Fast & efficient)
export PORTKEY_MODEL='claude-3-haiku-20240307'
```

#### OpenAI Models
```bash
# GPT-4o (Latest GPT-4)
export PORTKEY_MODEL='gpt-4o'

# GPT-4 Turbo
export PORTKEY_MODEL='gpt-4-turbo'

# GPT-3.5 Turbo (Faster, cheaper)
export PORTKEY_MODEL='gpt-3.5-turbo'
```

## How It Works

### In the Code (app.py)
```python
# Load model from environment variable with default
PORTKEY_MODEL = os.environ.get("PORTKEY_MODEL", "pilot-poc/claude-sonnet-4-5")

# Used in API call
body = {
    "model": PORTKEY_MODEL,
    "messages": [...]
}
```

### API Request
```json
POST https://api.portkey.ai/v1/chat/completions

Headers:
{
  "x-portkey-api-key": "YOUR_API_KEY",
  "Content-Type": "application/json"
}

Body:
{
  "model": "pilot-poc/claude-sonnet-4-5",
  "messages": [
    {
      "role": "system",
      "content": "You are a DevOps reporting assistant..."
    },
    {
      "role": "user",
      "content": "Generate TRM report from these messages..."
    }
  ]
}
```

## Model Selection Guide

### Choose Claude Sonnet 4.5 (Default) if:
- ✅ You want balanced performance and cost
- ✅ You need high-quality structured output
- ✅ You want consistent, reliable results
- ✅ **Recommended for most users**

### Choose Claude 3 Opus if:
- ✅ You need the most capable model
- ✅ Cost is less of a concern
- ✅ You have complex categorization needs
- ⚠️ Higher cost per request

### Choose GPT-4o if:
- ✅ You prefer OpenAI models
- ✅ You need fast response times
- ✅ You have existing OpenAI workflows

### Choose Claude 3 Haiku if:
- ✅ You need fast responses
- ✅ You have high volume requirements
- ✅ You want to minimize costs
- ⚠️ Slightly lower quality than Sonnet/Opus

### Choose GPT-3.5 Turbo if:
- ✅ You want the lowest cost
- ✅ You have simple TRM requirements
- ⚠️ Lower quality than GPT-4 or Claude 3

## Testing Different Models

### Quick Test
```bash
# Test with Claude Sonnet 4.5 (default)
export PORTKEY_MODEL='pilot-poc/claude-sonnet-4-5'
python app.py
# In Slack: /trm yesterday

# Test with GPT-4o
export PORTKEY_MODEL='gpt-4o'
python app.py
# In Slack: /trm yesterday

# Compare outputs
```

### Performance Comparison Script
```bash
#!/bin/bash
# test_models.sh

models=(
  "pilot-poc/claude-sonnet-4-5"
  "gpt-4o"
  "claude-3-opus-20240229"
)

for model in "${models[@]}"; do
  echo "Testing $model..."
  export PORTKEY_MODEL="$model"
  # Run your test here
  echo "---"
done
```

## Cost Considerations

### Approximate Costs (per 1M tokens)
| Model | Input | Output | Use Case |
|-------|-------|--------|----------|
| Claude Sonnet 4.5 | $3 | $15 | **Default - Best value** |
| Claude 3 Opus | $15 | $75 | Highest quality |
| GPT-4o | $5 | $15 | Fast, reliable |
| Claude 3 Haiku | $0.25 | $1.25 | High volume |
| GPT-3.5 Turbo | $0.50 | $1.50 | Budget option |

*Prices are approximate and may vary. Check Portkey pricing for exact rates.*

### Typical TRM Report Costs
- **Input**: ~5,000 tokens (200 Slack messages)
- **Output**: ~2,000 tokens (formatted TRM report)
- **Cost per report** (Claude Sonnet 4.5): ~$0.045
- **Cost for 100 reports/month**: ~$4.50

## Troubleshooting

### Error: "Model not found"
- Check that the model name is correct
- Verify your Portkey account has access to that model
- Try the default model: `pilot-poc/claude-sonnet-4-5`

### Error: "Rate limit exceeded"
- You've hit Portkey's rate limits
- Wait a few minutes and retry
- Consider upgrading your Portkey plan
- Switch to a faster model (Haiku) for high volume

### Poor Quality Output
- Try Claude Sonnet 4.5 or Opus for better results
- Check that your prompt is clear (in `summarize_with_portkey()`)
- Verify message quality/format from Slack

### Timeout Errors
- Increase timeout in `app.py` (currently 60s)
- Use a faster model (Haiku, GPT-3.5)
- Reduce message count (currently 200 max)

## Advanced Configuration

### Custom Prompt per Model
```python
def summarize_with_portkey(messages: list, start_date: str, end_date: str, week_num: int) -> str:
    # Adjust prompt based on model
    if "gpt" in PORTKEY_MODEL.lower():
        system_prompt = "You are a DevOps TRM assistant. Be concise."
    else:  # Claude models
        system_prompt = "You are a DevOps TRM assistant. Provide detailed analysis."
    
    # ... rest of function
```

### Model-Specific Parameters
```python
body = {
    "model": PORTKEY_MODEL,
    "messages": [...],
    "temperature": 0.3,  # Lower = more consistent
    "max_tokens": 4000,  # Adjust for output length
}
```

## Best Practices

1. **Start with Default**: Use Claude Sonnet 4.5 unless you have specific needs
2. **Test Before Production**: Try different models with sample data
3. **Monitor Costs**: Track API usage in Portkey dashboard
4. **Cache Results**: Save generated reports to avoid regeneration
5. **Set Budgets**: Configure spending limits in Portkey
6. **Version Control**: Document which model works best for your team

## Environment Setup Examples

### Development
```bash
export PORTKEY_MODEL='claude-3-haiku-20240307'  # Fast & cheap for testing
```

### Staging
```bash
export PORTKEY_MODEL='pilot-poc/claude-sonnet-4-5'  # Match production
```

### Production
```bash
export PORTKEY_MODEL='pilot-poc/claude-sonnet-4-5'  # Reliable & balanced
```

## Support

For model-specific issues:
1. Check Portkey AI documentation
2. Review model capabilities (Claude vs GPT)
3. Test with different models
4. Contact Portkey support for access issues

## References

- [Portkey AI Documentation](https://portkey.ai/docs)
- [Anthropic Claude Models](https://www.anthropic.com/claude)
- [OpenAI Models](https://platform.openai.com/docs/models)
- [Model Pricing Comparison](https://portkey.ai/pricing)

---

*Last updated: March 6, 2026*
*Default Model: pilot-poc/claude-sonnet-4-5*
