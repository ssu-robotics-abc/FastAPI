class ROS2Service:
    """
    TODO: ROS 2 연동을 위한 경계 계층입니다.

    지금은 print 기반 placeholder입니다.
    추후 rclpy publisher 로직을 이 클래스 내부에만 추가하면
    API 라우터와 DB 로직을 건드리지 않아도 됩니다.
    """

    def publish_scan_event(self, product_name: str) -> None:
        print(f"[ROS2] product scan completed: product_name={product_name}")

    def publish_purchase_complete(self, order_id: int, items: dict[str, int]) -> None:
        print(f"[ROS2] purchase completed: order_id={order_id}, items={items}")

    def publish_qr_scan_complete(self, customer_name: str) -> None:
        print(f"[ROS2] QR scan completed: customer_name={customer_name}")


ros2_service = ROS2Service()
