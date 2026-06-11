"""
mock_arm_node.py
/amr_robot_command Service 서버 mock.
LOAD / UNLOAD 요청을 받아 즉시 success=True 반환.
"""

import rclpy
from rclpy.node import Node
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor

from sml_msgs.srv import ArmCommand


class MockArmNode(Node):

    def __init__(self):
        super().__init__('mock_arm_node')
        self.cbg = ReentrantCallbackGroup()

        self._srv = self.create_service(
            ArmCommand,
            '/amr_robot_command',
            self._handle_request,
            callback_group=self.cbg,
        )
        # 슬롯 상태 시뮬레이션 (slot 1~6)
        self._slots = list(range(1, 7))
        self._loaded = {}  # object_id → slot_num

        self.get_logger().info('[MOCK ARM] /amr_robot_command 서버 시작')

    def _handle_request(self, request, response):
        action = request.action.upper()
        objects = list(request.object_ids)
        self.get_logger().info(
            f'[MOCK ARM] {action} 요청: objects={objects}')

        if action == 'LOAD':
            used_slots = []
            for obj in objects:
                if self._slots:
                    slot = self._slots.pop(0)
                    self._loaded[obj] = slot
                    used_slots.append(slot)
                else:
                    response.success = False
                    response.message = f'슬롯 부족: object {obj} 적재 불가'
                    response.slots = []
                    self.get_logger().warn('[MOCK ARM] LOAD 실패 — 슬롯 없음')
                    return response
            response.success = True
            response.message = ''
            response.slots = used_slots
            self.get_logger().info(
                f'[MOCK ARM] LOAD 완료: slots={used_slots}')

        elif action == 'UNLOAD':
            freed_slots = []
            for obj in objects:
                slot = self._loaded.pop(obj, None)
                if slot is not None:
                    self._slots.append(slot)
                    freed_slots.append(slot)
            response.success = True
            response.message = ''
            response.slots = freed_slots
            self.get_logger().info(
                f'[MOCK ARM] UNLOAD 완료: freed_slots={freed_slots}')

        else:
            response.success = False
            response.message = f'알 수 없는 action: {action}'
            response.slots = []

        return response


def main(args=None):
    rclpy.init(args=args)
    node = MockArmNode()
    executor = MultiThreadedExecutor(num_threads=4)
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
