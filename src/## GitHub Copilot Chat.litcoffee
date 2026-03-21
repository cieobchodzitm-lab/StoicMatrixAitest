## GitHub Copilot Chat

- Extension: 0.39.0 (prod)
- VS Code: 1.111.0 (ce099c1ed25d9eb3076c11e4a280f3eb52b4fbeb)
- OS: win32 10.0.19045 x64
- GitHub Account: cieobchodzitm-lab

## Network

User Settings:
```json
  "http.systemCertificatesNode": true,
  "github.copilot.advanced.debug.useElectronFetcher": true,
  "github.copilot.advanced.debug.useNodeFetcher": false,
  "github.copilot.advanced.debug.useNodeFetchFetcher": true
```

Connecting to https://api.github.com:
- DNS ipv4 Lookup: 140.82.121.6 (28 ms)
- DNS ipv6 Lookup: Error (45 ms): getaddrinfo ENOTFOUND api.github.com
- Proxy URL: http://45.76.123.45:7700 (1 ms)
- Proxy Connection: timed out after 10 seconds
- Electron fetch (configured): Error (8008 ms): Error: net::ERR_TIMED_OUT
	at SimpleURLLoaderWrapper.<anonymous> (node:electron/js2c/utility_init:2:10684)
	at SimpleURLLoaderWrapper.emit (node:events:519:28)
	at SimpleURLLoaderWrapper.callbackTrampoline (node:internal/async_hooks:130:17)
  [object Object]
  {"is_request_error":true,"network_process_crashed":false}
- Node.js https: timed out after 10 seconds
- Node.js fetch:
