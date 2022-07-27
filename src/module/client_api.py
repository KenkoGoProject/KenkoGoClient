from module.global_dict import Global


class ClientApi:
    """Client API"""
    @staticmethod
    def get_info() -> dict:
        """获取Client的信息"""
        return {
            'app_name': Global().app_name,
            'version': Global().version_str,
        }
