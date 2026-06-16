# MasterPC_mock

> MasterPC_ws의 전체 흐름 테스트용 mock 워크스페이스입니다.
> `amr_robot_ws` 없이 독립적으로 실행 가능합니다.

---

## 🚀 실행 데모

<img width="1920" height="1080" alt="output" src="https://github.com/user-attachments/assets/4a1ecc14-7d71-43ed-9472-5b3df92b3967" />

### 터미널 구성 (6분할)

| 위치 | 실행 명령어 | 설명 |
|------|------------|------|
| 상단 좌 | `ros2 run sml_system_pkg mock_nav_node` | [MOCK NAV] navigate_to_station 서버 |
| 상단 중 | `ros2 run sml_system_pkg mock_arm_node` | [MOCK ARM] /amr_robot_command 서버 |
| 상단 우 | `ros2 run sml_system_pkg mock_wb_node` | [MOCK WB] wb_task 서버 |
| 하단 좌 | `ros2 run sml_system_pkg sml_planning_node` | [PLANNING] PlanningNode |
| 하단 중 | `ros2 run sml_system_pkg sml_manager_node` | [MANAGER] sml_manager_node |
| 하단 우 | `ros2 run sml_system_pkg order_node` | [ORDER]order_list 및 arena_layout 설정값 출력 |

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

## 🗂️ 노드 역할

| 노드 | 역할 |
|------|------|
| `sml_planning_node` | Task를 받아 depends_on 기반 스텝 시퀀스 생성 |
| `sml_manager_node` | 스텝을 받아 AMR / WB에 병렬 명령 실행 |
| `sml_order_server` | 테스트용 Task 발행 |

---

## 🔗 통신 구조

```
sml_order_server
      ↓ /sml/task (Topic)
  ┌───┴───────────┐
  ↓               ↓
sml_planning_node  sml_manager_node ─────────────────┐
        ↑_________________↓                          |
         /sml/get_plan (Service)                     |
         매니저가 요청 → planning이 스텝 응답             |
                                                     |
                                          ┌──────────┼──────────┐
                                          ↓          ↓          ↓
                                    amr_nav_node  amr_robot_node  workbench_node
                                    (자율주행팀)    (Manipulation)  (Manipulation)
```

| 구분 | 방식 | 이름 | 설명 |
|------|------|------|------|
| Task 수신 | Topic | `/sml/task` | planning / manager 둘 다 구독 |
| 스텝 전달 | Service | `/sml/get_plan` | manager 요청 → planning 응답 |
| AMR 이동 | Action | `navigate_to_station` | manager → 자율주행팀 |
| AMR 팔 | Service | `/amr_robot_command` | manager → amr_robot_node |
| 워크벤치 | Action | `wb_task` | manager → Manipulation |
| 상태 모니터링 | Topic | `/sml/status` | manager 발행 |

---

## 📨 인터페이스 정의

### NavTask.action (자율주행팀 전달용)

```
# Goal
int32  station_id

---
# Result
bool   success
string fail_reason      # "NAV_FAILED" / "OBSTACLE" / "TIMEOUT"

---
# Feedback
string status           # "MOVING" / "ARRIVED"
```

### WbTask.action (Manipulation 전달용)

```
# Goal
string  work_type       # "PRODUCE" / "RECYCLE"
int32   product_id      # 만들거나 분해할 product_id (예: 13, 81)

---
# Result
bool    success
string  fail_reason

---
# Feedback
string status           # "PROCESSING" / "PRODUCING" / "RECYCLING"
```

### ArmCommand.srv (amr_robot_ws 참고)

```
# Request
string  action          # "LOAD" / "UNLOAD"
int32[] object_ids      # 처리할 물체 ID 리스트

---
# Response
bool    success
int32[] slots
int32[] object_ids
string  message
```

---

## 🚗 AMR 슬롯 구조

| 슬롯 | 용도 |
|------|------|
| 슬롯 1 | 완성품 / 분해 대상 전용 |
| 슬롯 2~6 | 재료 전용 (최대 5개) |

---

## 📋 스텝 구조 (Step.msg)

| 필드 | 타입 | 설명 |
|------|------|------|
| step_id | int32 | 스텝 식별자 |
| type | int32 | AMR=0 / WB=1 |
| action | int32 | LOAD=0 / UNLOAD=1 / PRODUCE=2 / RECYCLE=3 |
| object_ids | int32[] | 재료 또는 완성품 ID |
| station_id | int32 | 실행할 스테이션 ID |
| depends_on | int32[] | 선행 완료되어야 할 step_id 리스트 |

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
