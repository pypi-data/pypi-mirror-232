# -*- coding: utf-8 -*-
import ast
import inspect
import re
import pytest
import importlib
import requests

pytest_plugins = 'pytester'


def pytest_addoption(parser):
    group = parser.getgroup('collectinfo')
    group.addoption(
        '--collectinfo',
        action='store',
        default=None,
        help='收集用例消息发送到后台服务'
    )
    parser.addini('HELLO', 'Dummy pytest.ini setting')


module_name = "interface"  # 要引入的模块的名称
interface = importlib.import_module(module_name)

task_id = None
report_id = None
ctc_host = "http://10.10.150.42:8888/"
cover_host = f"{ctc_host}api/v1/cover"
# 添加Api任务
AddAPiTask = f"{cover_host}/apiTask"


# 关闭收集任务
def generate_api_close_task_url(task_id):
    return f"{cover_host}/task/{task_id}/collect"


# 获取Api任务报告
def generate_api_task_report_url(task_id):
    return f"{cover_host}/task/{task_id}/apiReport"


# 收集Api任务报告
def generate_collect_api_task_report_url(task_id, report_id):
    return f"{cover_host}/task/{task_id}/apiReport/{report_id}/collect"


def get_interface_info(source_code):
    # 使用正则表达式匹配赋值语句并提取method的静态值
    # 通用性不佳，格式不一定是这样的，有待优化
    # 获取host值
    with open("interface.py", "r") as file:
        content = file.read()
        # 使用正则表达式搜索host值
        pattern = r'host\s*=\s*"([^"]+)"'
        matches = re.search(pattern, content)
        # 提取引号中间的值
        if matches:
            host_value = matches.group(1)
        else:
            print("未找到host值")

    # 获取接口函数的静态值
    match = re.search(r'\.\s*(.+)', source_code)
    if match:
        method_static_value = match.group(1).strip()
        function = getattr(interface, method_static_value)
        source_code = inspect.getsource(function)
        # 使用正则表达式获取接口地址
        # 解析源代码为抽象语法树
        tree = ast.parse(source_code)
        # 查找赋值语句中的 URL
        for node in ast.walk(tree):
            # 在遍历的每个节点中，检查是否是一个赋值语句。如果是赋值语句，进入下一层循环
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    # 检查赋值语句的目标是否是一个名字节点，且名字为 url
                    if isinstance(target, ast.Name) and target.id == "url":
                        # 检查赋值语句的值是否是一个字符串节点
                        if isinstance(node.value, ast.BinOp) and isinstance(node.value.op, ast.Add):
                            # 检查二元操作的左侧是否是变量名"host"，右侧是否是字符串（ast.Str类型）
                            if isinstance(node.value.left, ast.Name) and node.value.left.id == "host" and isinstance(
                                    node.value.right, ast.Str):
                                url = host_value + node.value.right.s  # type: ignore
                                return url
    else:
        print("Unable to find the static value of method")
        return None


# @pytest.hookimpl
def pytest_sessionstart(session):
    print("session start")
    # 使用 global 关键字标识 task_id 为全局变量
    global task_id
    data = {"ProjectId": 1, "ServerName": "mfd-server", "Branch": "release/2.8.1"}
    # 添加api任务
    r = requests.post(AddAPiTask,
                      json=data,
                      headers={"Content-Type": "application/json"})
    result = r.json()
    task_id = result['data']['taskId']
    return task_id


# pytest.hookimpl 装饰器来注册钩子函数，并且使用 hookwrapper=True 来指示这是一个包装器钩子，允许在测试用例运行前后执行额外的代码。
# yield 语句允许测试用例正常执行，然后在其前后执行自定义代码
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_protocol(item):
    # 在测试用例执行之前执行的代码
    # start_time = datetime.fromtimestamp(time.time())
    # print(f"Start execution of '{item.name}' at {start_time}")
    global report_id
    source_code = inspect.getsource(item.function)
    request_url = get_interface_info(source_code)
    # 发送每个用例接口请求的地址
    AddApiTaskReport = generate_api_task_report_url(task_id)
    data = {"case": request_url}
    r = requests.post(AddApiTaskReport,
                      json=data, headers={"Content-Type": "application/json"})
    result = r.json()
    report_id = result['data']['reportId']
    # 执行测试用例的代码
    yield
    # end_time = datetime.fromtimestamp(time.time())
    # 在测试用例执行之后执行的代码
    CollectApiTaskReport = generate_collect_api_task_report_url(task_id, report_id)
    r = requests.post(CollectApiTaskReport,
                      headers={"Content-Type": "application/json"})
    result = r.json()
    assert result['code'] == 0


# @pytest.hookimpl
def pytest_sessionfinish(session):
    CloseTask = generate_api_close_task_url(task_id)
    r = requests.post(CloseTask,
                      headers={"Content-Type": "application/json"})
    result = r.json()
    assert result['code'] == 0
    print("all tests finished")
