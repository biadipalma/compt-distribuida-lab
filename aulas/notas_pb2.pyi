from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Nota(_message.Message):
    __slots__ = ("ra", "cod_disciplina", "ano", "semestre", "nota")
    RA_FIELD_NUMBER: _ClassVar[int]
    COD_DISCIPLINA_FIELD_NUMBER: _ClassVar[int]
    ANO_FIELD_NUMBER: _ClassVar[int]
    SEMESTRE_FIELD_NUMBER: _ClassVar[int]
    NOTA_FIELD_NUMBER: _ClassVar[int]
    ra: str
    cod_disciplina: str
    ano: int
    semestre: int
    nota: float
    def __init__(self, ra: _Optional[str] = ..., cod_disciplina: _Optional[str] = ..., ano: _Optional[int] = ..., semestre: _Optional[int] = ..., nota: _Optional[float] = ...) -> None: ...

class ConsultaNotaResponse(_message.Message):
    __slots__ = ("sucesso", "nota", "msg_erro")
    SUCESSO_FIELD_NUMBER: _ClassVar[int]
    NOTA_FIELD_NUMBER: _ClassVar[int]
    MSG_ERRO_FIELD_NUMBER: _ClassVar[int]
    sucesso: bool
    nota: Nota
    msg_erro: str
    def __init__(self, sucesso: _Optional[bool] = ..., nota: _Optional[_Union[Nota, _Mapping]] = ..., msg_erro: _Optional[str] = ...) -> None: ...

class AlunoDisciplinaRequest(_message.Message):
    __slots__ = ("ra", "cod_disciplina")
    RA_FIELD_NUMBER: _ClassVar[int]
    COD_DISCIPLINA_FIELD_NUMBER: _ClassVar[int]
    ra: str
    cod_disciplina: str
    def __init__(self, ra: _Optional[str] = ..., cod_disciplina: _Optional[str] = ...) -> None: ...

class AdicionaNotaRequest(_message.Message):
    __slots__ = ("ra", "cod_disciplina", "ano", "semestre", "nota")
    RA_FIELD_NUMBER: _ClassVar[int]
    COD_DISCIPLINA_FIELD_NUMBER: _ClassVar[int]
    ANO_FIELD_NUMBER: _ClassVar[int]
    SEMESTRE_FIELD_NUMBER: _ClassVar[int]
    NOTA_FIELD_NUMBER: _ClassVar[int]
    ra: str
    cod_disciplina: str
    ano: int
    semestre: int
    nota: float
    def __init__(self, ra: _Optional[str] = ..., cod_disciplina: _Optional[str] = ..., ano: _Optional[int] = ..., semestre: _Optional[int] = ..., nota: _Optional[float] = ...) -> None: ...

class StatusResponse(_message.Message):
    __slots__ = ("sucesso", "msg")
    SUCESSO_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    sucesso: bool
    msg: str
    def __init__(self, sucesso: _Optional[bool] = ..., msg: _Optional[str] = ...) -> None: ...

class AlunoRequest(_message.Message):
    __slots__ = ("ra",)
    RA_FIELD_NUMBER: _ClassVar[int]
    ra: str
    def __init__(self, ra: _Optional[str] = ...) -> None: ...

class MediaResponse(_message.Message):
    __slots__ = ("sucesso", "media", "msg_erro")
    SUCESSO_FIELD_NUMBER: _ClassVar[int]
    MEDIA_FIELD_NUMBER: _ClassVar[int]
    MSG_ERRO_FIELD_NUMBER: _ClassVar[int]
    sucesso: bool
    media: float
    msg_erro: str
    def __init__(self, sucesso: _Optional[bool] = ..., media: _Optional[float] = ..., msg_erro: _Optional[str] = ...) -> None: ...
