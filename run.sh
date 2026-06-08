#!/usr/bin/env bash
# FastAPI 서버를 ROS 2(Humble) 환경과 함께 실행합니다.
# rclpy는 시스템 Python 3.10에만 빌드되어 있으므로 .venv도 3.10이어야 하며,
# 아래 source 순서를 거쳐야 ros2_service가 실제로 토픽을 발행합니다.
set -e

cd "$(dirname "$0")"

source /opt/ros/humble/setup.bash
source /home/ssu/doosan_project/team_abc_ws/install/setup.bash
source .venv/bin/activate

# 로봇 노드와 동일한 도메인이어야 통신됩니다.
export ROS_DOMAIN_ID="${ROS_DOMAIN_ID:-26}"

exec uvicorn app.main:app --host 0.0.0.0 --port 8000 "$@"
