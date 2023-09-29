"""
@project: djangoModel->tool
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: CURD 工具
@created_time: 2022/9/15 14:14
"""
from pathlib import Path
import time

from django.core.paginator import Paginator, EmptyPage
from django.db.models import F, Count

from main.settings import BASE_DIR
from xj_user.services.user_detail_info_service import DetailInfoService
from ..models import Enroll, EnrollRecord, EnrollSubitem, EnrollSubitemRecord
from ..service.enroll_record_serivce import EnrollRecordServices
from ..service.enroll_status_code_service import EnrollStatusCodeService
from ..service.enroll_subitem_record_service import EnrollSubitemRecordService
from ..service.subitem_extend_service import output_convert
from ..utils.custom_tool import format_params_handle, write_to_log, filter_fields_handler, force_transform_type, dynamic_load_class
from ..utils.j_config import JConfig
from ..utils.j_dict import JDict

module_root = str(Path(__file__).resolve().parent)
# 配置之对象
main_config_dict = JDict(JConfig.get_section(path=str(BASE_DIR) + "/config.ini", section="xj_finance"))
module_config_dict = JDict(JConfig.get_section(path=str(BASE_DIR) + "/config.ini", section="xj_finance"))

sand_box_meet = main_config_dict.sand_box_meet or module_config_dict.sand_box_meet or ""
sand_box_receivable = main_config_dict.sand_box_receivable or module_config_dict.sand_box_receivable or ""


class EnrollServices:
    enroll_fields = [i.name for i in Enroll._meta.fields]

    def __init__(self):
        pass

    @staticmethod
    def __record_aggregate_by_enroll(enroll_id: int = None, enroll_id_list: list = None, exclude_code=124):
        """根据报名ID对记录进行聚合"""
        enroll_id, is_pass = force_transform_type(variable=enroll_id, var_type="int")
        enroll_id_list, is_pass = force_transform_type(variable=enroll_id_list, var_type="list_int")
        if not enroll_id_list and not enroll_id:
            return [], None
        # ----------------------- section 构建ORM start ----------------------------
        record_orm = EnrollRecord.objects
        if exclude_code:
            record_orm = record_orm.exclude(enroll_status_code=exclude_code)
        if enroll_id:
            count = record_orm.filter(enroll_id=enroll_id).count()
            return count, None
        else:
            record_orm = record_orm.filter(enroll_id__in=enroll_id_list)
            res = record_orm.values("enroll_id").annotate(count=Count("id")).values("enroll_id", "count")
            return {item["enroll_id"]: item["count"] for item in list(res)}, None
        # ----------------------- section 构建ORM start ----------------------------

    @staticmethod
    def enroll_add(params: dict = None):
        """
        报名表新增
        :param params: 添加参数
        :return: data,err
        """
        params, is_pass = force_transform_type(variable=params, var_type="dict")
        # 请求限制类型
        try:
            params = format_params_handle(
                param_dict=params,
                is_validate_type=True,
                is_remove_empty=True,
                filter_filed_list=[
                    "thread_id|int",
                    "category_id|int",
                    "user_id|int",
                    "trading_relate|int",
                    "region_code",
                    "occupy_room",
                    "enroll_status_code|int",
                    "min_number|int",
                    "max_number|int",
                    "min_count_apiece|int",
                    "max_count_apiece|int",
                    "enroll_rule_group_id|int",
                    "price|float",
                    "count|int",
                    "unit",
                    "fee|float",
                    "reduction|float",
                    "subitems_amount|float",
                    "amount|float",
                    "paid_amount|float",
                    "unpaid_amount|float",
                    "commision|float",
                    "deposit|float",
                    "hide_price|int",
                    "hide_user|int",
                    "has_repeat|int",
                    "has_subitem|int",
                    "has_audit|int",
                    "need_vouch|int",
                    "need_deposit|int",
                    "need_imprest|int",
                    "enable_pool|int",
                    "pool_limit|int",
                    "pool_stopwatch|int",
                    "open_time|date",
                    "close_time|date",
                    "launch_time|date",
                    "finish_time|date",
                    "spend_time|date",
                    "create_time|date",
                    "update_time|date",
                    "snapshot|dict",
                    "remark",
                    "finance_invoicing_code"
                ],
            )
        except ValueError as e:
            return None, str(e)

        # 必填参数校验
        must_keys = ["thread_id", "category_id", "user_id"]
        for i in must_keys:
            if not params.get(i, None):
                return None, str(i) + "必填"

        #  ORM添加插入操作
        try:
            instance = Enroll.objects.create(**params)
        except Exception as e:
            return None, str(e)
        added_enroll_info = instance.to_json()
        return {
                   "id": added_enroll_info.get("id"),
                   "enroll_id": added_enroll_info.get("id"),
                   "thread_id": added_enroll_info.get("thread_id"),
                   "category_id": added_enroll_info.get("category_id"),
               }, None

    @staticmethod
    def enroll_edit(params: dict = None, enroll_id=None, search_param: dict = None, **kwargs):
        """
        报名编辑
        :param params: 修改的参数
        :param enroll_id: 需要修改的报名主键
        :param search_param: 搜索参数, 服务层根据信息等其他搜索字段检索到需要修改的数据
        :return: data, err
        """
        # 空值检查
        params, is_pass = force_transform_type(variable=params, var_type="dict", default={})
        enroll_id, is_pass = force_transform_type(variable=enroll_id, var_type="int")
        search_param, is_pass = force_transform_type(variable=search_param, var_type="dict", default={})
        if not enroll_id and not search_param:
            return None, "无法找到要修改数据，请检查参数"
        # 搜索字段过滤
        if search_param:
            search_param = format_params_handle(
                param_dict=search_param,
                filter_filed_list=[
                    "enroll_id_list|list", "thread_id|int", "thread_id_list|list", "category_id|int", "category_id_list|list", "trading_relate", "region_code",
                    "enroll_status_code|int", "enroll_rule_group_id|int",
                ],
                split_list=["enroll_id_list", "thread_id_list", "category_id_list"],
                alias_dict={"enroll_id_list": "id__in", "thread_id_list": "thread_id__in"}
            )

        # 修改内容检查处理
        try:
            params = format_params_handle(
                param_dict=params,
                is_validate_type=True,
                is_remove_empty=True,
                filter_filed_list=[
                    "thread_id|int",
                    "category_id|int",
                    "user_id|int",
                    "trading_relate|int",
                    "region_code",
                    "occupy_room",
                    "enroll_status_code|int",
                    "min_number|int",
                    "max_number|int",
                    "min_count_apiece|int",
                    "max_count_apiece|int",
                    "enroll_rule_group_id|int",
                    "price|float",
                    "count|int",
                    "unit",
                    "fee|float",
                    "reduction|float",
                    "subitems_amount|float",
                    "amount|float",
                    "paid_amount|float",
                    "unpaid_amount|float",
                    "commision|float",
                    "deposit|float",
                    "hide_price|int",
                    "hide_user|int",
                    "has_repeat|int",
                    "has_subitem|int",
                    "has_audit|int",
                    "need_vouch|int",
                    "need_deposit|int",
                    "need_imprest|int",
                    "enable_pool|int",
                    "pool_limit|int",
                    "pool_stopwatch|int",
                    "open_time|date",
                    "close_time|date",
                    "launch_time|date",
                    "finish_time|date",
                    "spend_time|date",
                    "create_time|date",
                    "update_time|date",
                    "snapshot|dict",
                    "remark",
                    "finance_invoicing_code"
                ],
            )
        except ValueError as e:
            return None, str(e)
        if not params:
            return None, "没有可修改的内容"

        # 构建ORM，检查是否存在可修改项目
        enroll_obj = Enroll.objects
        if enroll_id:
            enroll_obj = enroll_obj.filter(id=enroll_id)
        elif search_param:
            enroll_obj = enroll_obj.filter(**search_param)

        update_total = enroll_obj.count()
        if update_total == 0:
            return None, "没有找到可修改项目"

        # IO 操作
        try:
            enroll_obj.update(**params)
        except Exception as e:
            return None, "修改异常:" + str(e)
        return enroll_obj.first().to_json(), None

    @staticmethod
    def enroll_delete(enroll_id=None):
        enroll_id, is_pass = force_transform_type(variable=enroll_id, var_type="int")
        if not enroll_id:
            return None, "不是有效的报名ID"

        enroll_obj = Enroll.objects.filter(id=enroll_id)
        if not enroll_obj:
            return None, None
        try:
            enroll_obj.delete()
        except Exception as e:
            return None, "删除异常:" + str(e)
        return None, None

    @staticmethod
    def enroll_detail(enroll_id: int = None, user_id: int = None, simple_return: bool = False):
        """
        报名详情
        :param enroll_id: 报名ID
        :param user_id: 用户ID
        :param simple_return: 是否仅返回基础信息
        :return: data , err
        """
        enroll_id, is_pass = force_transform_type(variable=enroll_id, var_type="int")
        user_id, is_pass = force_transform_type(variable=user_id, var_type="int")
        if not enroll_id:
            return None, "不是有效的报名ID"

        enroll_obj = Enroll.objects.filter(id=enroll_id).extra(select={
            'open_time': 'DATE_FORMAT(open_time, "%%Y-%%m-%%d %%H:%%i:%%s")',
            "close_time": 'DATE_FORMAT(close_time, "%%Y-%%m-%%d %%H:%%i:%%s")',
            "launch_time": 'DATE_FORMAT(launch_time, "%%Y-%%m-%%d %%H:%%i:%%s")',
            "finish_time": 'DATE_FORMAT(finish_time, "%%Y-%%m-%%d %%H:%%i:%%s")',
            "spend_time": 'DATE_FORMAT(spend_time, "%%Y-%%m-%%d %%H:%%i:%%s")',
            "create_time": 'DATE_FORMAT(create_time, "%%Y-%%m-%%d %%H:%%i:%%s")',
            "update_time": 'DATE_FORMAT(update_time, "%%Y-%%m-%%d %%H:%%i:%%s")',
        })
        if not enroll_obj:
            return None, "找不到该报名信息"
        enroll_detail = enroll_obj.first().to_json()

        if not simple_return:
            # 当前用户是否存在报名记录/当前用户是否存在报名分项记录
            enroll_detail["this_user_has_record"] = 0
            enroll_detail["this_user_has_subitem_record"] = 0
            # ================= 获取需要拼接的数据，报名分项，报名记录，报名分项记录 ==========================
            enroll_subitems_list = output_convert(list(EnrollSubitem.objects.annotate(category_id=F("enroll__category_id")).filter(enroll_id=enroll_id).values()))
            main_record_list, err = EnrollRecordServices.record_list({"enroll_id": enroll_id}, need_pagination=False)
            enroll_subitems_record_list, err = EnrollSubitemRecordService.list({"enroll_id": enroll_id}, False)
            # ================= 获取需要拼接的数据，报名分项，报名记录，报名分项记录 ==========================

            # ==================== 建立分项记录的字典映射  ==============================
            record_id_to_subitems_record_map = {}  # {"enroll_record_id":item}
            subitems_id_to_subitem_record_map = {}  # {"enroll_subitem_id":item}
            for enroll_subitems_record in enroll_subitems_record_list:
                # 判断当前用户是否存在报名分项记录
                if enroll_subitems_record["user_id"] or not enroll_subitems_record["user_id"] == user_id:
                    enroll_detail["this_user_has_subitem_record"] = 1
                # 找到属于其对应的报名记录, 并存如对应的字典中
                if record_id_to_subitems_record_map.get(enroll_subitems_record["enroll_subitem_id"], None) is None:
                    subitems_id_to_subitem_record_map[enroll_subitems_record["enroll_subitem_id"]] = [enroll_subitems_record]
                else:
                    subitems_id_to_subitem_record_map[enroll_subitems_record["enroll_subitem_id"]].append(enroll_subitems_record)

                if subitems_id_to_subitem_record_map.get(enroll_subitems_record["enroll_record_id"], None) is None:
                    record_id_to_subitems_record_map[enroll_subitems_record["enroll_record_id"]] = [enroll_subitems_record]
                else:
                    record_id_to_subitems_record_map[enroll_subitems_record["enroll_record_id"]].append(enroll_subitems_record)
            # ==================== 建立分享记录映射 ==============================

            # ==================== 报名记录和报名分项记录 进行数据拼接 ==========================
            for main_record in main_record_list:
                main_record["subitem_record_list"] = record_id_to_subitems_record_map.get(main_record["id"], {})
                # 遍历判断 该用户是否有报名记录
                if user_id and main_record["user_id"] and main_record["user_id"] == user_id:
                    enroll_detail["this_user_has_record"] = 1

            for enroll_subitem in enroll_subitems_list:
                enroll_subitem["subitem_record_list"] = subitems_id_to_subitem_record_map.get(enroll_subitem["id"], {})

            # 进行赋值
            enroll_detail["subitem_list"] = enroll_subitems_list
            enroll_detail["main_record_list"] = main_record_list
            # ==================== 报名记录和报名分项记录 进行数据拼接 ==========================

        return enroll_detail, None

    @staticmethod
    def enroll_list(params: dict = None, filter_fields: "list|str" = None, need_pagination: bool = True, **kwargs):
        """
        报名列表接口
        :param params: 查询参数
        :param filter_fields: 过滤字段列表或者字符串
        :param need_pagination: 是否需要分页
        :return: {'total': total, "page": page, "size": size, 'list': list(enroll_obj.object_list)}, err
        """
        # ======================= section 字段处理 start ========================
        kwargs, is_pass = force_transform_type(variable=kwargs, var_type="dict", default={})
        params, is_pass = force_transform_type(variable=params, var_type="dict", default={})
        params.update(kwargs)
        size, is_pass = force_transform_type(variable=params.pop('size', 10), var_type="int", default=10)
        page, is_pass = force_transform_type(variable=params.pop('page', 1), var_type="int", default=1)
        exclude_enroll_code, is_pass = force_transform_type(variable=params.pop('exclude_enroll_code', None), var_type="int")  # 不显示的状态
        check_has_record_user, is_pass = force_transform_type(variable=params.get("check_has_record_user"), var_type="int")
        exclude_record_code, is_pass = force_transform_type(variable=params.pop('exclude_record_code', None), var_type="int", default=124)  # 不显示的报名记录状态码
        sort = params.pop('sort', "-id")
        sort = sort if sort in [
            "id", "register_time", "open_time", "close_time", "launch_time", "finish_time", "spend_time",
            "create_time", "update_time", "-id", "-register_time", "-open_time", "-close_time", "-launch_time",
            "-finish_time", "-spend_time", "-create_time", "-update_time",
        ] else "-id"
        # ======================= section 字段处理 end   ========================

        # 处理filter_fields，获取ORM查询字段列表
        filter_fields_list = filter_fields_handler(
            input_field_expression=filter_fields,
            all_field_list=EnrollServices.enroll_fields
        )
        filter_fields_list = list(set(filter_fields_list + ["thread_id", "user_id", "id"]))
        print("params", params)
        # 非法字段剔除，类型转换
        params = format_params_handle(
            param_dict=params,
            is_remove_empty=True,
            filter_filed_list=[
                "id|int", "id_list|list", "thread_id|int", "category_id|int", "category_id_list|list", "thread_id_list|list",
                "user_id|int", "trading_relate", "region_code", "spend_time_start|date",
                "enroll_status_code|int", "enroll_status_code_list|list",
                "spend_time_end|date", "create_time_start|date", "create_time_end|date", "finish_time_start|date", "finish_time_end|date",
                "open_time_start|date", "open_time_end|date", "enroll_status_code|int", "has_subitem|bool", "finance_invoicing_code",
                "enroll_category_value", "bid_opening_time_start|date", "bid_opening_time_end|date",
            ],
            split_list=["category_id_list", "id_list", "enroll_status_code_list", "thread_id_list"],
            alias_dict={
                "spend_time_start": "spend_time__gte", "spend_time_end": "spend_time__lte",
                "create_time_start": "create_time__gte", "create_time_end": "create_time__lte",
                "finish_time_start": "finish_time__gte", "open_time_start": "open_time__gte",
                "open_time_end": "open_time__lte", "enroll_classify_value": "classify__value",
                "enroll_category_value": "category__value",
                "thread_id_list": "thread_id__in", "category_id_list": "category_id__in", "id_list": "id__in",
                "enroll_status_code_list": "enroll_status_code__in",
                "bid_opening_time_start": "bid_opening_time__gte", "bid_opening_time_end": "bid_opening_time__lte",
            },
        )
        print("params", params)
        # 构建ORM
        try:
            enroll_obj = Enroll.objects.extra(select={
                'register_time': 'DATE_FORMAT(register_time, "%%Y-%%m-%%d %%H:%%i:%%s")',
                'open_time': 'DATE_FORMAT(open_time, "%%Y-%%m-%%d %%H:%%i:%%s")',
                'close_time': 'DATE_FORMAT(close_time, "%%Y-%%m-%%d %%H:%%i:%%s")',
                'launch_time': 'DATE_FORMAT(launch_time, "%%Y-%%m-%%d %%H:%%i:%%s")',
                'finish_time': 'DATE_FORMAT(finish_time, "%%Y-%%m-%%d %%H:%%i:%%s")',
                'spend_time': 'DATE_FORMAT(spend_time, "%%Y-%%m-%%d %%H:%%i:%%s")',
                'create_time': 'DATE_FORMAT(create_time, "%%Y-%%m-%%d %%H:%%i:%%s")',
                'update_time': 'DATE_FORMAT(update_time, "%%Y-%%m-%%d %%H:%%i:%%s")'
            }).filter(**params).annotate(
                enroll_category_value=F("category__value"),
                # enroll_classify_value=F("thread__classify__value"),
            ).order_by(sort).values(*filter_fields_list)
            if exclude_enroll_code:
                enroll_obj.exclude(enroll_auth_status=exclude_enroll_code)
        except Exception as e:
            return None, "msg:" + str(e) + ";tip:非法参数"

        # 是否分页，判断返回
        total = enroll_obj.count()
        if not need_pagination and total <= 200:
            finish_list = list(enroll_obj)
        else:
            paginator = Paginator(enroll_obj, size)
            try:
                enroll_obj = paginator.page(page)
            except EmptyPage:
                return {'total': total, "page": page, "size": size, 'list': []}, None
            except Exception as e:
                return None, f'{str(e)}'
            finish_list = list(enroll_obj.object_list)

        enroll_id_list = [i["id"] for i in finish_list]
        # ========== section 验证报名列表，是否存在该用户的报名记录 start ==================
        # 检查指定用户在当前报名列表是否存在报名记录，用户ID为check_has_record_user。
        if check_has_record_user and enroll_id_list:
            has_record_enrolls = list(EnrollRecord.objects.exclude(enroll_status_code=exclude_record_code).filter(
                enroll_id__in=enroll_id_list,
                user_id=check_has_record_user,
            ).values("enroll_id"))
            has_record_enroll_ids = [i["enroll_id"] for i in has_record_enrolls]
            for j in finish_list:
                j["has_record"] = True if j.get("id") in has_record_enroll_ids else False
        # ========== section 验证报名列表，是否存在该用户的报名记录 end   ==================

        # ========== section 报名记录聚合 start ==================
        # 获取当前的报名
        try:
            data, err = EnrollServices.__record_aggregate_by_enroll(
                enroll_id_list=enroll_id_list,
                exclude_code=exclude_record_code
            )
            for i in finish_list:
                i["record_total"] = data.get(i["id"], 0)
        except Exception:
            pass
        # ========== section 报名记录聚合 end   ==================
        for v in finish_list:
            try:
                if int(v["enroll_status_code"]) != 234:  # 非报名中
                    record_params = {
                        "enroll_id": v["id"],
                        "enroll_status_code": v["enroll_status_code"]
                    }
                    record = EnrollRecord.objects.filter(**record_params).order_by("-id").first()
                    user_detail = DetailInfoService.get_detail(user_id=record.user_id)
                    v["audit_real_name"] = user_detail[0]["real_name"]
                    subitem_params = {
                        "enroll_record_id": record.id,
                        "user_id": record.user_id,
                    }
                    subitem_record = EnrollSubitemRecord.objects.filter(**subitem_params).first()
                    if subitem_record.files:
                        v["audit_files"] = subitem_record.files
            except:
                pass

        # 返回结果
        return finish_list if not need_pagination and total <= 200 else {'total': total, "page": page, "size": size, 'list': finish_list}, None

    @staticmethod
    def enroll_own_list(params, need_pagination=True):
        """
        分页查看本人的报名列表
        :param params:
        :param need_pagination:
        :return:
        """
        page, is_pass = force_transform_type(variable=params.pop('page', 1), var_type="int", default=1)
        size, is_pass = force_transform_type(variable=params.pop('size', 10), var_type="int", default=10)

        params = format_params_handle(
            param_dict=params,
            filter_filed_list=[
                "enroll_id", "thread_id", "user_id", "enroll_pay_status", "enroll_status_code", "enroll_status_code_list",
                "price", "count", "amount", "category_id", "thread_id_list", "finance_invoicing_code"
            ],
            split_list=["enroll_status_code_list"],
            alias_dict={"enroll_id": "id", "enroll_status_code_list": "enroll_status_code__in", "thread_id_list": "thread_id__in"}
        )
        enroll_obj = Enroll.objects.filter(**params).order_by("-id").values()
        if not need_pagination:
            # serializer = EnrollRecordListSerializer(data=enroll_obj)
            # serializer.is_valid()
            return list(enroll_obj.object_list), None

        paginator = Paginator(enroll_obj, size)
        try:
            enroll_obj = paginator.page(page)
        except EmptyPage:
            enroll_obj = paginator.page(paginator.num_pages)
        except Exception as e:
            return None, f'{str(e)}'
        return {'total': paginator.count, "page": int(page), "size": int(size), 'list': list(enroll_obj.object_list)}, None

    @staticmethod
    def enroll_undertake_list(params, need_pagination=True):
        size = params.pop('size', 10)
        page = params.pop('page', 1)

        params = format_params_handle(
            param_dict=params,
            filter_filed_list=[
                "enroll_id", "category_id", "thread_id_list", "user_id", "enroll_pay_status", "enroll_status_code",
                "enroll_status_code_list", "price", "count", "amount", "finance_invoicing_code"
            ],
            split_list=["enroll_status_code_list"],
            alias_dict={
                "enroll_status_code_list": "enroll_status_code__in",
                "thread_id_list": "enroll__thread_id__in",
                "category_id": "enroll__category_id"
            }
        )
        enroll_obj = EnrollRecord.objects.annotate(
            commision=F("enroll__commision"),
            thread_id=F("enroll__thread_id")
        ).filter(**params).order_by("-id").values()

        if not need_pagination:
            # 扩展字段替换，并过滤
            return EnrollRecordServices.extend_transform_fields(list(enroll_obj.object_list)), None

        paginator = Paginator(enroll_obj, size)
        try:
            enroll_obj = paginator.page(page)
        except EmptyPage:
            enroll_obj = paginator.page(paginator.num_pages)
        except Exception as e:
            return None, f'{str(e)}'

        # 扩展字段替换，并过滤
        enroll_record_list = EnrollRecordServices.extend_transform_fields(list(enroll_obj.object_list))
        return {'total': paginator.count, "page": page, "size": size, 'list': enroll_record_list}, None

    @staticmethod
    def bxtx_pay_call_back(order_no, payed_code=422):
        """
        镖行天下支付业务回调服务
        回调逻辑：
        1.用户支付分为两种：（1）用户支付预付款 （2）用户补差价
        情况1：支付预付款，但是还没有成单。修改状态进入代报名状态。
        情况2：（报名并指派后）用户支付差价，订单开始。进入上传状态。
        扩展逻辑：分销逻辑，资金逻辑。

        2023-2-6 回调逻辑：第一种代补差价付款成功后，直接进入已接单待上传，第二种：付完首付款后直接进入报名中
        :param payed_code: 已支付状态码
        :param order_no: 订单号
        :return: response
        """
        try:
            # ================= section 通过订单号（order_no）查询订单信息  start ======================
            FinanceListService, import_err = dynamic_load_class(import_path="xj_finance.services.finance_list_service", class_name="FinanceListService")
            if import_err:
                return None, "该系统没有安装资金模块：" + str(import_err)
            finance_transact_data, err = FinanceListService.detail(order_no=order_no)
            write_to_log(
                prefix="报名支付回调",
                content="finance_transact_data:" + str(finance_transact_data or "") + "  err:" + str(err or "")
            )
            if err:
                raise Exception(err)
            # ================= section 通过订单号（order_no）查询订单信息  end ======================

            # ================= section 修改订单状态和已支付金额 start ======================
            enroll_id = finance_transact_data.get("enroll_id", None)
            if not enroll_id:
                return None, None

            outgo = finance_transact_data.get("outgo", 0)
            enroll_obj = Enroll.objects.filter(id=enroll_id).first()
            if not enroll_obj:
                return None, None
            Enroll.objects.filter(id=enroll_id).update(
                paid_amount=abs(float(enroll_obj.paid_amount or 0)) + abs(float(outgo or 0)),
                unpaid_amount=abs(float(enroll_obj.unpaid_amount or 0)) - abs(float(outgo or 0)),
                spend_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            )
            EnrollStatusCodeService.batch_edit_code(enroll_id=enroll_id, code=payed_code)
            # ================= section 修改订单状态和已支付金额 end   ======================

            # ================= section 回调站内通知 start ======================
            try:
                write_to_log(prefix="报名支付回调触发站内通知", content="开发触发通知")
                SinglePushPipeline, import_err = dynamic_load_class(
                    import_path="xj_push.push_pipeline.single_push_pipeline",
                    class_name="SinglePushPipeline"
                )
                if not import_err:
                    SinglePushPipeline.process(params={"enroll_id": enroll_id, "push_action": "payed"})
            except Exception as e:
                write_to_log(
                    prefix="报名支付回调触发站内通知异常",
                    err_obj=e
                )
            # ================= section 回调站内通知 end   ======================
            return payed_code, None
        except Exception as e:
            write_to_log(prefix="报名支付回调异常", content="order_no:" + str(order_no or ""), err_obj=e)
            return None, str(e)

    @staticmethod
    def enroll_check_and_accept(enroll_id=None, check_success_code=656, **kwargs):
        """
        报名余额验收中
        :param enroll_id: 报名ID
        :param check_success_code: 当前审核中的状态码
        :param kwargs:  **
        :return:data,err
        """
        if not enroll_id or check_success_code is None:
            return None, "参数错误"
        is_check_success = Enroll.objects.filter(id=enroll_id, enroll_status_code=check_success_code).values("id").first()
        if not is_check_success:
            return None, "该报名不可触发余额"
        FinanceListService, import_err = dynamic_load_class(import_path="xj_finance.services.finance_list_service", class_name="FinanceListService")
        if import_err:
            return None, "该系统没有安装资金模块：" + str(import_err)
        try:
            # ============ 完成订单联动资金修改 start ============
            # TODO 资金联动代码块，后期使用流程控制
            records_vales = list(
                EnrollRecord.objects.filter(enroll_id=enroll_id, enroll_status_code=check_success_code).values(
                    "user_id", "price", 'again_price', "initiator_again_price"
                )
            )
            for item in records_vales:
                content = {
                    "account_id": item.get("user_id"),
                    "amount": item.get("again_price", 0),
                    "currency": "CNY",
                    "pay_mode": "BALANCE",
                    "enroll_id": enroll_id
                }
                write_to_log(prefix="资金联动修改：", content=content)
                data, err = FinanceListService.finance_create_or_write_off(data=content)
                if err:
                    write_to_log(level="error", prefix="资金余额联动修改异常，finance_create_or_write_off方法err", content=err)
            # ============ 完成订单联动资金修改 end ============
            return None, None
        except Exception as e:
            write_to_log(prefix="资金余额联动修改【enroll_check_and_accept】异常：", err_obj=e)
            return None, str(e)

    @staticmethod
    def old_enroll_check_and_accept(enroll_id=None, **kwargs):
        """
        报名余额验收中
        :param enroll_id: 报名ID
        :param kwargs:  **
        :return:data,err
        """
        if not enroll_id:
            return None, "参数错误，enroll_id为空"
        FinanceListService, import_err = dynamic_load_class(import_path="xj_finance.services.finance_list_service", class_name="FinanceListService")
        if import_err:
            return None, "该系统没有安装资金模块：" + str(import_err)
        try:
            records_vales = list(
                EnrollRecord.objects.filter(enroll_id=enroll_id).exclude(enroll_status_code=124).values(
                    "user_id", "price", 'again_price', "initiator_again_price"
                )
            )
            for item in records_vales:
                content = {
                    "account_id": item.get("user_id"),
                    "amount": item.get("again_price", 0),
                    "currency": "CNY",
                    "pay_mode": "BALANCE",
                    "enroll_id": enroll_id
                }
                write_to_log(prefix="资金联动修改内容", content=content)
                data, err = FinanceListService.finance_create_or_write_off(data=content)
                if err:
                    write_to_log(level="error", prefix="资金余额联动修改异常，finance_create_or_write_off方法err", content=err)
            return None, None
        except Exception as e:
            write_to_log(prefix="资金联动修改异常", err_obj=e)
            return None, str(e)
