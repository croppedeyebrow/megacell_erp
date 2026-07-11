# ERP_Infra / cloudflare

Cloudflare Tunnel과 Access 운영 설정을 기록합니다.

## 역할 구분

| 계층 | 역할 |
| --- | --- |
| **MegaCell ERP 로그인/회원가입** | 계정·권한의 기준. Argon2id, 세션 쿠키 |
| Cloudflare Tunnel | 사내 PC의 FastAPI/Front를 HTTPS로 노출 |
| Cloudflare Access (선택) | 외곽 네트워크 보호. **ERP 계정을 대체하지 않음** |

직원 계정은 ERP에서 직접 가입·로그인합니다. Access 이메일 허용 목록으로 회원 관리하지 않습니다.

## 현재 운영 주소

```text
https://erp.megacell-erp.com
```

## Tunnel Public Hostname (전환 중)

기존 Streamlit:

```text
Service URL: localhost:8501
```

신규 FastAPI 기준으로 전환 시:

```text
Service URL: localhost:8000
```

(Front 정적 배포 또는 리버스 프록시 구성은 별도)

## Access 정책 (선택)

Access를 유지할 경우에도 ERP 내부 로그인과 별개입니다.  
초기에는 허용된 회사 이메일만 터널에 들어오게 할 수 있습니다.

```text
Action: Allow
Include: Emails / Email domain
```
