# 🤖 Robotics ABC Dashboard API

> [!NOTE]  
> 이 문서는 FastAPI 백엔드 서버의 개발 환경 설정, 실행 방법, API 엔드포인트 사용법을 설명합니다.  
> 본 서버는 제품 재고 관리, 바코드/QR 인식 결과 처리, 최종 구매 처리 프로세스를 담당하며 추후 ROS 2 로봇 제어 노드와 통합됩니다.

---

## 1. 개발 환경 설정

본 프로젝트는 `uv` 기반 Python 프로젝트입니다.

`uv`가 설치되어 있지 않다면 아래 문서를 참고해 설치합니다.

> https://docs.astral.sh/uv/getting-started/installation/

### Python 버전 설치

`.python-version` 파일에 정의된 Python 버전을 사용합니다.

```bash
uv python install
```

### 의존성 설치

`pyproject.toml`과 `uv.lock`을 기준으로 프로젝트 의존성을 설치합니다.

```bash
uv sync
```

---

## 2. 데이터베이스 초기화

본 프로젝트는 SQLAlchemy 기반으로 DB를 사용하며, DB 스키마 관리는 Alembic을 통해 수행합니다.

### 테이블 생성

```bash
uv run alembic upgrade head
```

### 초기 상품 데이터 삽입

```bash
uv run python scripts/seed_db.py
```

SQLite DB 파일은 `data/robot_orders.db`에 생성됩니다.

> DB 파일은 개발 중 생성되는 로컬 데이터이므로 Git에 포함하지 않습니다.

---

## 3. 서버 실행

FastAPI 개발 서버를 실행합니다.

```bash
uv run fastapi dev app/main.py --host 0.0.0.0 --port 8000
```

또는 `uvicorn`으로 직접 실행할 수 있습니다.

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

실행 후 브라우저에서 API 문서를 확인할 수 있습니다.

```text
http://localhost:8000/docs
```

같은 네트워크의 다른 기기에서 접속해야 하는 경우 서버 PC의 IP를 확인합니다.

```bash
hostname -I
```

예시:

```text
http://<서버_IP>:8000/docs
```

---

# 로보틱스 스토어 API 연동 가이드

모든 API는 기본적으로 `/api/v1` prefix를 사용합니다.

예시:

```text
/api/v1/stock/{product_name}
/api/v1/scan
/api/v1/purchase
/api/v1/qr_scan_complete
```

---

## 1. 특정 상품 재고 및 바코드 조회

**`GET` `/api/v1/stock/{product_name}`**

해당 상품의 현재 남은 재고 수량과 바코드 정보를 조회합니다.

### Parameters

| 이름 | 위치 | 설명 |
|---|---|---|
| `product_name` | Path | 조회할 상품 이름. 예: `칸초` |

### Response

#### Success - 200 OK

```json
{
  "product_name": "칸초",
  "remaining_stock": 20,
  "barcode_data": "8801062518210"
}
```

#### Error - 404 Not Found

DB에 해당 이름의 상품이 없을 경우 에러를 반환합니다.

```json
{
  "detail": "해당 상품을 찾을 수 없습니다."
}
```

---

## 2. 바코드 스캔 확인 및 ROS 2 신호 전송

**`POST` `/api/v1/scan`**

앱 카메라에서 상품 바코드가 인식되었을 때 호출합니다.

서버는 DB에서 바코드 번호를 상품명으로 변환하여 반환하고, 내부적으로 ROS 2 시스템에 상품 인식 신호를 전달합니다.

> 바코드는 계산 대상이 아니라 식별자이므로 문자열로 전송하는 것을 권장합니다.

### Request Body

```json
{
  "barcode_data": "8801062518210"
}
```

### Response

#### Success - 200 OK

```json
{
  "product_name": "칸초",
  "message": "스캔 완료 신호가 전송되었습니다."
}
```

#### Error - 404 Not Found

DB에 등록되지 않은 바코드일 경우 에러를 반환합니다.

```json
{
  "detail": "등록되지 않은 바코드입니다."
}
```

---

## 3. 구매 처리 및 로봇 동작 명령

**`POST` `/api/v1/purchase`**

구매자가 최종 결제를 확정했을 때 호출합니다.

장바구니에 담긴 여러 상품의 수량을 한 번에 전송받아 다음 작업을 수행합니다.

1. 요청 상품 존재 여부 확인
2. 재고 수량 검증
3. 주문 내역 생성
4. 주문 상품 생성
5. 상품 재고 차감
6. ROS 2 시스템에 구매 완료 및 로봇 동작 신호 전달

### Request Body

`items`는 `"상품명": 구매수량` 형태의 객체로 전송합니다.

```json
{
  "customer_name": "홍길동",
  "items": {
    "칸초": 1,
    "펩시": 2
  }
}
```

### Response

#### Success - 200 OK

```json
{
  "status": "success",
  "order_id": 1,
  "message": "구매 처리가 완료되었습니다. (구매자: 홍길동)"
}
```

#### Error - 400 Bad Request

요청 수량이 현재 재고보다 많을 경우 에러를 반환하고 트랜잭션을 취소합니다.

```json
{
  "detail": "'칸초' 재고가 부족합니다. (현재: 0개)"
}
```

#### Error - 404 Not Found

존재하지 않는 상품이 요청 목록에 포함된 경우 에러를 반환하고 트랜잭션을 취소합니다.

```json
{
  "detail": "'없는상품' 상품을 찾을 수 없습니다."
}
```

---

## 4. 사용자 QR 스캔 완료 신호 전송

**`POST` `/api/v1/qr_scan_complete`**

앱에서 구매자 정보가 담긴 QR 코드 인식이 완료되었을 때 호출합니다.

별도의 DB 처리는 수행하지 않고, 특정 사용자가 QR 스캔을 완료했다는 신호를 ROS 2 시스템으로 전달합니다.

### Request Body

```json
{
  "customer_name": "홍길동"
}
```

### Response

#### Success - 200 OK

```json
{
  "status": "success",
  "message": "[홍길동]님의 QR 스캔 완료 신호가 ROS 2로 전송되었습니다."
}
```

---

## 5. 예시 요청

### 상품 재고 조회

```bash
curl http://localhost:8000/api/v1/stock/칸초
```

### 바코드 스캔

```bash
curl -X POST http://localhost:8000/api/v1/scan \
  -H "Content-Type: application/json" \
  -d '{"barcode_data": "8801062518210"}'
```

### 구매 처리

```bash
curl -X POST http://localhost:8000/api/v1/purchase \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "홍길동",
    "items": {
      "칸초": 1,
      "펩시": 2
    }
  }'
```

### QR 스캔 완료

```bash
curl -X POST http://localhost:8000/api/v1/qr_scan_complete \
  -H "Content-Type: application/json" \
  -d '{"customer_name": "홍길동"}'
```

---

## 6. 프로젝트 구조

```text
app/
├── api/
│   ├── deps.py
│   └── v1/
│       ├── router.py
│       └── endpoints/
│           ├── purchase.py
│           ├── qr.py
│           ├── scan.py
│           └── stock.py
├── core/
│   └── config.py
├── crud/
│   ├── order.py
│   └── product.py
├── db/
│   ├── base.py
│   └── session.py
├── models/
│   ├── order.py
│   └── product.py
├── schemas/
│   ├── order.py
│   ├── product.py
│   └── scan.py
├── services/
│   ├── order_service.py
│   └── ros2_service.py
└── main.py
```