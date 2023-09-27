import io
import json
from typing import Any, Union, Iterable

from pydantic import BaseModel

from .client import AsyncTgClient, SyncTgClient, TgRuntimeError, raise_for_tg_response_status
from . import tg_types


class BaseTgRequest(BaseModel):

    class Config:
        extra = 'forbid'
        validate_assignment = True

    async def apost_as_json(self, api_method: str) -> bytes:
        client = AsyncTgClient.default_client.get(None)

        if not client:
            raise TgRuntimeError('Requires AsyncTgClient to be specified before call.')

        http_response = await client.session.post(
            f'{client.api_root}{api_method}',
            headers={
                'content-type': 'application/json',
                'accept': 'application/json',
            },
            content=self.json(exclude_none=True).encode('utf-8'),
        )
        raise_for_tg_response_status(http_response)
        return http_response.content

    def post_as_json(self, api_method: str) -> bytes:
        client = SyncTgClient.default_client.get(None)

        if not client:
            raise TgRuntimeError('Requires SyncTgClient to be specified before call.')

        http_response = client.session.post(
            f'{client.api_root}{api_method}',
            headers={
                'content-type': 'application/json',
                'accept': 'application/json',
            },
            content=self.json(exclude_none=True).encode('utf-8'),
        )
        raise_for_tg_response_status(http_response)
        return http_response.content

    async def apost_multipart_form_data(self, api_method: str, content: dict, files: dict) -> bytes:
        client = AsyncTgClient.default_client.get(None)

        if not client:
            raise TgRuntimeError('Requires AsyncTgClient to be specified before call.')

        if content.get('caption_entities'):
            content['caption_entities'] = json.dumps(content['caption_entities'])

        if content.get('entities'):
            content['entities'] = json.dumps(content['entities'])

        if content.get('reply_markup'):
            content['reply_markup'] = json.dumps(content['reply_markup'])

        if content.get('media'):
            content['media'] = json.dumps(content['media'])

        http_response = await client.session.post(
            f'{client.api_root}{api_method}',
            files=files,
            data=content,
        )
        raise_for_tg_response_status(http_response)
        return http_response.content

    def post_multipart_form_data(self, api_method: str, content: dict, files: dict) -> bytes:
        client = SyncTgClient.default_client.get(None)

        if not client:
            raise TgRuntimeError('Requires SyncTgClient to be specified before call.')

        if content.get('caption_entities'):
            content['caption_entities'] = json.dumps(content['caption_entities'])

        if content.get('entities'):
            content['entities'] = json.dumps(content['entities'])

        if content.get('reply_markup'):
            content['reply_markup'] = json.dumps(content['reply_markup'])

        if content.get('media'):
            content['media'] = json.dumps(content['media'])

        http_response = client.session.post(
            f'{client.api_root}{api_method}',
            files=files,
            data=content,
        )
        raise_for_tg_response_status(http_response)
        return http_response.content


class BaseTgResponse(BaseModel):
    ok: bool
    error_code: int | None = None
    description: str = ''

    result: Any

    class Config:
        extra = 'ignore'
        allow_mutation = False

    # TODO Some errors may also have an optional field 'parameters' of the type ResponseParameters, which can
    # help to automatically handle the error.


class SendMessageResponse(BaseTgResponse):
    result: tg_types.Message


class SendMessageRequest(BaseTgRequest):
    """Object encapsulates data for calling web API endpoint `sendMessage`.

    Telegram web API docs:
        See here https://core.telegram.org/bots/api#sendmessage
    """

    chat_id: int
    text: str
    parse_mode: tg_types.ParseMode | None
    entities: list[tg_types.MessageEntity] | None
    disable_web_page_preview: bool | None
    disable_notification: bool | None
    protect_content: bool | None
    message_thread_id: bool | None
    allow_sending_without_reply: bool | None
    reply_markup: Union[
        tg_types.InlineKeyboardMarkup,
        tg_types.ReplyKeyboardMarkup,
        tg_types.ReplyKeyboardRemove,
        tg_types.ForceReply,
    ] | None = None

    async def asend(self) -> SendMessageResponse:
        """Shortcut method to call sendMessage Tg web API endpoint."""
        json_payload = await self.apost_as_json('sendMessage')
        response = SendMessageResponse.parse_raw(json_payload)
        return response

    def send(self) -> SendMessageResponse:
        """Shortcut method to call sendMessage Tg web API endpoint."""
        json_payload = self.post_as_json('sendMessage')
        response = SendMessageResponse.parse_raw(json_payload)
        return response


class SendPhotoResponse(BaseTgResponse):
    result: tg_types.Message


class SendBytesPhotoRequest(BaseTgRequest):
    """Object encapsulates data for calling web API endpoint `sendPhoto`.

    Telegram web API docs:
        See here https://core.telegram.org/bots/api#sendphoto
    """

    chat_id: int
    photo: Union[
        bytes,
        Iterable[bytes],
    ]
    filename: str | None
    message_thread_id: int | None
    caption: str | None
    parse_mode: str | None
    caption_entities: list[tg_types.MessageEntity] | None
    has_spoiler: bool | None
    disable_notification: bool | None
    protect_content: bool | None
    reply_to_message_id: int | None
    allow_sending_without_reply: bool | None
    reply_markup: Union[
        tg_types.InlineKeyboardMarkup,
        tg_types.ReplyKeyboardMarkup,
        tg_types.ReplyKeyboardRemove,
        tg_types.ForceReply,
    ] | None = None

    async def asend(self) -> SendPhotoResponse:
        """Shortcut method to call sendPhoto Tg web API endpoint."""
        content = self.dict(exclude_none=True, exclude={'photo'})
        photo_bytes = io.BytesIO(self.photo)
        photo_bytes.name = self.filename
        files = {'photo': photo_bytes}
        json_payload = await self.apost_multipart_form_data('sendPhoto', content, files)
        response = SendPhotoResponse.parse_raw(json_payload)
        return response

    def send(self) -> SendPhotoResponse:
        """Shortcut method to call sendPhoto Tg web API endpoint."""
        content = self.dict(exclude_none=True, exclude={'photo'})
        photo_bytes = io.BytesIO(self.photo)
        photo_bytes.name = self.filename
        files = {'photo': photo_bytes}
        json_payload = self.post_multipart_form_data('sendPhoto', content, files)
        response = SendPhotoResponse.parse_raw(json_payload)
        return response


class SendUrlPhotoRequest(BaseTgRequest):
    """Object encapsulates data for calling web API endpoint `sendPhoto`.

    Telegram web API docs:
        See here https://core.telegram.org/bots/api#sendphoto
    """

    chat_id: int
    photo: str
    filename: str | None
    message_thread_id: int | None
    caption: str | None
    parse_mode: str | None
    caption_entities: list[tg_types.MessageEntity] | None
    has_spoiler: bool | None
    disable_notification: bool | None
    protect_content: bool | None
    reply_to_message_id: int | None
    allow_sending_without_reply: bool | None
    reply_markup: Union[
        tg_types.InlineKeyboardMarkup,
        tg_types.ReplyKeyboardMarkup,
        tg_types.ReplyKeyboardRemove,
        tg_types.ForceReply,
    ] | None = None

    async def asend(self) -> SendPhotoResponse:
        """Shortcut method to call sendPhoto Tg web API endpoint."""
        json_payload = await self.apost_as_json('sendPhoto')
        response = SendPhotoResponse.parse_raw(json_payload)
        return response

    def send(self) -> SendPhotoResponse:
        """Shortcut method to call sendPhoto Tg web API endpoint."""
        json_payload = self.post_as_json('sendPhoto')
        response = SendPhotoResponse.parse_raw(json_payload)
        return response


class SendDocumentResponse(BaseTgResponse):
    result: tg_types.Message


class SendBytesDocumentRequest(BaseTgRequest):
    """Object encapsulates data for calling web API endpoint `sendDocument`.

    Telegram web API docs:
        See here https://core.telegram.org/bots/api#senddocument
    """

    chat_id: int
    document: bytes
    filename: str | None
    message_thread_id: int | None
    thumbnail: bytes | str | None
    caption: str | None
    parse_mode: str | None
    caption_entities: list[tg_types.MessageEntity] | None
    disable_content_type_detection: bool | None
    disable_notification: bool | None
    protect_content: bool | None
    reply_to_message_id: int | None
    allow_sending_without_reply: bool | None
    reply_markup: Union[
        tg_types.InlineKeyboardMarkup,
        tg_types.ReplyKeyboardMarkup,
        tg_types.ReplyKeyboardRemove,
        tg_types.ForceReply,
    ] | None = None

    async def asend(self) -> SendDocumentResponse:
        """Shortcut method to call sendDocument Tg web API endpoint."""
        content = self.dict(exclude_none=True, exclude={'document'})
        document_bytes = io.BytesIO(self.document)
        document_bytes.name = self.filename
        files = {'document': document_bytes}
        json_payload = await self.apost_multipart_form_data('sendDocument', content, files)
        response = SendDocumentResponse.parse_raw(json_payload)
        return response

    def send(self) -> SendDocumentResponse:
        """Shortcut method to call sendDocument Tg web API endpoint."""
        content = self.dict(exclude_none=True, exclude={'document'})
        document_bytes = io.BytesIO(self.document)
        document_bytes.name = self.filename
        files = {'document': document_bytes}
        json_payload = self.post_multipart_form_data('sendDocument', content, files)
        response = SendDocumentResponse.parse_raw(json_payload)
        return response


class SendUrlDocumentRequest(BaseTgRequest):
    """Object encapsulates data for calling web API endpoint `sendDocument`.

    Telegram web API docs:
        See here https://core.telegram.org/bots/api#senddocument
    """

    chat_id: int
    document: str
    filename: str | None
    message_thread_id: int | None
    thumbnail: bytes | str | None
    caption: str | None
    parse_mode: str | None
    caption_entities: list[tg_types.MessageEntity] | None
    disable_content_type_detection: bool | None
    disable_notification: bool | None
    protect_content: bool | None
    reply_to_message_id: int | None
    allow_sending_without_reply: bool | None
    reply_markup: Union[
        tg_types.InlineKeyboardMarkup,
        tg_types.ReplyKeyboardMarkup,
        tg_types.ReplyKeyboardRemove,
        tg_types.ForceReply,
    ] | None = None

    async def asend(self) -> SendDocumentResponse:
        """Shortcut method to call sendDocument Tg web API endpoint."""
        json_payload = await self.apost_as_json('sendDocument')
        response = SendDocumentResponse.parse_raw(json_payload)
        return response

    def send(self) -> SendDocumentResponse:
        """Shortcut method to call sendDocument Tg web API endpoint."""
        json_payload = self.post_as_json('sendDocument')
        response = SendDocumentResponse.parse_raw(json_payload)
        return response


class DeleteMessageResponse(BaseTgResponse):
    result: bool


class DeleteMessageRequest(BaseTgRequest):
    """Object encapsulates data for calling web API endpoint `deleteMessage`.

    Telegram web API docs:
        See here https://core.telegram.org/bots/api#deletemessage
    """

    chat_id: int
    message_id: int

    async def asend(self) -> DeleteMessageResponse:
        """Shortcut method to call deleteMessage Tg web API endpoint."""
        json_payload = await self.apost_as_json('deleteMessage')
        response = DeleteMessageResponse.parse_raw(json_payload)
        return response

    def send(self) -> DeleteMessageResponse:
        """Shortcut method to call deleteMessage Tg web API endpoint."""
        json_payload = self.post_as_json('deleteMessage')
        response = DeleteMessageResponse.parse_raw(json_payload)
        return response


class EditMessageTextResponse(BaseTgResponse):
    result: tg_types.Message | bool


class EditMessageTextRequest(BaseTgRequest):
    """Object encapsulates data for calling web API endpoint `editMessageText`.

    Telegram web API docs:
        See here https://core.telegram.org/bots/api#editmessagetext
    """

    chat_id: int | None
    message_id: int | None
    inline_message_id: str | None
    text: str
    parse_mode: str | None
    entities: list[tg_types.MessageEntity] | None
    disable_web_page_preview: bool | None
    reply_markup: tg_types.InlineKeyboardMarkup | None

    async def asend(self) -> EditMessageTextResponse:
        """Shortcut method to call editMessageText Tg web API endpoint."""
        json_payload = await self.apost_as_json('editmessagetext')
        response = EditMessageTextResponse.parse_raw(json_payload)
        return response

    def send(self) -> EditMessageTextResponse:
        """Shortcut method to call editMessageText Tg web API endpoint."""
        json_payload = self.post_as_json('editmessagetext')
        response = EditMessageTextResponse.parse_raw(json_payload)
        return response


class EditMessageReplyMarkupResponse(BaseTgResponse):
    result: tg_types.Message | bool


class EditMessageReplyMarkupRequest(BaseTgRequest):
    """Object encapsulates data for calling web API endpoint `editMessageReplyMarkup`.

    Telegram web API docs:
        See here https://core.telegram.org/bots/api#editmessagereplymarkup
    """

    chat_id: int | None
    message_id: int | None
    inline_message_id: str | None
    reply_markup: tg_types.InlineKeyboardMarkup | None

    async def asend(self) -> EditMessageReplyMarkupResponse:
        """Shortcut method to call editMessageText Tg web API endpoint."""
        json_payload = await self.apost_as_json('editmessagereplymarkup')
        response = EditMessageReplyMarkupResponse.parse_raw(json_payload)
        return response

    def send(self) -> EditMessageReplyMarkupResponse:
        """Shortcut method to call editMessageText Tg web API endpoint."""
        json_payload = self.post_as_json('editmessagereplymarkup')
        response = EditMessageReplyMarkupResponse.parse_raw(json_payload)
        return response


class EditMessageCaptionResponse(BaseTgResponse):
    result: tg_types.Message | bool


class EditMessageCaptionRequest(BaseTgRequest):
    """Object encapsulates data for calling web API endpoint `editMessageCaption`.

    Telegram web API docs:
        See here https://core.telegram.org/bots/api#editmessagecaption
    """

    chat_id: int | None
    message_id: int | None
    inline_message_id: str | None
    caption: str
    parse_mode: str | None
    caption_entities: list[tg_types.MessageEntity] | None
    reply_markup: tg_types.InlineKeyboardMarkup | None

    async def asend(self) -> EditMessageCaptionResponse:
        """Shortcut method to call editMessageText Tg web API endpoint."""
        json_payload = await self.apost_as_json('editmessagecaption')
        response = EditMessageCaptionResponse.parse_raw(json_payload)
        return response

    def send(self) -> EditMessageCaptionResponse:
        """Shortcut method to call editMessageText Tg web API endpoint."""
        json_payload = self.post_as_json('editmessagecaption')
        response = EditMessageCaptionResponse.parse_raw(json_payload)
        return response


class EditMessageMediaResponse(BaseTgResponse):
    result: tg_types.Message | bool


class EditBytesMessageMediaRequest(BaseTgRequest):
    """Object encapsulates data for calling web API endpoint `editmessagemedia`.

    Telegram web API docs:
        See here https://core.telegram.org/bots/api#editmessagemedia
    """

    chat_id: int | None
    message_id: int | None
    inline_message_id: str | None
    media: Union[tg_types.InputMediaBytesDocument, tg_types.InputMediaBytesPhoto]
    reply_markup: tg_types.InlineKeyboardMarkup | None

    async def asend(self) -> EditMessageMediaResponse:
        """Shortcut method to call editmessagemedia Tg web API endpoint."""
        content = self.dict(exclude_none=True)

        content['media'].pop('media_content')
        media_bytes = io.BytesIO(self.media.media_content)
        files = {self.media.media: media_bytes}

        if not self.media.media.startswith('attach://'):
            content['media']['media'] = f"attach://{content['media']['media']}"

        if 'thumbnail' in content['media'] and 'thumbnail_content' in content['media']:
            content['media'].pop('thumbnail_content')
            thumbnail_bytes = io.BytesIO(self.media.thumbnail_content)
            files[self.media.thumbnail] = thumbnail_bytes

            if not self.media.thumbnail.startswith('attach://'):
                content['media']['thumbnail'] = f"attach://{content['media']['thumbnail']}"

        json_payload = await self.apost_multipart_form_data('editmessagemedia', content, files)
        response = EditMessageMediaResponse.parse_raw(json_payload)
        return response

    def send(self) -> EditMessageMediaResponse:
        """Shortcut method to call editmessagemedia Tg web API endpoint."""
        content = self.dict(exclude_none=True)

        content['media'].pop('media_content')
        media_bytes = io.BytesIO(self.media.media_content)
        files = {self.media.media: media_bytes}

        if not self.media.media.startswith('attach://'):
            content['media']['media'] = f"attach://{content['media']['media']}"

        if 'thumbnail' in content['media'] and 'thumbnail_content' in content['media']:
            content['media'].pop('thumbnail_content')
            thumbnail_bytes = io.BytesIO(self.media.thumbnail_content)
            files[self.media.thumbnail] = thumbnail_bytes

            if not self.media.thumbnail.startswith('attach://'):
                content['media']['thumbnail'] = f"attach://{content['media']['thumbnail']}"

        json_payload = self.post_multipart_form_data('editmessagemedia', content, files)
        response = EditMessageMediaResponse.parse_raw(json_payload)
        return response


class EditUrlMessageMediaRequest(BaseTgRequest):
    """Object encapsulates data for calling web API endpoint `editmessagemedia`.

    Telegram web API docs:
        See here https://core.telegram.org/bots/api#editmessagemedia
    """

    chat_id: int | None
    message_id: int | None
    inline_message_id: str | None
    media: Union[tg_types.InputMediaUrlDocument, tg_types.InputMediaUrlPhoto]
    reply_markup: tg_types.InlineKeyboardMarkup | None

    async def asend(self) -> EditMessageMediaResponse:
        """Shortcut method to call editmessagemedia Tg web API endpoint."""
        json_payload = await self.apost_as_json('editmessagemedia')
        response = EditMessageMediaResponse.parse_raw(json_payload)
        return response

    def send(self) -> EditMessageMediaResponse:
        """Shortcut method to call editmessagemedia Tg web API endpoint."""
        json_payload = self.post_as_json('editmessagemedia')
        response = EditMessageMediaResponse.parse_raw(json_payload)
        return response
