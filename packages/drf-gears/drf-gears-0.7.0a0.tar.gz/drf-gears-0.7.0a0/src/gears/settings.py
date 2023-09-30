from django.conf import settings


def get_settings():
    default = dict(
        runserver_plus_up_tasks=[],
        runserver_plus_down_tasks=[],
    )

    conf = getattr(settings, "GEARS", {})

    return {
        attr_name: conf.get(attr_name, default_value)
        for attr_name, default_value in default.items()
    }
