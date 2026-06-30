# infra/cloudflare

Cloudflare Tunnel과 Access 운영 설정을 기록합니다.

## 현재 운영 주소

```text
https://erp.megacell-erp.com
```

## Tunnel Public Hostname

```text
Subdomain: erp
Domain: megacell-erp.com
Path: blank
Service type: HTTP
Service URL: localhost:8501
```

외부 접속은 HTTPS로 제공되지만, 터널이 바라보는 로컬 Streamlit 서버는 HTTP `localhost:8501`입니다.

## Access 정책

초기 운영은 허용된 이메일만 접근하는 방식입니다.

```text
Action: Allow
Include: Emails
Identity provider: One-time PIN
```

직원 전체로 확장할 때는 `megacell.or.kr` 이메일 도메인 허용을 검토합니다.
