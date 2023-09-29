from django.urls import re_path

from .api.enroll_apis import EnrollAPI
from .api.enroll_statistics_apis import EnrollStatisticsAPI
from .api.enroll_status_code_api import EnrollStatusCodeAPI
from .api.rarely_data_list_api import OtherListAPIView
from .api.record_apis import RecordAPI
from .api.rule_apis import RuleAPI
from .api.subitem_apis import SubitemApis
from .api.subitem_record_apis import SubitemRecordApis
from .api.valuation_api import ValuationAPIView
from .service_register import register

# 对服务进行，注册可直接访问，提过流程模块等调度模块调用
register()

urlpatterns = [
    # 报名基础接口
    re_path(r'^list/?$', EnrollAPI.list),
    re_path(r'^detail/?(?P<enroll_id>\d+)?$', EnrollAPI.detail),
    re_path(r'^edit/?(?P<enroll_id>\d+)?$', EnrollAPI.edit),
    re_path(r'^delete/?(?P<enroll_id>\d+)?$', EnrollAPI.delete),
    re_path(r'^add/?$', EnrollAPI.add),
    # 业报名 务接口
    re_path(r'^own_list/?$', EnrollAPI.own_list),
    re_path(r'^undertake_list/?$', EnrollAPI.undertake_list),
    re_path(r'^pay_callback/?$', EnrollAPI.enroll_pay_callback),  # 镖行天下支付回调接口

    # 报名记录
    re_path(r'^record_list/?$', RecordAPI.list),  # 不合并太多信息, 仅仅返回记录相关的信息
    re_path(r'^record_list_v2/?$', RecordAPI.list_v2),  # 关联较多数据，发起人、报名人、信息表
    re_path(r'^record_add/?$', RecordAPI.add),
    re_path(r'^record_del/?(?P<pk>\d+)?$', RecordAPI.record_del),
    re_path(r'^record_edit/?(?P<pk>\d+)?$', RecordAPI.record_edit),
    re_path(r'^record_detail/?(?P<pk>\d+)?$', RecordAPI.record_detail),
    re_path(r'^appoint/?$', RecordAPI.appoint),  # 指派报名人完成任务
    re_path(r'^old_appoint/?$', RecordAPI.old_appoint),  # 指派报名人完成任务

    # 报名分项
    re_path(r'^subitem_add/?$', SubitemApis.add),
    re_path(r'^subitem_detail/?(?P<pk>\d+)?$', SubitemApis.detail),
    re_path(r'^subitem_batch_add/?$', SubitemApis.batch_add),
    re_path(r'^subitem_list/?$', SubitemApis.list),
    re_path(r'^subitem_edit/?(?P<pk>\d+)?$', SubitemApis.edit),  # 报名分项,包括资金联动修改，后面会抽离出来 TODO 资金联动代迁移出来
    re_path(r'^subitem_batch_edit/?$', SubitemApis.batch_edit),
    re_path(r'^subitem_edit_by_enroll/?(?P<enroll_id>\d+)?$', SubitemApis.edit_by_enroll_id),  #
    re_path(r'^subitem_extend_field/?$', SubitemApis.extend_field),

    # 报名分项记录
    re_path(r'^subitem_record_add/?$', SubitemRecordApis.add),

    # re_path(r'^subitem_record_del/?(?P<pk>\d+)?$', SubitemRecordApis.delete), // 记录没有删除这个流程节点
    re_path(r'^subitem_record_list/?$', SubitemRecordApis.list),
    re_path(r'^subitem_record_edit/?(?P<pk>\d+)?$', SubitemRecordApis.edit),
    re_path(r'^subitem_record_batch_add/?$', SubitemRecordApis.batch_add),

    # 报名规则
    re_path(r'^rule_list/?$', RuleAPI.list),
    re_path(r'^rule_edit/?(?P<rule_value_id>\d+)?$', RuleAPI.edit),
    re_path(r'^rule_delete/?(?P<rule_value_id>\d+)?$', RuleAPI.delete),
    re_path(r'^rule_add/?$', RuleAPI.add),
    re_path(r'^rule_group_list/?$', RuleAPI.group_list),  # 分组列表

    # 计价接口
    re_path(r'^valuation/?$', ValuationAPIView.valuate),
    re_path(r'^valuation_test/?$', ValuationAPIView.valuate_test),
    re_path(r'^valuation_detailed_list/?(?P<enroll_id>\d+)?$', ValuationAPIView.valuation_detailed_list),

    # 非热更新列表返回
    re_path(r'^status_code/?$', OtherListAPIView.enroll_status_code),

    # 报名统计
    re_path(r'^statistics/?$', EnrollStatisticsAPI.statistics),  # 镖行小程序 统计接口 后期会被弃用
    re_path(r'^statistics_by_user/?$', EnrollStatisticsAPI.statistics_by_user),  # 镖行小程序 统计接口 后期会被弃用
    re_path(r'^every_one_total/?$', EnrollStatisticsAPI.every_one_total),  # 统计每个人的报名数据
    re_path(r'^every_day_total/?$', EnrollStatisticsAPI.every_day_total),  # 统计每日数据的报名数据

    # 报名状态接口
    re_path(r'^batch_edit_code/?$', EnrollStatusCodeAPI.batch_edit_code),
    re_path(r'^ask_enroll_pay_status/?$', EnrollStatusCodeAPI.ask_pay_status),
]
