from typing import List, Tuple

from django.db import models


class OnChangeModel(models.Model):
    """
    Handle a field edition.

    on_change_fields -- a list of field for processing by this model.
    Create a method with name like 'on_change_<field_name>' for handling its edition.
    """

    # It would be nice to make a decorator @on_change(field1, field2...)

    on_change_fields = ()
    pre_save_prefix = 'on_change_'
    origin_prefix = '__origin_'

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.get_on_change_fields():
            setattr(self, self.get_origin_name(name), getattr(self, name, None))

    def save(self, *args, **kwargs):
        self.process_changed_fields()
        super().save(*args, **kwargs)
        self.after_save()

    def execute_on_change_method(self, origin_name, origin_value, name, value):
        method = self._get_method(name)
        method(origin_value, value)
        # set new value as original value preventing extra method execution
        setattr(self, origin_name, value)

    def get_origin_name(self, name):
        return f'{self.origin_prefix}{name}'

    def get_origin_value(self, origin_name):
        return getattr(self, origin_name)

    def process_changed_fields(self):
        for origin_name, origin_value, name, value in self.get_changed_fields():
            self.execute_on_change_method(origin_name, origin_value, name, value)

    def after_save(self):
        """Customize it on your taste"""
        pass

    def get_on_change_fields(self):
        return self.on_change_fields

    def get_changed_fields(self) -> List[Tuple]:
        for name in self.get_on_change_fields():
            origin_name = self.get_origin_name(name)
            origin_value = self.get_origin_value(origin_name)
            value = getattr(self, name)
            if value != origin_value:
                yield origin_name, origin_value, name, value

    def _get_method(self, field_name: str):
        method_name = f'{self.pre_save_prefix}{field_name}'
        try:
            return getattr(self, method_name)
        except AttributeError:
            raise Exception(f'OnChangeModel has no method {method_name}')
