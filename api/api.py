from .blueprint import api
from .utils import generate_res
from ..models import level_models


# 获取punish_levels, reward_levels,change_levels
@api.route('/changes/')
def changes():
    data = {name: model.all() for name, model in level_models.items()}
    return generate_res("success", data=data)

