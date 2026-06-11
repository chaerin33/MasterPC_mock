# MasterPC_mock

> MasterPC_ws의 전체 흐름 테스트용 mock 워크스페이스입니다.
> `amr_robot_ws` 없이 독립적으로 실행 가능합니다.

---

## 📦 패키지 구조

```
MasterPC_mock/src/
  sml_msgs/                  # 공용 메시지 / 서비스 / 액션 패키지
    msg/
      Order.msg
      Station.msg
      Task.msg
      Step.msg
    srv/
      GetPlan.srv
      ArmCommand.srv
    action/
      NavTask.action
      WbTask.action

  sml_system_pkg/
    sml_system_pkg/
      sml_planning_node.py   # 스텝 시퀀스 생성 노드
      sml_manager_node.py    # 실행 관리 노드
      order_server.py        # 테스트용 Task 발행 노드
      mock_nav_node.py       # navigate_to_station mock 서버
      mock_arm_node.py       # /amr_robot_command mock 서버
      mock_wb_node.py        # wb_task mock 서버
```

---

## 🔗 통신 구조

```
order_server
      ↓ /sml/task (Topic)
  ┌───┴───────────┐
  ↓               ↓
sml_planning_node  sml_manager_node
        ↑_________________↓
         /sml/get_plan (Service)

                    sml_manager_node
                          ↓ navigate_to_station (Action)
                    mock_nav_node
                          ↓ /amr_robot_command (Service)
                    mock_arm_node
                          ↓ wb_task (Action)
                    mock_wb_node
```

---

## ▶️ 실행 방법

터미널마다 아래 source를 먼저 실행하세요:

```bash
cd ~/robocup/mock/MasterPC_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
```

**터미널 1 — mock nav**
```bash
ros2 run sml_system_pkg mock_nav_node
```

**터미널 2 — mock arm**
```bash
ros2 run sml_system_pkg mock_arm_node
```

**터미널 3 — mock wb**
```bash
ros2 run sml_system_pkg mock_wb_node
```

**터미널 4 — planning 노드**
```bash
ros2 run sml_system_pkg sml_planning_node
```

**터미널 5 — manager 노드**
```bash
ros2 run sml_system_pkg sml_manager_node
```

**터미널 6 — order server (마지막에 실행)**
```bash
ros2 run sml_system_pkg order_server
```

order_server 실행 후 Tier / Stage를 입력하면 전체 흐름이 시작됩니다.
`[MANAGER] ✅ 모든 스텝 완료!` 로그가 출력되면 정상입니다.

---

## 🔗 연관 저장소

| 저장소 | 설명 |
|--------|------|
| [MasterPC_ws](https://github.com/chaerin33/MasterPC_ws) | 실제 운용 워크스페이스 |
| [MasterPC_mock](https://github.com/chaerin33/MasterPC_mock) | 이 저장소 |
| [amr_robot_ws](https://github.com/chaerin33/amr_robot_ws) | AMR 로봇팔 제어 |
