import json

try:
    import rclpy
    from rclpy.node import Node
    from std_msgs.msg import String
    from abc_interfaces.srv import SttStart
except ModuleNotFoundError:
    rclpy = None
    Node = None
    String = None
    SttStart = None


class ROS2Service:
    def __init__(self):
        """FastAPI와 ROS 2 사이의 발행 브리지입니다.

        ROS 2가 설치되지 않은 일반 프론트/API 개발 환경에서는 noop 모드로 동작해
        FastAPI 앱 import와 HTTP API 조회가 막히지 않게 합니다.
        """
        self.enabled = rclpy is not None
        self.node = None
        self.scan_publisher = None
        self.pick_request_publisher = None
        self.stt_start_client = None

        if not self.enabled:
            print("⚠️ [ROS2] rclpy가 없어 ROS 발행은 비활성화됩니다. HTTP API는 계속 동작합니다.")
            return

        if not rclpy.ok():
            rclpy.init()

        self.node = Node('fastapi_barcode_bridge')
        self.scan_publisher = self.node.create_publisher(String, 'scan_done', 10)
        self.pick_request_publisher = self.node.create_publisher(String, 'pick_request', 10)
        self.stt_start_client = self.node.create_client(SttStart, '/stt_start')

        print("✅ [ROS2] Bridge Node 및 Publisher가 생성되었습니다.")

    def publish_scan_event(self, product_id: str) -> None:
        if not self.enabled:
            print(f"[ROS2 disabled] scan_done: product_id={product_id}")
            return

        msg = String()
        msg.data = product_id
        self.scan_publisher.publish(msg)
        print(f"🚀 [ROS2] Topic 'scan_done'에 product_id={product_id} 발행 완료")

    def publish_pick_request(self, items: dict[str, int]) -> None:
        if not self.enabled:
            print(f"[ROS2 disabled] pick_request: items={items}")
            return

        msg = String()
        msg.data = json.dumps({"items": items}, ensure_ascii=False)
        self.pick_request_publisher.publish(msg)
        print(f"🚀 [ROS2] Topic 'pick_request'에 items={items} 발행 완료")

    def publish_purchase_complete(self, order_id: int, items: dict[str, int]) -> None:
        print(f"[ROS2] purchase completed: order_id={order_id}, items={items}")

    def publish_qr_scan_complete(self, customer_name: str) -> None:
        print(f"[ROS2] QR scan completed: customer_name={customer_name}")

    def start_stt(self, timeout_sec: float = 3.0) -> bool:
        if not self.enabled:
            print("[ROS2 disabled] stt_start: start=True")
            return False

        if not self.stt_start_client.wait_for_service(timeout_sec=timeout_sec):
            print("⚠️ [ROS2] Service '/stt_start'를 찾을 수 없습니다.")
            return False

        request = SttStart.Request()
        request.start = True

        future = self.stt_start_client.call_async(request)
        rclpy.spin_until_future_complete(
            self.node,
            future,
            timeout_sec=timeout_sec,
        )

        if not future.done():
            print("⚠️ [ROS2] Service '/stt_start' 응답 시간 초과")
            return False

        response = future.result()
        success = bool(response and response.success)
        print(f"🚀 [ROS2] Service '/stt_start' 호출 완료: success={success}")
        return success


ros2_service = ROS2Service()
