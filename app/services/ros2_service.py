import rclpy
from rclpy.node import Node
from std_msgs.msg import String 

class ROS2Service:
    def __init__(self):
        """
        클래스 생성 시 ROS 2 노드와 Publisher를 초기화합니다.
        """
        # rclpy.init()이 되어있는지 확인 후 초기화
        if not rclpy.ok():
            rclpy.init()
            
        # FastAPI용 ROS 2 노드 생성
        self.node = Node('fastapi_barcode_bridge')
        
        # 'scan_done' 토픽으로 Int32 타입 메시지를 보내는 Publisher 생성
        self.scan_publisher = self.node.create_publisher(String, 'scan_done', 10)
        
        print("✅ [ROS2] Bridge Node 및 'scan_done' Publisher가 생성되었습니다.")

    def publish_scan_event(self, product_id: str) -> None:
        """
        스캔 완료된 상품의 ID를 'scan_done' 토픽으로 발행합니다.
        """
        msg = String()
        msg.data = product_id
        
        # 실제 메시지 발행
        self.scan_publisher.publish(msg)
        
        print(f"🚀 [ROS2] Topic 'scan_done'에 product_id={product_id} 발행 완료")

    def publish_purchase_complete(self, order_id: int, items: dict[str, int]) -> None:
        # 필요 시 Int32나 String 등으로 구현 가능
        print(f"[ROS2] purchase completed: order_id={order_id}, items={items}")

    def publish_qr_scan_complete(self, customer_name: str) -> None:
        print(f"[ROS2] QR scan completed: customer_name={customer_name}")

# 전역 객체 생성
ros2_service = ROS2Service()