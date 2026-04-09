from enum import Enum, unique

@unique
class BusinessType(Enum):
    """
    业务操作类型

    OTHER: 其它
    INSERT: 新增
    UPDATE: 修改
    DELETE: 删除
    GRANT: 授权
    EXPORT: 导出
    IMPORT: 导入
    FORCE: 强退
    GENCODE: 生成代码
    CLEAN: 清空数据
    """

    OTHER = 0
    INSERT = 1
    UPDATE = 2
    DELETE = 3
    GRANT = 4
    EXPORT = 5
    IMPORT = 6
    FORCE = 7
    GENCODE = 8
    CLEAN = 9


@unique
class QueueEnum(str, Enum):
    """队列枚举"""
    none = "None"
    not_none = "not None"
    date = "date"
    month = "month"
    like = "like"
    eq = "eq" or "=="
    in_ = "in"
    between = "between"
    ne = "!=" or "ne"
    gt = ">" or "gt"
    ge = ">=" or "ge"
    lt = "<" or "lt"
    le = "<=" or "le"


class PermissionFilterStrategy(str, Enum):
    """
    权限过滤策略枚举

    定义不同的权限过滤策略，让模型选择合适的过滤方式
    """
    DATA_SCOPE = "data_scope"  # 基于数据范围权限（默认）
    ROLE_BASED = "role_based"  # 基于角色授权（菜单）
    DEPT_BASED = "dept_based"  # 基于部门关联（部门、角色）
    SELF_ONLY = "self_only"    # 仅本人数据
    USER_ROLE = "user_role"    # 当前用户绑定的角色
