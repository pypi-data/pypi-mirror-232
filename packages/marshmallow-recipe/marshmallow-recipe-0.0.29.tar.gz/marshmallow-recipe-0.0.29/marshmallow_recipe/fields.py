import collections
import collections.abc
import dataclasses
import datetime
import enum
from typing import Any

import marshmallow as m
import marshmallow.validate

_MARSHMALLOW_VERSION_MAJOR = int(m.__version__.split(".")[0])


def str_field(
    *,
    required: bool,
    allow_none: bool,
    default: Any = dataclasses.MISSING,
    name: str | None = None,
    validate: collections.abc.Callable[[Any], Any] | None = None,
    **_: Any,
) -> m.fields.Field:
    if default is m.missing:
        return m.fields.Str(
            allow_none=allow_none,
            validate=validate,
            **default_fields(m.missing),
            **data_key_fields(name),
        )

    if required:
        if default is None:
            raise ValueError("Default value cannot be none")

        return m.fields.String(required=True, allow_none=allow_none, validate=validate, **data_key_fields(name))

    return m.fields.Str(
        allow_none=allow_none,
        validate=validate,
        **default_fields(None if default is dataclasses.MISSING else default),
        **data_key_fields(name),
    )


def bool_field(
    *,
    required: bool,
    allow_none: bool,
    default: Any = dataclasses.MISSING,
    name: str | None = None,
    validate: collections.abc.Callable[[Any], Any] | None = None,
    **_: Any,
) -> m.fields.Field:
    if default is m.missing:
        return m.fields.Bool(
            allow_none=allow_none,
            validate=validate,
            **default_fields(m.missing),
            **data_key_fields(name),
        )

    if required:
        if default is None:
            raise ValueError("Default value cannot be none")

        return m.fields.Boolean(required=True, allow_none=allow_none, validate=validate, **data_key_fields(name))

    return m.fields.Bool(
        allow_none=allow_none,
        validate=validate,
        **default_fields(None if default is dataclasses.MISSING else default),
        **data_key_fields(name),
    )


def decimal_field(
    *,
    required: bool,
    allow_none: bool,
    default: Any = dataclasses.MISSING,
    name: str | None = None,
    places: int = 2,
    as_string: bool = True,
    validate: collections.abc.Callable[[Any], Any] | None = None,
    **_: Any,
) -> m.fields.Field:
    if default is m.missing:
        return m.fields.Decimal(
            allow_none=allow_none,
            as_string=as_string,
            places=places,
            validate=validate,
            **default_fields(m.missing),
            **data_key_fields(name),
        )

    if required:
        if default is None:
            raise ValueError("Default value cannot be none")
        return m.fields.Decimal(
            required=True,
            allow_none=allow_none,
            as_string=as_string,
            places=places,
            validate=validate,
            **data_key_fields(name),
        )

    return m.fields.Decimal(
        allow_none=allow_none,
        as_string=as_string,
        places=places,
        validate=validate,
        **default_fields(None if default is dataclasses.MISSING else default),
        **data_key_fields(name),
    )


def int_field(
    *,
    required: bool,
    allow_none: bool,
    default: Any = dataclasses.MISSING,
    name: str | None = None,
    validate: collections.abc.Callable[[Any], Any] | None = None,
    **_: Any,
) -> m.fields.Field:
    if default is m.missing:
        return m.fields.Int(
            allow_none=allow_none,
            validate=validate,
            **default_fields(m.missing),
            **data_key_fields(name),
        )

    if required:
        if default is None:
            raise ValueError("Default value cannot be none")
        return m.fields.Int(required=True, allow_none=allow_none, validate=validate, **data_key_fields(name))

    return m.fields.Int(
        allow_none=allow_none,
        validate=validate,
        **default_fields(None if default is dataclasses.MISSING else default),
        **data_key_fields(name),
    )


def float_field(
    *,
    required: bool,
    allow_none: bool,
    default: Any = dataclasses.MISSING,
    name: str | None = None,
    validate: collections.abc.Callable[[Any], Any] | None = None,
    **_: Any,
) -> m.fields.Field:
    if default is m.missing:
        return m.fields.Float(
            allow_none=allow_none,
            validate=validate,
            **default_fields(m.missing),
            **data_key_fields(name),
        )

    if required:
        if default is None:
            raise ValueError("Default value cannot be none")
        return m.fields.Float(required=True, allow_none=allow_none, validate=validate, **data_key_fields(name))

    return m.fields.Float(
        allow_none=allow_none,
        validate=validate,
        **default_fields(None if default is dataclasses.MISSING else default),
        **data_key_fields(name),
    )


def uuid_field(
    *,
    required: bool,
    allow_none: bool,
    default: Any = dataclasses.MISSING,
    name: str | None = None,
    validate: collections.abc.Callable[[Any], Any] | None = None,
    **_: Any,
) -> m.fields.Field:
    if default is m.missing:
        return m.fields.UUID(
            allow_none=allow_none,
            validate=validate,
            **default_fields(m.missing),
            **data_key_fields(name),
        )

    if required:
        if default is None:
            raise ValueError("Default value cannot be none")
        return m.fields.UUID(required=True, allow_none=allow_none, validate=validate, **data_key_fields(name))

    return m.fields.UUID(
        allow_none=allow_none,
        validate=validate,
        **default_fields(None if default is dataclasses.MISSING else default),
        **data_key_fields(name),
    )


def datetime_field(
    *,
    required: bool,
    allow_none: bool,
    default: Any = dataclasses.MISSING,
    name: str | None = None,
    validate: collections.abc.Callable[[Any], Any] | None = None,
    format: str | None = None,
    **_: Any,
) -> m.fields.Field:
    if default is m.missing:
        return DateTimeField(
            allow_none=allow_none,
            validate=validate,
            format=format,
            **default_fields(m.missing),
            **data_key_fields(name),
        )

    if required:
        if default is None:
            raise ValueError("Default value cannot be none")
        return DateTimeField(
            required=True, allow_none=allow_none, validate=validate, format=format, **data_key_fields(name)
        )

    return DateTimeField(
        allow_none=allow_none,
        validate=validate,
        format=format,
        **default_fields(None if default is dataclasses.MISSING else default),
        **data_key_fields(name),
    )


def date_field(
    *,
    required: bool,
    allow_none: bool,
    default: Any = dataclasses.MISSING,
    name: str | None = None,
    validate: collections.abc.Callable[[Any], Any] | None = None,
    **_: Any,
) -> m.fields.Field:
    if default is m.missing:
        return m.fields.Date(
            allow_none=allow_none,
            validate=validate,
            **default_fields(m.missing),
            **data_key_fields(name),
        )

    if required:
        if default is None:
            raise ValueError("Default value cannot be none")
        return m.fields.Date(required=True, allow_none=allow_none, validate=validate, **data_key_fields(name))

    return m.fields.Date(
        allow_none=allow_none,
        validate=validate,
        **default_fields(None if default is dataclasses.MISSING else default),
        **data_key_fields(name),
    )


def nested_field(
    nested_schema: type[m.Schema],
    *,
    required: bool,
    allow_none: bool,
    default: Any = dataclasses.MISSING,
    name: str | None = None,
    validate: collections.abc.Callable[[Any], Any] | None = None,
    **_: Any,
) -> m.fields.Field:
    if default is m.missing:
        return m.fields.Nested(
            nested_schema,
            allow_none=allow_none,
            validate=validate,
            **default_fields(m.missing),
            **data_key_fields(name),
        )

    if required:
        if default is None:
            raise ValueError("Default value cannot be none")
        return m.fields.Nested(
            nested_schema, required=True, allow_none=allow_none, validate=validate, **data_key_fields(name)
        )

    return m.fields.Nested(
        nested_schema,
        allow_none=allow_none,
        validate=validate,
        **default_fields(None if default is dataclasses.MISSING else default),
        **data_key_fields(name),
    )


def list_field(
    field: m.fields.Field,
    *,
    required: bool,
    allow_none: bool,
    default: Any = dataclasses.MISSING,
    name: str | None = None,
    validate: collections.abc.Callable[[Any], Any] | None = None,
    **_: Any,
) -> m.fields.Field:
    if default is m.missing:
        return m.fields.List(
            field,
            allow_none=allow_none,
            validate=validate,
            **default_fields(m.missing),
            **data_key_fields(name),
        )

    if required:
        if default is None:
            raise ValueError("Default value cannot be none")
        return m.fields.List(field, required=True, allow_none=allow_none, validate=validate, **data_key_fields(name))

    return m.fields.List(
        field,
        allow_none=allow_none,
        validate=validate,
        **default_fields(None if default is dataclasses.MISSING else default),
        **data_key_fields(name),
    )


def set_field(
    field: m.fields.Field,
    *,
    required: bool,
    allow_none: bool,
    default: Any = dataclasses.MISSING,
    name: str | None = None,
    validate: collections.abc.Callable[[Any], Any] | None = None,
    **_: Any,
) -> m.fields.Field:
    if default is m.missing:
        return SetField(
            field,
            allow_none=allow_none,
            validate=validate,
            **default_fields(m.missing),
            **data_key_fields(name),
        )

    if required:
        if default is None:
            raise ValueError("Default value cannot be none")
        return SetField(field, required=True, allow_none=allow_none, validate=validate, **data_key_fields(name))

    return SetField(
        field,
        allow_none=allow_none,
        validate=validate,
        **default_fields(None if default is dataclasses.MISSING else default),
        **data_key_fields(name),
    )


def frozen_set_field(
    field: m.fields.Field,
    *,
    required: bool,
    allow_none: bool,
    default: Any = dataclasses.MISSING,
    name: str | None = None,
    validate: collections.abc.Callable[[Any], Any] | None = None,
    **_: Any,
) -> m.fields.Field:
    if default is m.missing:
        return FrozenSetField(
            field,
            allow_none=allow_none,
            validate=validate,
            **default_fields(m.missing),
            **data_key_fields(name),
        )

    if required:
        if default is None:
            raise ValueError("Default value cannot be none")
        return FrozenSetField(field, required=True, allow_none=allow_none, validate=validate, **data_key_fields(name))

    return FrozenSetField(
        field,
        allow_none=allow_none,
        validate=validate,
        **default_fields(None if default is dataclasses.MISSING else default),
        **data_key_fields(name),
    )


def tuple_field(
    field: m.fields.Field,
    *,
    required: bool,
    allow_none: bool,
    default: Any = dataclasses.MISSING,
    name: str | None = None,
    validate: collections.abc.Callable[[Any], Any] | None = None,
    **_: Any,
) -> m.fields.Field:
    if default is m.missing:
        return TupleField(
            field,
            allow_none=allow_none,
            validate=validate,
            **default_fields(m.missing),
            **data_key_fields(name),
        )

    if required:
        if default is None:
            raise ValueError("Default value cannot be none")
        return TupleField(field, required=True, allow_none=allow_none, validate=validate, **data_key_fields(name))

    return TupleField(
        field,
        allow_none=allow_none,
        validate=validate,
        **default_fields(None if default is dataclasses.MISSING else default),
        **data_key_fields(name),
    )


def dict_field(
    keys_field: m.fields.Field | None,
    values_field: m.fields.Field | None,
    *,
    required: bool,
    allow_none: bool,
    default: Any = dataclasses.MISSING,
    name: str | None = None,
    validate: collections.abc.Callable[[Any], Any] | None = None,
    **_: Any,
) -> m.fields.Field:
    if default is m.missing:
        return DictField(
            keys=keys_field,
            values=values_field,
            allow_none=allow_none,
            validate=validate,
            **default_fields(m.missing),
            **data_key_fields(name),
        )

    if required:
        if default is None:
            raise ValueError("Default value cannot be none")
        return DictField(
            keys=keys_field,
            values=values_field,
            required=True,
            allow_none=allow_none,
            validate=validate,
            **data_key_fields(name),
        )

    return DictField(
        keys=keys_field,
        values=values_field,
        allow_none=allow_none,
        validate=validate,
        **default_fields(None if default is dataclasses.MISSING else default),
        **data_key_fields(name),
    )


def enum_field(
    enum_type: type[enum.Enum],
    *,
    required: bool,
    allow_none: bool,
    name: str | None = None,
    default: Any = dataclasses.MISSING,
    validate: collections.abc.Callable[[Any], Any] | None = None,
    **_: Any,
) -> marshmallow.fields.Field:
    if default is m.missing:
        return EnumField(
            enum_type=enum_type,
            allow_none=allow_none,
            validate=validate,
            **default_fields(m.missing),
            **data_key_fields(name),
        )

    if required:
        if default is None:
            raise ValueError("Default value cannot be none")
        return EnumField(
            enum_type=enum_type,
            required=True,
            allow_none=allow_none,
            validate=validate,
            **data_key_fields(name),
        )

    return EnumField(
        enum_type=enum_type,
        allow_none=allow_none,
        validate=validate,
        **default_fields(None if default is dataclasses.MISSING else default),
        **data_key_fields(name),
    )


def raw_field(
    *,
    default: Any = dataclasses.MISSING,
    name: str | None = None,
    validate: collections.abc.Callable[[Any], Any] | None = None,
    **_: Any,
) -> m.fields.Field:
    return m.fields.Raw(
        allow_none=True,
        validate=validate,
        **default_fields(None if default is dataclasses.MISSING else default),
        **data_key_fields(name),
    )


DateTimeField: type[m.fields.DateTime]
EnumField: type[m.fields.String]
DictField: type[m.fields.Field]
SetField: type[m.fields.List]
FrozenSetField: type[m.fields.List]
TupleField: type[m.fields.List]

if _MARSHMALLOW_VERSION_MAJOR >= 3:

    def data_key_fields(name: str | None) -> dict[str, Any]:
        if name is None:
            return {}
        return dict(data_key=name)

    def default_fields(value: Any) -> dict[str, Any]:
        return dict(dump_default=value, load_default=value)

    class DateTimeFieldV3(m.fields.DateTime):
        def _deserialize(self, value: Any, attr: Any, data: Any, **kwargs: Any) -> Any:
            result = super()._deserialize(value, attr, data, **kwargs)
            if result.tzinfo is None:
                return result.replace(tzinfo=datetime.timezone.utc)
            return result.astimezone(datetime.timezone.utc)

        def _serialize(self, value: Any, attr: Any, obj: Any, **kwargs: Any) -> Any:
            if value is None:
                return None

            if value.tzinfo is None:
                value = value.replace(tzinfo=datetime.timezone.utc)

            return super()._serialize(value, attr, obj, **kwargs)

    DateTimeField = DateTimeFieldV3

    class SetFieldV3(m.fields.List):
        def _deserialize(self, value: Any, attr: Any, data: Any, **kwargs: Any) -> Any:
            result = super()._deserialize(value, attr, data, **kwargs)
            return None if None else set(result)

    SetField = SetFieldV3

    class FrozenSetFieldV3(m.fields.List):
        def _deserialize(self, value: Any, attr: Any, data: Any, **kwargs: Any) -> Any:
            result = super()._deserialize(value, attr, data, **kwargs)
            return None if None else frozenset(result)

    FrozenSetField = FrozenSetFieldV3

    class TupleFieldV3(m.fields.List):
        def _deserialize(self, value: Any, attr: Any, data: Any, **kwargs: Any) -> Any:
            result = super()._deserialize(value, attr, data, **kwargs)
            return None if None else tuple(result)

    TupleField = TupleFieldV3

    class EnumFieldV3(m.fields.String):
        default_error = "Not a valid choice: '{input}'. Allowed values: {choices}"

        def __init__(
            self,
            *args: Any,
            enum_type: type[enum.Enum],
            error: str | None = None,
            extendable_default: Any = m.missing,
            **kwargs: Any,
        ):
            """
            :param enum_type: class inherited from Enum and string, where all values are different strings
            :param error: error string pattern with {input} and {choices}
            """
            allow_none = (
                kwargs.get("allow_none") is True
                or kwargs.get("allow_none") is None
                and kwargs.get("missing", m.missing) is None
            )

            self.enum_type = enum_type
            self._validate_enum(self.enum_type)

            self.error = error or EnumFieldV3.default_error
            self._validate_error(self.error)

            self.choices = [enum_instance.value for enum_instance in enum_type]
            self._validate_choices(self.choices)
            if allow_none:
                self.choices.append(None)

            self.extendable_default = extendable_default
            self._validate_default(self.enum_type, self.extendable_default, allow_none)
            if "dump_default" in kwargs:
                self._validate_default(self.enum_type, kwargs["dump_default"], allow_none)
            if "load_default" in kwargs:
                self._validate_default(self.enum_type, kwargs["load_default"], allow_none)

            enum_validator = m.validate.OneOf(self.choices, error=self.error)  # type: ignore
            if "validate" in kwargs and kwargs["validate"] is not None:
                validators = kwargs["validate"]
                if not isinstance(validators, list):
                    validators = [validators]
                validators.append(enum_validator)
                kwargs["validate"] = validators
            else:
                kwargs["validate"] = enum_validator

            super().__init__(*args, **kwargs)

        def _serialize(self, value: Any, attr: Any, obj: Any, **kwargs: Any) -> Any:
            if value is None:
                return None
            if isinstance(value, self.enum_type):
                return value.value
            return super()._serialize(value, attr, obj)

        def _deserialize(self, value: Any, attr: Any, data: Any, **kwargs: Any) -> Any:
            if value is None:
                return None
            if isinstance(value, self.enum_type):
                return value
            string_value = super()._deserialize(value, attr, data)
            try:
                return self.enum_type(string_value)
            except ValueError:
                if self.extendable_default is m.missing:
                    raise m.ValidationError(self.default_error.format(input=value, choices=self.choices))
                return self.extendable_default
            except Exception:
                raise m.ValidationError(self.default_error.format(input=value, choices=self.choices))

        @staticmethod
        def _validate_enum(enum_type: Any) -> None:
            if not issubclass(enum_type, enum.Enum):
                raise ValueError(f"Enum type {enum_type} should be subtype of Enum")
            if not issubclass(enum_type, str):
                raise ValueError(f"Enum type {enum_type} should be subtype of str")

        @staticmethod
        def _validate_error(error: str) -> None:
            try:
                error.format(input="", choices="")
            except KeyError:
                raise ValueError("Error should contain only {{input}} and {{choices}}'")

        @staticmethod
        def _validate_choices(choices: list) -> None:
            for choice in choices:
                if not isinstance(choice, str):
                    raise ValueError(f"There is enum value, which is not a string: {choice}")

        @staticmethod
        def _validate_default(enum_type: Any, default: Any, allow_none: bool) -> None:
            if default is m.missing:
                return

            if allow_none and default is None:
                return

            if callable(default):
                return

            if not isinstance(default, enum_type):
                raise ValueError(f"Default should be an instance of enum_type {enum_type}")

    EnumField = EnumFieldV3

    DictField = m.fields.Dict
else:
    dateutil_tz_utc_cls: type[datetime.tzinfo] | None
    try:
        import dateutil.tz  # type: ignore

        dateutil_tz_utc_cls = dateutil.tz.tzutc
    except ImportError:
        dateutil_tz_utc_cls = None

    def data_key_fields(name: str | None) -> dict[str, Any]:
        if name is None:
            return {}
        return dict(dump_to=name, load_from=name)

    def default_fields(value: Any) -> dict[str, Any]:
        return dict(missing=value, default=value)

    class DateTimeFieldV2(m.fields.DateTime):
        def _deserialize(self, value: Any, attr: Any, data: Any, **_: Any) -> Any:
            result = super()._deserialize(value, attr, data)
            if result.tzinfo is None:
                return result.replace(tzinfo=datetime.timezone.utc)
            if dateutil_tz_utc_cls is not None and isinstance(result.tzinfo, dateutil_tz_utc_cls):
                return result.replace(tzinfo=datetime.timezone.utc)
            return result.astimezone(datetime.timezone.utc)

    DateTimeField = DateTimeFieldV2

    class SetFieldV2(m.fields.List):
        def _deserialize(self, value: Any, attr: Any, data: Any, **_: Any) -> Any:
            result = super()._deserialize(value, attr, data)
            return None if None else set(result)

    SetField = SetFieldV2

    class FrozenSetFieldV2(m.fields.List):
        def _deserialize(self, value: Any, attr: Any, data: Any, **_: Any) -> Any:
            result = super()._deserialize(value, attr, data)
            return None if None else frozenset(result)

    FrozenSetField = FrozenSetFieldV2

    class TupleFieldV2(m.fields.List):
        def _deserialize(self, value: Any, attr: Any, data: Any, **_: Any) -> Any:
            result = super()._deserialize(value, attr, data)
            return None if None else tuple(result)

    TupleField = TupleFieldV2

    class EnumFieldV2(m.fields.String):
        default_error = "Not a valid choice: '{input}'. Allowed values: {choices}"

        def __init__(
            self,
            *args: Any,
            enum_type: type[enum.Enum],
            error: str | None = None,
            extendable_default: Any = m.missing,
            **kwargs: Any,
        ):
            """
            :param enum_type: class inherited from Enum and string, where all values are different strings
            :param error: error string pattern with {input} and {choices}
            """
            allow_none = (
                kwargs.get("allow_none") is True
                or kwargs.get("allow_none") is None
                and kwargs.get("missing", m.missing) is None
            )

            self.enum_type = enum_type
            self._validate_enum(self.enum_type)

            self.error = error or EnumFieldV2.default_error
            self._validate_error(self.error)

            self.choices = [enum_instance.value for enum_instance in enum_type]
            self._validate_choices(self.choices)
            if allow_none:
                self.choices.append(None)

            self.extendable_default = extendable_default
            self._validate_default(self.enum_type, self.extendable_default, allow_none)
            if "default" in kwargs:
                self._validate_default(self.enum_type, kwargs["default"], allow_none)
            if "missing" in kwargs:
                self._validate_default(self.enum_type, kwargs["missing"], allow_none)

            enum_validator = m.validate.OneOf(self.choices, error=self.error)  # type: ignore
            if "validate" in kwargs and kwargs["validate"] is not None:
                validators = kwargs["validate"]
                if not isinstance(validators, list):
                    validators = [validators]
                validators.append(enum_validator)
                kwargs["validate"] = validators
            else:
                kwargs["validate"] = enum_validator

            super().__init__(*args, **kwargs)

        def _serialize(self, value: Any, attr: Any, obj: Any, **kwargs: Any) -> Any:
            if value is None:
                return None
            if isinstance(value, self.enum_type):
                return value.value
            return super()._serialize(value, attr, obj)

        def _deserialize(self, value: Any, attr: Any, data: Any, **kwargs: Any) -> Any:
            if value is None:
                return None
            if isinstance(value, self.enum_type):
                return value
            string_value = super()._deserialize(value, attr, data)
            try:
                return self.enum_type(string_value)
            except ValueError:
                if self.extendable_default is m.missing:
                    raise m.ValidationError(self.default_error.format(input=value, choices=self.choices))
                return self.extendable_default
            except Exception:
                raise m.ValidationError(self.default_error.format(input=value, choices=self.choices))

        @staticmethod
        def _validate_enum(enum_type: Any) -> None:
            if not issubclass(enum_type, enum.Enum):
                raise ValueError(f"Enum type {enum_type} should be subtype of Enum")
            if not issubclass(enum_type, str):
                raise ValueError(f"Enum type {enum_type} should be subtype of str")

        @staticmethod
        def _validate_error(error: str) -> None:
            try:
                error.format(input="", choices="")
            except KeyError:
                raise ValueError("Error should contain only {{input}} and {{choices}}'")

        @staticmethod
        def _validate_choices(choices: list) -> None:
            for choice in choices:
                if not isinstance(choice, str):
                    raise ValueError(f"There is enum value, which is not a string: {choice}")

        @staticmethod
        def _validate_default(enum_type: Any, default: Any, allow_none: bool) -> None:
            if default is m.missing:
                return

            if allow_none and default is None:
                return

            if callable(default):
                return

            if not isinstance(default, enum_type):
                raise ValueError(f"Default should be an instance of enum_type {enum_type}")

    EnumField = EnumFieldV2

    class TypedDict(m.fields.Field):
        default_error_messages = {"invalid": "Not a valid mapping type."}

        def __init__(
            self, keys: m.fields.Field | None = None, values: m.fields.Field | None = None, *args: Any, **kwargs: Any
        ):
            self.keys = keys
            self.values = values
            super().__init__(*args, **kwargs)

        def _serialize(self, value: Any, attr: Any, obj: Any, **kwargs: Any) -> Any:
            if value is None:
                return None
            if self.values is None and self.keys is None:
                return value

            if self.keys is None:
                keys = {k: k for k in value.keys()}
            else:
                keys = {k: self.keys._serialize(k, None, None, **kwargs) for k in value.keys()}

            result = {}
            if self.values is None:
                for k, v in value.items():
                    if k in keys:
                        result[keys[k]] = v
            else:
                for k, v in value.items():
                    result[keys[k]] = self.values._serialize(v, None, None, **kwargs)

            return result

        def _deserialize(self, value: Any, attr: Any, data: Any, **kwargs: Any) -> Any:
            if not isinstance(value, dict):
                self.fail("invalid")

            if self.keys is None and self.values is None:
                return value

            errors = collections.defaultdict(dict)  # type: ignore

            if self.keys is None:
                keys = {k: k for k in value.keys()}
            else:
                keys = {}
                for key in value.keys():
                    try:
                        keys[key] = self.keys.deserialize(key, **kwargs)
                    except m.ValidationError as error:
                        errors[key]["key"] = error.messages

            result = {}
            if self.values is None:
                for k, v in value.items():
                    if k in keys:
                        result[keys[k]] = v
            else:
                for key, val in value.items():
                    try:
                        deserialized_value = self.values.deserialize(val, **kwargs)
                    except m.ValidationError as error:
                        errors[key]["value"] = error.messages
                        if error.data is not None and key in keys:
                            result[keys[key]] = error.data
                    else:
                        if key in keys:
                            result[keys[key]] = deserialized_value

            if errors:
                raise m.ValidationError(errors, data=result)

            if errors:
                raise m.ValidationError(errors)

            return result

    DictField = TypedDict
