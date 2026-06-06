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

