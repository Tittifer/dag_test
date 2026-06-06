# DAG API Test Framework

这是 `dag-docker-sim-java` 的独立接口自动化测试框架，参考了 `pytest + requests + YAML + Allure` 的组织方式。

## 目录说明

```text
base/                  核心用例执行器
common/                配置、请求、断言、日志、YAML、并发工具
conf/config.ini        默认环境配置
testcase/              测试入口和 YAML 用例
report/                测试报告输出
logs/                  运行日志
extract.yaml           跨接口提取变量
```

## 准备被测服务

先启动 Java 项目：

```powershell
cd D:\Java_study\dag_docker_sim_java\dag_docker_sim_java
mvn -s maven-settings.xml spring-boot:run
```

默认测试地址是：

```text
http://localhost:8080
```

可以在 `conf/config.ini` 修改，也可以运行时覆盖：

```powershell
python run.py --base-url http://localhost:8080
```

## 安装依赖

```powershell
pip install -e .
```

如果只跑普通接口测试，核心依赖是 `pytest`、`requests`、`PyYAML`。MySQL 和 Redis 断言默认关闭，需要时在 `conf/config.ini` 打开。

## 运行测试

全部测试：

```powershell
python run.py
```

只跑普通接口：

```powershell
python run.py --mark "api"
```

只跑业务链路：

```powershell
python run.py --mark "business"
```

并发场景单独运行：

```powershell
python run.py --mark "concurrency"
```

生成 Allure 原始结果：

```powershell
python run.py --allure
```

跳过服务健康检查：

```powershell
python run.py --skip-health-check
```

健康检查配置在 `conf/config.ini`：

```ini
[health_check]
enabled = true
path = /api/health
expected_code = 0
timeout = 3
```

## YAML 用例格式

```yaml
- baseInfo:
    api_name: register device
    url: /api/fusions/fusion1/devices/register
    method: POST
    header:
      Content-Type: application/json
  testCase:
    - case_name: register dynamic device successfully
      json:
        deviceName: "${unique_device_name(single-device)}"
        useBootstrapIdentity: false
        autoConfirm: true
      extract:
        deviceId: $.data.device_id
      validation:
        - status_code: 200
        - code: 0
        - message: ok
        - jsonpath_not_empty:
            - $.data.device_id
```

支持 `${get_extract_data(key)}`、`${timestamp()}`、`${uuid()}`、`${random_int(1,100)}`、`${unique_device_name(prefix)}` 等动态参数。

## 外置请求数据

复杂请求体可以放到 `data/payloads`，YAML 中通过 `json_file` 引用，并用 `json_override` 覆盖本条用例的差异字段：

```yaml
- case_name: submit telemetry
  json_file: data/payloads/telemetry_normal.json
  json_override:
    dataPayload:
      device_name: "${get_extract_data(flowDeviceName)}"
      sequence: 2
```

处理顺序是：

```text
读取 json_file -> 替换动态参数 -> 合并 json_override -> 发送请求
```

## 断言能力

常用断言：

```yaml
validation:
  - status_code: 200
  - code: 0
  - message: ok
  - jsonpath_eq:
      $.data.terminal_id: fusion1
  - jsonpath_exists:
      - $.data.summary
  - jsonpath_not_empty:
      - $.data.device_id
  - jsonpath_type:
      $.data.transactions: list
      $.data.summary: dict
  - jsonpath_length:
      $.data: 3
  - jsonpath_min_length:
      $.data.transactions: 1
  - jsonpath_greater_or_equal:
      $.data.simulated_device_count: 0
  - jsonpath_contains:
      $.data.transactions: "${get_extract_data(flowBusinessTxId)}"
  - jsonpath_regex:
      $.data.device_id: ".+"
  - response_time_less_than: 2000
```
