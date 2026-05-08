# 개발 환경 설정 및 서버 실행

> [!NOTE]  
> 이 문서는 FastAPI 백엔드 서버의 엔드포인트 기능과 사용법을 설명합니다. 본 서버는 제품의 재고 관리, 바코드 인식 결과 처리, 그리고 최종 구매(결제) 프로세스를 담당하며 추후 ROS 2 로봇 제어 노드와 통합됩니다.


## 1. 개발 환경 설정

본 프로젝트는 `uv` 기반 Python 프로젝트로 uv가 설치되어있지 않다면, 아래 링크를 통해 설치해주시기 바랍니다
> https://docs.astral.sh/uv/getting-started/installation/


### python version
`.python-version` 파일에 정의된 Python 버전을 사용합니다.
```bash
uv python install
```

### 의존성 라이브러리 설치

`pyproject.toml`과 `uv.lock`을 기준으로 프로젝트 의존성을 설치합니다.

```bash
uv sync
```



---  

  

## 2. 서버 실행

FastAPI 개발 서버를 실행합니다.

```bash
fastapi dev --host 0.0.0.0 --port 8000
```


실행 후 브라우저에서 API 문서를 확인할 수 있습니다.

```text
http://localhost:8000/docs
```


같은 네트워크의 다른 기기에서 접속해야 하는 경우 서버 PC의 IP를 확인합니다.

```bash
hostname -I
```

---

# 🤖 로보틱스 스토어 API 연동 가이드

이 문서는 FastAPI 백엔드 서버의 엔드포인트 기능과 사용법을 설명합니다. 본 서버는 제품의 재고 관리, 바코드/QR 인식 결과 처리, 그리고 최종 구매(결제) 프로세스를 담당하며 추후 ROS 2 로봇 제어 노드와 통합됩니다.

---

## 1. 특정 상품 재고 및 바코드 조회
**`GET` /stock/{product_name}**

해당 상품의 현재 남은 재고(수량)와 바코드 정보를 확인합니다.

* **Parameters:**
    * `product_name` (Path) : 조회할 상품의 이름 (예: `칸초`)
* **Response (Success - 200 OK):**
    ```json
    {
      "product_name": "칸초",
      "remaining_stock": 20,
      "barcode_data": 8801062518210
    }
    ```
* **Response (Error - 404):** 해당 이름의 상품이 DB에 없을 경우 에러를 반환합니다.

---

## 2. 바코드 스캔 확인 및 ROS 2 신호 전송
**`POST` /scan**

앱 카메라에서 상품 바코드(정수형 숫자)가 인식되었을 때 호출합니다. DB에서 바코드 번호를 상품명으로 변환하여 반환하며, 내부적으로 로봇(ROS 2)에게 해당 상품을 인식했다는 신호를 보냅니다.

* **Request Body (JSON):**
    ```json
    {
      "barcode_data": 8801062518210
    }
    ```
* **Response (Success - 200 OK):**
    ```json
    {
      "product_name": "칸초",
      "message": "스캔 완료 신호가 전송되었습니다."
    }
    ```
* **Response (Error - 404):** DB에 등록되지 않은 바코드일 경우 에러를 반환합니다.

---

## 3. 구매 처리 (장바구니 결제) 및 로봇 동작 명령
**`POST` /purchase**

구매자가 최종 결제를 확정했을 때 호출합니다. 장바구니에 담긴 여러 상품의 수량을 한 번에 전송받아 재고를 차감하고, 주문 내역(DB)을 생성한 뒤, 로봇(ROS 2)에게 픽업 동작을 시작하라는 최종 명령 신호를 보냅니다.

* **Request Body (JSON):**
    * `items`는 `"상품명": 구매수량` 형태의 딕셔너리로 전송합니다.
    ```json
    {
      "customer_name": "홍길동",
      "items": {
        "칸초": 1,
        "펩시": 2
      }
    }
    ```
* **Response (Success - 200 OK):**
    ```json
    {
      "status": "success",
      "order_id": 1,
      "message": "구매 처리가 완료되었습니다. (구매자: 홍길동)"
    }
    ```
* **Response (Error - 400/404):** 존재하지 않는 상품이 목록에 있거나, 재고보다 많은 수량을 요청했을 경우 트랜잭션을 취소하고 에러를 반환합니다.

---

## 4. [NEW] 사용자 QR 스캔 완료 신호 전송
**`POST` /qr_scan_complete**

앱에서 구매자 정보가 담긴 QR 코드가 인식 완료되었을 때 호출합니다. DB 처리를 생략하고, 특정 사용자가 스캔을 완료했다는 신호를 ROS 2 시스템으로 즉각 전송합니다.

* **Request Body (JSON):**
    ```json
    {
      "customer_name": "홍길동"
    }
    ```
* **Response (Success - 200 OK):**
    ```json
    {
      "status": "success",
      "message": "[홍길동]님의 QR 스캔 완료 신호가 ROS 2로 전송되었습니다."
    }
    ```

---
* 문서 버전: v1.4.1
* 통합 상태: ROS 2 통신 로직 뼈대 포함 (상품 스캔, 구매 완료, 구매자 QR 스캔)