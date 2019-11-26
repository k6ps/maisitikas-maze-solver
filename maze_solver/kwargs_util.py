class KwArgsUtil(object):

    @staticmethod
    def kwarg_or_default(default_value, param_key: str, **kwargs):
        if kwargs is None or param_key not in kwargs: 
            return default_value
        else:
            return kwargs[param_key]
