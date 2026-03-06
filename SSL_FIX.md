# SSL Certificate Issues - Quick Fix

## Problem
You're seeing this error:
```
ssl.SSLCertVerificationError: [SSL: CERTIFICATE_VERIFY_FAILED] 
certificate verify failed: self-signed certificate in certificate chain
```

## Cause
Your corporate network uses a proxy with self-signed SSL certificates (SSL interception).

## Solution

### Option 1: Disable SSL Verification (Quick Fix for Corporate Networks)

```bash
export DISABLE_SSL_VERIFY=1
python app.py
```

Or add to your environment:
```bash
# In your .env or shell profile
export SLACK_BOT_TOKEN='xoxb-your-token'
export SLACK_APP_TOKEN='xapp-your-token'
export PORTKEY_API_KEY='your-portkey-key'
export DISABLE_SSL_VERIFY=1  # Add this line

python app.py
```

You'll see a warning:
```
⚠️  WARNING: Running with SSL verification disabled!
```

This is expected and safe for corporate networks with SSL interception.

### Option 2: Use the Alternative Script

There's also `app_no_ssl_verify.py` (older version without TRM features):
```bash
python app_no_ssl_verify.py
```

But we recommend using Option 1 above to get all the latest TRM features.

## Security Note

⚠️ **WARNING**: Disabling SSL verification should only be done in corporate environments with SSL interception proxies. Do NOT disable SSL verification when:
- Running in production on public internet
- Handling sensitive data outside corporate network
- Deploying to cloud servers

The `DISABLE_SSL_VERIFY=1` flag affects:
- Slack API connections
- Portkey AI API connections

## Testing

Test that it works:
```bash
export DISABLE_SSL_VERIFY=1
python app.py
```

You should see:
```
⚠️  WARNING: Running with SSL verification disabled!
⚡️ Slack TRM Bot is starting...
✅ Bot is running! Use /trm in your Slack workspace.
```

Then test in Slack:
```
/trm yesterday
```

## When You Don't Need This

If you're running the bot:
- On your local machine with direct internet access
- On a cloud server (AWS, GCP, Azure)
- In Docker without a corporate proxy

Then you should NOT set `DISABLE_SSL_VERIFY=1`. The bot will work with normal SSL verification.

## Troubleshooting

### Still getting SSL errors?
1. Check if you need to configure HTTP_PROXY and HTTPS_PROXY:
   ```bash
   export HTTP_PROXY=http://proxy.company.com:8080
   export HTTPS_PROXY=http://proxy.company.com:8080
   export DISABLE_SSL_VERIFY=1
   ```

2. Check your company's internal documentation for proxy settings

### Other SSL errors?
If you see different SSL errors, try:
```bash
# Install/update certificates
pip install --upgrade certifi

# or
brew install ca-certificates  # macOS
```

## Alternative: Install Corporate CA Certificate

If you want to keep SSL verification enabled, you can install your corporate CA certificate:

1. Get your company's root CA certificate (usually a .crt or .pem file)
2. Add it to certifi:
   ```bash
   # Find certifi location
   python -c "import certifi; print(certifi.where())"
   
   # Append your company cert
   cat /path/to/company-ca.crt >> $(python -c "import certifi; print(certifi.where())")
   ```

3. Run the bot without DISABLE_SSL_VERIFY

## Summary

**For most corporate users behind a proxy:**
```bash
export DISABLE_SSL_VERIFY=1
python app.py
```

**For users with direct internet access:**
```bash
# Don't set DISABLE_SSL_VERIFY
python app.py
```

---

*Last updated: March 6, 2026*
