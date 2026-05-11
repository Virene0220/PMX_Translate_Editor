#!/usr/bin/env python3
"""PMX name translation helper for PMX Editor workflows.

This tool rewrites PMX text fields while preserving all geometry, physics and
binary data. It is intentionally dependency-free so it can run on a stock
Windows Python install.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import struct
import sys
import threading
import unicodedata
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable


LANG_EN = "en"
LANG_VI = "vi"
DEFAULT_CACHE_PATH = Path(__file__).with_name("translation_cache.json")
APP_ICON_ICO = "app_icon.ico"
APP_ICON_PNG = "app_icon.png"


COMMON_TRANSLATIONS_EN = {
    "センター": "center",
    "中心": "center",
    "全ての親": "motherbone",
    "全親": "motherbone",
    "上半身": "upper body",
    "上半身2": "upper body 2",
    "下半身": "lower body",
    "首": "neck",
    "頭": "head",
    "頭部": "head",
    "髪": "hair",
    "前髪": "front hair",
    "後髪": "back hair",
    "横髪": "side hair",
    "右": "right",
    "左": "left",
    "腕": "arm",
    "ひじ": "elbow",
    "肘": "elbow",
    "手首": "wrist",
    "手": "hand",
    "指": "finger",
    "親指": "thumb",
    "人指": "index finger",
    "人差指": "index finger",
    "中指": "middle finger",
    "薬指": "ring finger",
    "小指": "little finger",
    "足": "leg",
    "ひざ": "knee",
    "膝": "knee",
    "足首": "ankle",
    "つま先": "toe",
    "目": "eye",
    "眉": "eyebrow",
    "口": "mouth",
    "舌": "tongue",
    "歯": "teeth",
    "笑い": "smile",
    "笑顔": "smile",
    "怒り": "angry",
    "悲しみ": "sad",
    "照れ": "shy",
    "まばたき": "blink",
    "ウィンク": "wink",
    "あ": "a",
    "い": "i",
    "う": "u",
    "え": "e",
    "お": "o",
    "材質": "material",
    "肌": "skin",
    "顔": "face",
    "服": "clothes",
    "スカート": "skirt",
    "靴": "shoes",
    "リボン": "ribbon",
    "影": "shadow",
    "地面": "ground",
    "床": "floor",
    "壁": "wall",
    "天井": "ceiling",
    "空": "sky",
    "背景": "background",
    "ステージ": "stage",
    "ライト": "light",
    "照明": "light",
    "ガラス": "glass",
    "窓": "window",
    "扉": "door",
    "ドア": "door",
    "柱": "pillar",
    "階段": "stairs",
    "水": "water",
    "木": "tree",
    "草": "grass",
    "花": "flower",
    "表示枠": "display frame",
    "剛体": "rigid body",
    "ジョイント": "joint",
    "ボーン": "bone",
    "モーフ": "morph",
    "テクスチャ": "texture",
}

COMMON_TRANSLATIONS_VI = {
    "center": "trung tam",
    "motherbone": "xuong goc",
    "upper body": "than tren",
    "upper body 2": "than tren 2",
    "lower body": "than duoi",
    "neck": "co",
    "head": "dau",
    "hair": "toc",
    "front hair": "toc truoc",
    "back hair": "toc sau",
    "side hair": "toc ben",
    "right": "phai",
    "left": "trai",
    "arm": "tay",
    "elbow": "khuyu tay",
    "wrist": "co tay",
    "hand": "ban tay",
    "finger": "ngon tay",
    "thumb": "ngon cai",
    "index finger": "ngon tro",
    "middle finger": "ngon giua",
    "ring finger": "ngon ap ut",
    "little finger": "ngon ut",
    "leg": "chan",
    "knee": "dau goi",
    "ankle": "co chan",
    "toe": "ngon chan",
    "eye": "mat",
    "eyebrow": "long may",
    "mouth": "mieng",
    "tongue": "luoi",
    "teeth": "rang",
    "smile": "cuoi",
    "angry": "gian",
    "sad": "buon",
    "shy": "xau ho",
    "blink": "nham mat",
    "wink": "nhay mat",
    "material": "vat lieu",
    "skin": "da",
    "face": "mat",
    "clothes": "quan ao",
    "skirt": "vay",
    "shoes": "giay",
    "ribbon": "no",
    "shadow": "bong",
    "ground": "mat dat",
    "floor": "san",
    "wall": "tuong",
    "ceiling": "tran",
    "sky": "troi",
    "background": "nen",
    "stage": "san khau",
    "light": "den",
    "glass": "kinh",
    "window": "cua so",
    "door": "cua",
    "pillar": "cot",
    "stairs": "cau thang",
    "water": "nuoc",
    "tree": "cay",
    "grass": "co",
    "flower": "hoa",
    "display frame": "khung hien thi",
    "rigid body": "vat ly",
    "joint": "khop noi",
    "bone": "xuong",
    "morph": "morph",
    "texture": "texture",
}

SECTION_LABELS = {
    "model": "Model info",
    "texture": "Textures",
    "material": "Materials",
    "bone": "Bones",
    "morph": "Morphs",
    "display": "Display frames",
    "rigid_body": "Rigid bodies",
    "joint": "Joints",
    "soft_body": "Soft bodies",
}

TRANSLATABLE_SECTIONS = {
    "material",
    "bone",
    "morph",
    "display",
    "rigid_body",
    "joint",
    "soft_body",
}

DISABLED_TRANSLATION_SECTIONS = {
    "display",
    "rigid_body",
    "joint",
    "soft_body",
}

DEFAULT_TRANSLATION_SECTIONS = TRANSLATABLE_SECTIONS - DISABLED_TRANSLATION_SECTIONS

MOTION_NAME_SECTIONS = {
    "bone",
    "morph",
}


def is_motion_local_name(entry: "TextEntry") -> bool:
    return entry.section in MOTION_NAME_SECTIONS and entry.field == "local_name"


SECTION_FILTER_LABELS = {
    "material": "Objects/Materials",
    "bone": "Bones",
    "morph": "Morphs",
    "display": "Display",
    "rigid_body": "Rigid bodies",
    "joint": "Joints",
    "soft_body": "Soft bodies",
}

UI_LANGUAGE_NAMES = {
    "en": "English",
    "vi": "Tiếng Việt",
    "ru": "Русский",
}

UI_LANGUAGE_CODES = {name: code for code, name in UI_LANGUAGE_NAMES.items()}

UI_TEXT = {
    "en": {
        "title": "PMX Translate Editor",
        "open_pmx": "Open PMX",
        "ui": "UI",
        "target": "Target",
        "overwrite_local": "Overwrite local names",
        "only_empty": "Only empty fields",
        "online_fallback": "Online fallback",
        "auto_translate": "Auto Translate",
        "clear_changes": "Clear Changes",
        "save_as": "Save As",
        "translate_sections": "Translate sections",
        "section_material": "Objects/Materials",
        "section_bone": "Bones",
        "section_morph": "Morphs",
        "section_display": "Display",
        "section_rigid_body": "Rigid bodies",
        "section_joint": "Joints",
        "section_soft_body": "Soft bodies",
        "sync_name_fields": "Translate local name and write both fields",
        "translate_textures": "Copy translated texture files and update PMX paths",
        "delete_original_textures": "Delete original texture files after successful copy",
        "column_object": "Object",
        "column_field": "Field",
        "column_original": "Original",
        "column_new": "New value",
        "original": "Original",
        "new": "New",
        "apply_selected": "Apply Selected",
        "ready": "Open a PMX file to start.",
        "loaded": "Loaded {name}: {count} text field(s).",
        "pending": "{count} pending change(s).",
        "pending_review": "{count} pending change(s). {review} still need review.",
        "select_section": "Select at least one section or texture translation.",
        "translating": "Translating...",
        "translating_progress": "Translating {done}/{total}...",
        "translate_failed": "Translate failed: {error}",
        "cleared": "Pending changes cleared.",
        "saved": "Saved {name} with {count} change(s).",
        "copied": " Copied {count} texture file(s).",
        "deleted": " Deleted {count} old texture file(s).",
        "delete_title": "Delete original textures",
        "delete_confirm": (
            "Delete old texture files after they are copied successfully?\n\n"
            "Files still referenced by the PMX or outside the model folder will be kept."
        ),
        "open_error": "Open PMX",
        "save_error": "Save PMX",
        "texture_copy": "Texture copy",
        "pmx_files": "PMX files",
        "all_files": "All files",
    },
    "vi": {
        "title": "PMX Translate Editor",
        "open_pmx": "Mở PMX",
        "ui": "Ngôn ngữ",
        "target": "Dịch sang ngôn ngữ",
        "overwrite_local": "Ghi đè tên local",
        "only_empty": "Chỉ điền ô trống",
        "online_fallback": "Dịch từ điển online",
        "auto_translate": "Tự động dịch",
        "clear_changes": "Xóa thay đổi",
        "save_as": "Lưu tại",
        "translate_sections": "Nhóm cần dịch",
        "section_material": "Object/Material",
        "section_bone": "Bone",
        "section_morph": "Morph",
        "section_display": "Khung hiển thị",
        "section_rigid_body": "Rigid body",
        "section_joint": "Joint",
        "section_soft_body": "Soft body",
        "sync_name_fields": "Dịch tên local và ghi vào cả hai ô tên",
        "translate_textures": "Copy texture đã dịch và cập nhật path PMX",
        "delete_original_textures": "Xóa texture gốc sau khi copy thành công",
        "column_object": "Đối tượng",
        "column_field": "Trường",
        "column_original": "Gốc",
        "column_new": "Giá trị mới",
        "original": "Gốc",
        "new": "Mới",
        "apply_selected": "Áp dụng dòng chọn",
        "ready": "Mở file PMX để bắt đầu.",
        "loaded": "Đã mở {name}: {count} trường text.",
        "pending": "{count} thay đổi đang chờ.",
        "pending_review": "{count} thay đổi đang chờ. {review} dòng cần kiểm tra.",
        "select_section": "Hãy chọn ít nhất một nhóm hoặc chế độ dịch texture.",
        "translating": "Đang dịch...",
        "translating_progress": "Đang dịch {done}/{total}...",
        "translate_failed": "Dịch lỗi: {error}",
        "cleared": "Đã xóa các thay đổi đang chờ.",
        "saved": "Đã lưu {name} với {count} thay đổi.",
        "copied": " Đã copy {count} file texture.",
        "deleted": " Đã xóa {count} file texture cũ.",
        "delete_title": "Xóa texture gốc",
        "delete_confirm": (
            "Xóa các file texture cũ sau khi copy thành công?\n\n"
            "File còn được PMX tham chiếu hoặc nằm ngoài thư mục model sẽ được giữ lại."
        ),
        "open_error": "Mở PMX",
        "save_error": "Lưu PMX",
        "texture_copy": "Copy texture",
        "pmx_files": "File PMX",
        "all_files": "Tất cả file",
    },
    "ru": {
        "title": "PMX Translate Editor",
        "open_pmx": "Открыть PMX",
        "ui": "Интерфейс",
        "target": "Язык перевода",
        "overwrite_local": "Перезаписать local names",
        "only_empty": "Только пустые поля",
        "online_fallback": "Онлайн-перевод при необходимости",
        "auto_translate": "Автоперевод",
        "clear_changes": "Очистить изменения",
        "save_as": "Сохранить как",
        "translate_sections": "Разделы для перевода",
        "section_material": "Объекты/Материалы",
        "section_bone": "Кости",
        "section_morph": "Морфы",
        "section_display": "Отображение",
        "section_rigid_body": "Rigid bodies",
        "section_joint": "Joints",
        "section_soft_body": "Soft bodies",
        "sync_name_fields": "Перевести local name и записать в оба поля",
        "translate_textures": "Скопировать переведенные текстуры и обновить пути PMX",
        "delete_original_textures": "Удалить старые текстуры после успешного копирования",
        "column_object": "Объект",
        "column_field": "Поле",
        "column_original": "Исходное",
        "column_new": "Новое значение",
        "original": "Исходное",
        "new": "Новое",
        "apply_selected": "Применить выбранное",
        "ready": "Откройте PMX-файл, чтобы начать.",
        "loaded": "Загружено {name}: {count} текстовых полей.",
        "pending": "{count} изменений ожидает сохранения.",
        "pending_review": "{count} изменений ожидает сохранения. {review} требуют проверки.",
        "select_section": "Выберите хотя бы один раздел или перевод текстур.",
        "translating": "Перевод...",
        "translating_progress": "Перевод {done}/{total}...",
        "translate_failed": "Ошибка перевода: {error}",
        "cleared": "Ожидающие изменения очищены.",
        "saved": "Сохранено {name}, изменений: {count}.",
        "copied": " Скопировано текстур: {count}.",
        "deleted": " Удалено старых текстур: {count}.",
        "delete_title": "Удалить старые текстуры",
        "delete_confirm": (
            "Удалить старые файлы текстур после успешного копирования?\n\n"
            "Файлы, которые все еще используются PMX или находятся вне папки модели, будут сохранены."
        ),
        "open_error": "Открыть PMX",
        "save_error": "Сохранить PMX",
        "texture_copy": "Копирование текстур",
        "pmx_files": "PMX файлы",
        "all_files": "Все файлы",
    },
}


@dataclass
class TextEntry:
    id: int
    section: str
    index: int
    field: str
    offset: int
    byte_length: int
    encoding: str
    value: str

    @property
    def raw_start(self) -> int:
        return self.offset + 4

    @property
    def raw_end(self) -> int:
        return self.raw_start + self.byte_length

    @property
    def label(self) -> str:
        label = SECTION_LABELS.get(self.section, self.section)
        if self.index >= 0:
            return f"{label} #{self.index}"
        return label


class PmxFormatError(RuntimeError):
    pass


class PmxReader:
    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0
        self.entries: list[TextEntry] = []
        self.text_encoding = "utf-16-le"
        self.vertex_index_size = 4
        self.texture_index_size = 4
        self.material_index_size = 4
        self.bone_index_size = 4
        self.morph_index_size = 4
        self.rigid_body_index_size = 4
        self.additional_uv_count = 0
        self.version = 0.0

    def parse(self) -> list[TextEntry]:
        self._parse_header()
        self._read_text("model", -1, "local_name")
        self._read_text("model", -1, "universal_name")
        self._read_text("model", -1, "local_comment")
        self._read_text("model", -1, "universal_comment")
        self._parse_vertices()
        self._parse_faces()
        self._parse_textures()
        self._parse_materials()
        self._parse_bones()
        self._parse_morphs()
        self._parse_display_frames()
        self._parse_rigid_bodies()
        self._parse_joints()
        self._parse_soft_bodies_if_present()
        return self.entries

    def _need(self, size: int) -> None:
        if self.pos + size > len(self.data):
            raise PmxFormatError(f"Unexpected end of file at byte {self.pos}.")

    def _read(self, size: int) -> bytes:
        self._need(size)
        chunk = self.data[self.pos : self.pos + size]
        self.pos += size
        return chunk

    def _skip(self, size: int) -> None:
        self._need(size)
        self.pos += size

    def _u8(self) -> int:
        return self._read(1)[0]

    def _i32(self) -> int:
        return struct.unpack_from("<i", self._read(4))[0]

    def _parse_header(self) -> None:
        magic = self._read(4)
        if magic != b"PMX ":
            raise PmxFormatError("This is not a PMX file.")
        self.version = struct.unpack_from("<f", self._read(4))[0]
        setting_count = self._u8()
        settings = self._read(setting_count)
        if setting_count < 8:
            raise PmxFormatError("PMX header is missing global settings.")
        self.text_encoding = "utf-16-le" if settings[0] == 0 else "utf-8"
        self.additional_uv_count = settings[1]
        self.vertex_index_size = settings[2]
        self.texture_index_size = settings[3]
        self.material_index_size = settings[4]
        self.bone_index_size = settings[5]
        self.morph_index_size = settings[6]
        self.rigid_body_index_size = settings[7]

    def _read_text(self, section: str, index: int, field: str) -> str:
        offset = self.pos
        byte_length = self._i32()
        if byte_length < 0:
            raise PmxFormatError(f"Negative string length at byte {offset}.")
        raw = self._read(byte_length)
        try:
            value = raw.decode(self.text_encoding)
        except UnicodeDecodeError:
            value = raw.decode(self.text_encoding, errors="replace")
        self.entries.append(
            TextEntry(
                id=len(self.entries),
                section=section,
                index=index,
                field=field,
                offset=offset,
                byte_length=byte_length,
                encoding=self.text_encoding,
                value=value,
            )
        )
        return value

    def _idx(self, size: int) -> None:
        self._skip(size)

    def _parse_vertices(self) -> None:
        count = self._i32()
        for _ in range(count):
            self._skip(12 + 12 + 8 + self.additional_uv_count * 16)
            deform = self._u8()
            if deform == 0:
                self._idx(self.bone_index_size)
            elif deform == 1:
                self._idx(self.bone_index_size)
                self._idx(self.bone_index_size)
                self._skip(4)
            elif deform == 2:
                self._skip(self.bone_index_size * 4 + 16)
            elif deform == 3:
                self._skip(self.bone_index_size * 2 + 4 + 36)
            elif deform == 4:
                self._skip(self.bone_index_size * 4 + 16)
            else:
                raise PmxFormatError(f"Unsupported vertex deform type {deform}.")
            self._skip(4)

    def _parse_faces(self) -> None:
        count = self._i32()
        self._skip(count * self.vertex_index_size)

    def _parse_textures(self) -> None:
        count = self._i32()
        for index in range(count):
            self._read_text("texture", index, "path")

    def _parse_materials(self) -> None:
        count = self._i32()
        for index in range(count):
            self._read_text("material", index, "local_name")
            self._read_text("material", index, "universal_name")
            self._skip(4 * 4 + 3 * 4 + 4 + 3 * 4 + 1 + 4 * 4 + 4)
            self._idx(self.texture_index_size)
            self._idx(self.texture_index_size)
            self._skip(1)
            toon_flag = self._u8()
            if toon_flag == 0:
                self._idx(self.texture_index_size)
            else:
                self._skip(1)
            self._read_text("material", index, "memo")
            self._skip(4)

    def _parse_bones(self) -> None:
        count = self._i32()
        for index in range(count):
            self._read_text("bone", index, "local_name")
            self._read_text("bone", index, "universal_name")
            self._skip(12)
            self._idx(self.bone_index_size)
            self._skip(4)
            flags = struct.unpack_from("<H", self._read(2))[0]
            if flags & 0x0001:
                self._idx(self.bone_index_size)
            else:
                self._skip(12)
            if flags & 0x0100 or flags & 0x0200:
                self._idx(self.bone_index_size)
                self._skip(4)
            if flags & 0x0400:
                self._skip(12)
            if flags & 0x0800:
                self._skip(24)
            if flags & 0x2000:
                self._skip(4)
            if flags & 0x0020:
                self._idx(self.bone_index_size)
                self._skip(4 + 4)
                link_count = self._i32()
                for _ in range(link_count):
                    self._idx(self.bone_index_size)
                    has_limit = self._u8()
                    if has_limit:
                        self._skip(24)

    def _parse_morphs(self) -> None:
        count = self._i32()
        for index in range(count):
            self._read_text("morph", index, "local_name")
            self._read_text("morph", index, "universal_name")
            self._skip(1)
            morph_type = self._u8()
            offset_count = self._i32()
            for _ in range(offset_count):
                if morph_type == 0:
                    self._skip(self.morph_index_size + 4)
                elif morph_type == 1:
                    self._skip(self.vertex_index_size + 12)
                elif morph_type == 2:
                    self._skip(self.bone_index_size + 12 + 16)
                elif 3 <= morph_type <= 7:
                    self._skip(self.vertex_index_size + 16)
                elif morph_type == 8:
                    self._skip(self.material_index_size + 1 + 4 * (4 + 4 + 3 + 4 + 1 + 4 + 4 + 4))
                elif morph_type == 9:
                    self._skip(self.morph_index_size + 4)
                elif morph_type == 10:
                    self._skip(self.rigid_body_index_size + 1 + 12 + 12)
                else:
                    raise PmxFormatError(f"Unsupported morph type {morph_type}.")

    def _parse_display_frames(self) -> None:
        count = self._i32()
        for index in range(count):
            self._read_text("display", index, "local_name")
            self._read_text("display", index, "universal_name")
            self._skip(1)
            item_count = self._i32()
            for _ in range(item_count):
                item_type = self._u8()
                if item_type == 0:
                    self._idx(self.bone_index_size)
                elif item_type == 1:
                    self._idx(self.morph_index_size)
                else:
                    raise PmxFormatError(f"Unsupported display frame item type {item_type}.")

    def _parse_rigid_bodies(self) -> None:
        count = self._i32()
        for index in range(count):
            self._read_text("rigid_body", index, "local_name")
            self._read_text("rigid_body", index, "universal_name")
            self._skip(self.bone_index_size + 1 + 2 + 1 + 12 + 12 + 12 + 4 * 5 + 1)

    def _parse_joints(self) -> None:
        count = self._i32()
        for index in range(count):
            self._read_text("joint", index, "local_name")
            self._read_text("joint", index, "universal_name")
            self._skip(1 + self.rigid_body_index_size * 2 + 12 + 12 + 12 + 12 + 12 + 12 + 12 + 12)

    def _parse_soft_bodies_if_present(self) -> None:
        if self.pos >= len(self.data):
            return
        start = self.pos
        try:
            count = self._i32()
            if count < 0 or count > 100000:
                self.pos = start
                return
            for index in range(count):
                self._read_text("soft_body", index, "local_name")
                self._read_text("soft_body", index, "universal_name")
                # PMX 2.1 soft-body records are large and rarely used for name
                # translation. Stop after collecting names to avoid corrupting
                # offsets in unknown vendor extensions.
                break
        except PmxFormatError:
            self.pos = start


def parse_pmx(data: bytes) -> list[TextEntry]:
    return PmxReader(data).parse()


def resource_path(name: str) -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    bundled = base / name
    if bundled.exists():
        return bundled
    return Path(__file__).resolve().parent / name


def write_replacements(data: bytes, entries: list[TextEntry], replacements: dict[int, str]) -> bytes:
    chunks: list[bytes] = []
    cursor = 0
    for entry in sorted(entries, key=lambda item: item.offset):
        if entry.id not in replacements:
            continue
        if is_motion_local_name(entry):
            continue
        new_value = replacements[entry.id]
        encoded = new_value.encode(entry.encoding)
        chunks.append(data[cursor : entry.offset])
        chunks.append(struct.pack("<i", len(encoded)))
        chunks.append(encoded)
        cursor = entry.raw_end
    chunks.append(data[cursor:])
    return b"".join(chunks)


def strip_vietnamese_accents(text: str) -> str:
    text = text.replace("\u0111", "d").replace("\u0110", "D")
    normalized = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")


def has_cjk(text: str) -> bool:
    return bool(re.search(r"[\u3040-\u30ff\u3400-\u9fff]", text))


def normalize_ascii_spacing(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"[_\-]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _longest_dictionary_translate(text: str, dictionary: dict[str, str]) -> str:
    if not text:
        return text
    keys = sorted(dictionary, key=len, reverse=True)
    result: list[str] = []
    pos = 0
    while pos < len(text):
        matched = False
        for key in keys:
            if text.startswith(key, pos):
                result.append(" " + dictionary[key] + " ")
                pos += len(key)
                matched = True
                break
        if not matched:
            result.append(text[pos])
            pos += 1
    return "".join(result)


def translate_name(text: str, language: str) -> str:
    text = normalize_ascii_spacing(text)
    translated = _longest_dictionary_translate(text, COMMON_TRANSLATIONS_EN)
    translated = normalize_ascii_spacing(translated)
    translated_lower = translated.lower()

    if language == LANG_VI:
        translated_lower = _longest_dictionary_translate(translated_lower, COMMON_TRANSLATIONS_VI)
        translated_lower = strip_vietnamese_accents(translated_lower)

    translated_lower = normalize_ascii_spacing(translated_lower)
    translated_lower = re.sub(r"\s+([0-9]+)$", r" \1", translated_lower)
    return translated_lower or text


def clean_machine_translation(text: str, language: str) -> str:
    text = normalize_ascii_spacing(text)
    text = text.strip(" '\"\t\r\n")
    text = re.sub(r"\s+([0-9]+)$", r" \1", text)
    text = text.lower()
    if language == LANG_VI:
        text = strip_vietnamese_accents(text)
    return normalize_ascii_spacing(text)


def load_translation_cache(path: Path | None = None) -> dict[str, str]:
    cache_path = path or DEFAULT_CACHE_PATH
    if not cache_path.exists():
        return {}
    try:
        raw = json.loads(cache_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(raw, dict):
        return {}
    return {str(key): str(value) for key, value in raw.items()}


def save_translation_cache(cache: dict[str, str], path: Path | None = None) -> None:
    cache_path = path or DEFAULT_CACHE_PATH
    cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def machine_translate_text(
    text: str,
    language: str,
    source_language: str = "auto",
    cache: dict[str, str] | None = None,
    timeout: float = 10.0,
) -> str:
    normalized = normalize_ascii_spacing(text)
    if not normalized:
        return normalized
    cache_key = f"google|{source_language}|{language}|{normalized}"
    if cache is not None and cache_key in cache:
        return cache[cache_key]

    params = urllib.parse.urlencode(
        {
            "client": "gtx",
            "sl": source_language,
            "tl": language,
            "dt": "t",
            "q": normalized,
        }
    )
    url = "https://translate.googleapis.com/translate_a/single?" + params
    request = urllib.request.Request(url, headers={"User-Agent": "PMX-Translate-Editor/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))

    translated = ""
    if payload and isinstance(payload[0], list):
        translated = "".join(part[0] for part in payload[0] if part and part[0])
    translated = clean_machine_translation(translated, language)
    if cache is not None and translated:
        cache[cache_key] = translated
    return translated


def translate_name_with_optional_online(
    text: str,
    language: str,
    online_fallback: bool = False,
    source_language: str = "auto",
    cache: dict[str, str] | None = None,
) -> str:
    translated = translate_name(text, language)
    if not online_fallback or not has_cjk(translated):
        return translated
    try:
        machine = machine_translate_text(text, language, source_language=source_language, cache=cache)
    except Exception:
        return translated
    return machine or translated


def sanitize_filename_stem(text: str) -> str:
    text = normalize_ascii_spacing(text)
    text = re.sub(r'[<>:"/\\|?*\x00-\x1f]+', " ", text)
    text = re.sub(r"\s+", "_", text).strip(" ._")
    return text or "texture"


def split_pmx_texture_path(path: str) -> tuple[str, str, str]:
    separator = "\\" if "\\" in path and "/" not in path else "/"
    normalized = path.replace("\\", "/")
    directory, sep, filename = normalized.rpartition("/")
    if not sep:
        return "", filename, separator
    return directory, filename, separator


def join_pmx_texture_path(directory: str, filename: str, separator: str) -> str:
    if not directory:
        return filename
    return directory.replace("/", separator) + separator + filename


def translated_texture_path(
    texture_path: str,
    language: str,
    online_fallback: bool = False,
    source_language: str = "auto",
    cache: dict[str, str] | None = None,
) -> str:
    directory, filename, separator = split_pmx_texture_path(texture_path)
    if not filename or filename in {".", ".."}:
        return texture_path
    stem, extension = os.path.splitext(filename)
    if not stem:
        return texture_path
    translated = translate_name_with_optional_online(
        stem,
        language,
        online_fallback=online_fallback,
        source_language=source_language,
        cache=cache,
    )
    new_filename = sanitize_filename_stem(translated) + extension.lower()
    return join_pmx_texture_path(directory, new_filename, separator)


def uniquify_texture_paths(paths_by_id: dict[int, str]) -> dict[int, str]:
    used: set[str] = set()
    unique: dict[int, str] = {}
    for entry_id, path in paths_by_id.items():
        key = path.replace("\\", "/").lower()
        if key not in used:
            used.add(key)
            unique[entry_id] = path
            continue
        directory, filename, separator = split_pmx_texture_path(path)
        stem, extension = os.path.splitext(filename)
        counter = 2
        while True:
            candidate = join_pmx_texture_path(directory, f"{stem}_{counter}{extension}", separator)
            candidate_key = candidate.replace("\\", "/").lower()
            if candidate_key not in used:
                used.add(candidate_key)
                unique[entry_id] = candidate
                break
            counter += 1
    return unique


def build_texture_path_replacements(
    entries: list[TextEntry],
    language: str,
    online_fallback: bool = False,
    source_language: str = "auto",
    cache: dict[str, str] | None = None,
) -> dict[int, str]:
    proposed: dict[int, str] = {}
    for entry in entries:
        if entry.section != "texture" or entry.field != "path":
            continue
        path = entry.value.strip()
        if not path:
            continue
        new_path = translated_texture_path(
            path,
            language,
            online_fallback=online_fallback,
            source_language=source_language,
            cache=cache,
        )
        if new_path != entry.value:
            proposed[entry.id] = new_path
    return uniquify_texture_paths(proposed)


def resolve_texture_file(base_dir: Path, pmx_texture_path: str) -> Path:
    normalized = pmx_texture_path.replace("\\", os.sep).replace("/", os.sep)
    path = Path(normalized)
    if path.is_absolute():
        return path
    return base_dir / path


def copy_replaced_textures(
    source_pmx_path: Path,
    output_pmx_path: Path,
    entries: list[TextEntry],
    replacements: dict[int, str],
    delete_originals: bool = False,
) -> tuple[int, int, list[str]]:
    source_base = source_pmx_path.parent
    output_base = output_pmx_path.parent
    copied = 0
    deleted = 0
    warnings: list[str] = []
    final_texture_paths = {
        replacements.get(entry.id, entry.value).replace("\\", "/").lower()
        for entry in entries
        if entry.section == "texture" and entry.field == "path"
    }
    delete_candidates: dict[Path, str] = {}

    for entry in entries:
        if entry.section != "texture" or entry.field != "path" or entry.id not in replacements:
            continue
        source_file = resolve_texture_file(source_base, entry.value)
        dest_file = resolve_texture_file(output_base, replacements[entry.id])
        if source_file == dest_file:
            continue
        if not source_file.exists():
            warnings.append(f"Missing texture: {entry.value}")
            continue
        try:
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            if not dest_file.exists():
                shutil.copy2(source_file, dest_file)
                copied += 1
            if delete_originals and dest_file.exists():
                old_key = entry.value.replace("\\", "/").lower()
                if old_key in final_texture_paths:
                    warnings.append(f"Kept still-referenced texture: {entry.value}")
                else:
                    delete_candidates[source_file] = entry.value
        except OSError as exc:
            warnings.append(f"Could not copy {entry.value}: {exc}")

    if delete_originals:
        source_base_resolved = source_base.resolve()
        for source_file, original_path in delete_candidates.items():
            try:
                resolved_source = source_file.resolve()
                if not resolved_source.is_relative_to(source_base_resolved):
                    warnings.append(f"Kept outside model folder: {original_path}")
                    continue
                if resolved_source.exists():
                    resolved_source.unlink()
                    deleted += 1
            except OSError as exc:
                warnings.append(f"Could not delete {original_path}: {exc}")
    return copied, deleted, warnings


def has_texture_replacements(entries: list[TextEntry], replacements: dict[int, str]) -> bool:
    return any(
        entry.section == "texture" and entry.field == "path" and entry.id in replacements
        for entry in entries
    )


def should_translate_entry(
    entry: TextEntry,
    include_comments: bool,
    overwrite_local: bool,
    translate_sections: set[str] | None = None,
) -> bool:
    if entry.section == "model":
        return False
    if entry.section in DISABLED_TRANSLATION_SECTIONS:
        return False
    if translate_sections is not None and entry.section not in translate_sections:
        return False
    if "comment" in entry.field:
        return include_comments
    if entry.section == "texture":
        return False
    if is_motion_local_name(entry):
        return False
    if entry.field == "local_name" and not overwrite_local:
        return False
    if entry.field in {"memo", "path"}:
        return False
    return True


def default_source_for_entry(entry: TextEntry, all_entries: list[TextEntry]) -> str:
    if entry.value.strip():
        return entry.value
    if entry.field != "universal_name":
        return entry.value
    for other in all_entries:
        if (
            other.section == entry.section
            and other.index == entry.index
            and other.field == "local_name"
            and other.value.strip()
        ):
            return other.value
    return entry.value


def build_auto_replacements(
    entries: list[TextEntry],
    language: str,
    include_comments: bool = False,
    overwrite_local: bool = False,
    only_empty: bool = False,
    online_fallback: bool = False,
    source_language: str = "auto",
    cache: dict[str, str] | None = None,
    translate_sections: set[str] | None = None,
    sync_name_fields: bool = False,
    translate_textures: bool = False,
    progress_callback: Callable[[int, int], None] | None = None,
) -> dict[int, str]:
    if sync_name_fields:
        replacements = build_synced_name_replacements(
            entries,
            language,
            online_fallback=online_fallback,
            source_language=source_language,
            cache=cache,
            translate_sections=translate_sections,
            progress_callback=progress_callback,
        )
        if translate_textures:
            replacements.update(
                build_texture_path_replacements(
                    entries,
                    language,
                    online_fallback=online_fallback,
                    source_language=source_language,
                    cache=cache,
                )
            )
        return replacements

    replacements: dict[int, str] = {}
    candidates = [
        entry
        for entry in entries
        if should_translate_entry(entry, include_comments, overwrite_local, translate_sections)
        and not (only_empty and entry.value.strip())
    ]
    translated_sources: dict[str, str] = {}
    total = len(candidates)

    for index, entry in enumerate(candidates, start=1):
        source = default_source_for_entry(entry, entries)
        if source in translated_sources:
            translated = translated_sources[source]
        else:
            translated = translate_name_with_optional_online(
                source,
                language,
                online_fallback=online_fallback,
                source_language=source_language,
                cache=cache,
            )
            translated_sources[source] = translated
        if translated != entry.value:
            replacements[entry.id] = translated
        if progress_callback is not None:
            progress_callback(index, total)
    if translate_textures:
        replacements.update(
            build_texture_path_replacements(
                entries,
                language,
                online_fallback=online_fallback,
                source_language=source_language,
                cache=cache,
            )
        )
    return replacements


def build_synced_name_replacements(
    entries: list[TextEntry],
    language: str,
    online_fallback: bool = False,
    source_language: str = "auto",
    cache: dict[str, str] | None = None,
    translate_sections: set[str] | None = None,
    progress_callback: Callable[[int, int], None] | None = None,
) -> dict[int, str]:
    pairs: dict[tuple[str, int], dict[str, TextEntry]] = {}
    for entry in entries:
        if entry.section == "model":
            continue
        if entry.section in DISABLED_TRANSLATION_SECTIONS:
            continue
        if translate_sections is not None and entry.section not in translate_sections:
            continue
        if entry.field not in {"local_name", "universal_name"}:
            continue
        pairs.setdefault((entry.section, entry.index), {})[entry.field] = entry

    replacements: dict[int, str] = {}
    translated_sources: dict[str, str] = {}
    items = list(pairs.values())
    total = len(items)
    for index, pair in enumerate(items, start=1):
        local_entry = pair.get("local_name")
        universal_entry = pair.get("universal_name")
        source = ""
        if local_entry is not None and local_entry.value.strip():
            source = local_entry.value
        elif universal_entry is not None:
            source = universal_entry.value
        if not source.strip():
            if progress_callback is not None:
                progress_callback(index, total)
            continue

        if source in translated_sources:
            translated = translated_sources[source]
        else:
            translated = translate_name_with_optional_online(
                source,
                language,
                online_fallback=online_fallback,
                source_language=source_language,
                cache=cache,
            )
            translated_sources[source] = translated

        target_entries = [universal_entry]
        if local_entry is not None and not is_motion_local_name(local_entry):
            target_entries.append(local_entry)
        for entry in target_entries:
            if entry is not None and translated != entry.value:
                replacements[entry.id] = translated
        if progress_callback is not None:
            progress_callback(index, total)
    return replacements


def count_untranslated_cjk(replacements: dict[int, str]) -> int:
    return sum(1 for value in replacements.values() if has_cjk(value))


def parse_section_filter(value: str | None) -> set[str] | None:
    if value is None or not value.strip() or value.strip().lower() == "all":
        return None
    aliases = {
        "object": "material",
        "objects": "material",
        "materials": "material",
        "material": "material",
        "bone": "bone",
        "bones": "bone",
        "morph": "morph",
        "morphs": "morph",
        "display": "display",
        "frames": "display",
        "rigid": "rigid_body",
        "rigid_body": "rigid_body",
        "rigid_bodies": "rigid_body",
        "physics": "rigid_body",
        "joint": "joint",
        "joints": "joint",
        "soft": "soft_body",
        "soft_body": "soft_body",
        "soft_bodies": "soft_body",
    }
    selected: set[str] = set()
    invalid: list[str] = []
    for part in re.split(r"[,; ]+", value.strip().lower()):
        if not part:
            continue
        section = aliases.get(part)
        if section is None:
            invalid.append(part)
        else:
            selected.add(section)
    if invalid:
        valid = ", ".join(sorted(aliases))
        raise ValueError(f"Unknown section(s): {', '.join(invalid)}. Valid values: all, {valid}")
    return selected or None


def run_cli(args: argparse.Namespace) -> int:
    input_path = Path(args.input)
    data = input_path.read_bytes()
    entries = parse_pmx(data)
    cache_path = Path(args.cache) if args.cache else DEFAULT_CACHE_PATH
    cache = load_translation_cache(cache_path) if args.online else None
    translate_sections = parse_section_filter(args.sections)
    translate_textures = args.translate_textures or args.delete_original_textures
    replacements = build_auto_replacements(
        entries,
        args.language,
        include_comments=False,
        overwrite_local=args.overwrite_local,
        only_empty=args.only_empty,
        online_fallback=args.online,
        source_language=args.source_language,
        cache=cache,
        translate_sections=translate_sections,
        sync_name_fields=args.sync_name_fields,
        translate_textures=translate_textures,
    )
    if cache is not None:
        save_translation_cache(cache, cache_path)
    if args.dry_run:
        for entry in entries:
            if entry.id in replacements:
                print(f"{entry.label} {entry.field}: {entry.value!r} -> {replacements[entry.id]!r}")
        print(f"{len(replacements)} field(s) would be changed.")
        remaining = count_untranslated_cjk(replacements)
        if remaining:
            print(f"{remaining} translated field(s) still contain CJK characters and need manual review.")
        return 0

    output_path = Path(args.output) if args.output else input_path.with_name(input_path.stem + f".{args.language}.pmx")
    if not output_path.is_absolute():
        output_path = Path.cwd() / output_path
    output_path.write_bytes(write_replacements(data, entries, replacements))
    copied = 0
    deleted = 0
    warnings: list[str] = []
    if translate_textures:
        copied, deleted, warnings = copy_replaced_textures(
            input_path,
            output_path,
            entries,
            replacements,
            delete_originals=args.delete_original_textures,
        )
    print(f"Wrote {output_path}")
    print(f"Changed {len(replacements)} field(s).")
    if translate_textures:
        print(f"Copied {copied} texture file(s).")
        if args.delete_original_textures:
            print(f"Deleted {deleted} original texture file(s).")
        for warning in warnings:
            print(f"Warning: {warning}")
    return 0


class PmxTranslatorApp:
    def __init__(self) -> None:
        import tkinter as tk
        from tkinter import ttk

        self.tk = tk
        self.ttk = ttk
        self.root = tk.Tk()
        self.root.geometry("1080x680")
        self.icon_photo = None
        self.configure_app_icon()
        self.data: bytes | None = None
        self.entries: list[TextEntry] = []
        self.replacements: dict[int, str] = {}
        self.path: Path | None = None
        self.selected_id: int | None = None
        self.is_translating = False

        self.ui_language_var = tk.StringVar(value=UI_LANGUAGE_NAMES["en"])
        self.language_var = tk.StringVar(value=LANG_EN)
        self.overwrite_local_var = tk.BooleanVar(value=False)
        self.sync_name_fields_var = tk.BooleanVar(value=False)
        self.translate_textures_var = tk.BooleanVar(value=False)
        self.delete_original_textures_var = tk.BooleanVar(value=False)
        self.only_empty_var = tk.BooleanVar(value=False)
        self.online_fallback_var = tk.BooleanVar(value=False)
        self.section_vars = {
            section: tk.BooleanVar(value=section in DEFAULT_TRANSLATION_SECTIONS)
            for section in TRANSLATABLE_SECTIONS
        }
        self.status_var = tk.StringVar(value="")
        self.original_var = tk.StringVar(value="")
        self.new_value_var = tk.StringVar(value="")
        self.section_checkbuttons: dict[str, object] = {}

        self._build_ui()
        self.apply_ui_language()

    def configure_app_icon(self) -> None:
        ico_path = resource_path(APP_ICON_ICO)
        if ico_path.exists():
            try:
                self.root.iconbitmap(default=str(ico_path))
                return
            except Exception:
                pass
        png_path = resource_path(APP_ICON_PNG)
        if png_path.exists():
            try:
                self.icon_photo = self.tk.PhotoImage(file=str(png_path))
                self.root.iconphoto(True, self.icon_photo)
            except Exception:
                self.icon_photo = None

    def _build_ui(self) -> None:
        tk = self.tk
        ttk = self.ttk

        root = self.root
        root.columnconfigure(0, weight=1)
        root.rowconfigure(2, weight=1)

        toolbar = ttk.Frame(root, padding=8)
        toolbar.grid(row=0, column=0, sticky="ew")
        toolbar.columnconfigure(11, weight=1)

        self.open_button = ttk.Button(toolbar, command=self.open_file)
        self.open_button.grid(row=0, column=0, padx=(0, 6))
        self.ui_label = ttk.Label(toolbar)
        self.ui_label.grid(row=0, column=1, padx=(0, 4))
        self.ui_combo = ttk.Combobox(toolbar, textvariable=self.ui_language_var, state="readonly", width=12)
        self.ui_combo["values"] = tuple(UI_LANGUAGE_NAMES.values())
        self.ui_combo.grid(row=0, column=2, padx=(0, 8))
        self.ui_combo.bind("<<ComboboxSelected>>", self.on_ui_language_changed)
        self.target_label = ttk.Label(toolbar)
        self.target_label.grid(row=0, column=3, padx=(0, 4))
        lang = ttk.Combobox(toolbar, textvariable=self.language_var, state="readonly", width=22)
        lang["values"] = (LANG_EN, LANG_VI)
        lang.grid(row=0, column=4, padx=(0, 8))
        self.overwrite_local_check = ttk.Checkbutton(toolbar, variable=self.overwrite_local_var)
        self.overwrite_local_check.grid(row=0, column=5, padx=(0, 8))
        self.only_empty_check = ttk.Checkbutton(toolbar, variable=self.only_empty_var)
        self.only_empty_check.grid(row=0, column=6, padx=(0, 8))
        self.online_fallback_check = ttk.Checkbutton(toolbar, variable=self.online_fallback_var)
        self.online_fallback_check.grid(row=0, column=7, padx=(0, 8))
        self.auto_button = ttk.Button(toolbar, command=self.auto_translate)
        self.auto_button.grid(row=0, column=8, padx=(0, 6))
        self.clear_button = ttk.Button(toolbar, command=self.clear_changes)
        self.clear_button.grid(row=0, column=9, padx=(0, 6))
        self.save_button = ttk.Button(toolbar, command=self.save_as)
        self.save_button.grid(row=0, column=10, padx=(0, 6))

        self.filters = ttk.LabelFrame(root, padding=(8, 4, 8, 8))
        self.filters.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 8))
        for col, section in enumerate(
            ("material", "bone", "morph", "display", "rigid_body", "joint", "soft_body")
        ):
            checkbutton = ttk.Checkbutton(
                self.filters,
                variable=self.section_vars[section],
            )
            if section in DISABLED_TRANSLATION_SECTIONS:
                self.section_vars[section].set(False)
                checkbutton.configure(state="disabled")
            checkbutton.grid(row=0, column=col, sticky="w", padx=(0, 10))
            self.section_checkbuttons[section] = checkbutton
        self.sync_name_fields_check = ttk.Checkbutton(
            self.filters,
            variable=self.sync_name_fields_var,
        )
        self.sync_name_fields_check.grid(row=1, column=0, columnspan=4, sticky="w", pady=(6, 0))
        self.translate_textures_check = ttk.Checkbutton(
            self.filters,
            variable=self.translate_textures_var,
            command=self.on_translate_textures_toggle,
        )
        self.translate_textures_check.grid(row=2, column=0, columnspan=4, sticky="w", pady=(6, 0))
        self.delete_original_textures_check = ttk.Checkbutton(
            self.filters,
            variable=self.delete_original_textures_var,
            command=self.on_delete_original_textures_toggle,
        )
        self.delete_original_textures_check.grid(row=3, column=0, columnspan=4, sticky="w", pady=(6, 0))

        panes = ttk.PanedWindow(root, orient=tk.VERTICAL)
        panes.grid(row=2, column=0, sticky="nsew", padx=8, pady=(0, 8))

        table_frame = ttk.Frame(panes)
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        panes.add(table_frame, weight=4)

        columns = ("section", "field", "original", "new")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        self.tree.column("section", width=180, minwidth=120)
        self.tree.column("field", width=130, minwidth=100)
        self.tree.column("original", width=360, minwidth=180)
        self.tree.column("new", width=360, minwidth=180)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.tag_configure("needs_review", background="#fff2cc")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        editor = ttk.Frame(panes, padding=8)
        editor.columnconfigure(1, weight=1)
        panes.add(editor, weight=1)

        self.original_label = ttk.Label(editor)
        self.original_label.grid(row=0, column=0, sticky="w", padx=(0, 8))
        ttk.Entry(editor, textvariable=self.original_var, state="readonly").grid(row=0, column=1, sticky="ew")
        self.new_label = ttk.Label(editor)
        self.new_label.grid(row=1, column=0, sticky="w", padx=(0, 8), pady=(8, 0))
        new_entry = ttk.Entry(editor, textvariable=self.new_value_var)
        new_entry.grid(row=1, column=1, sticky="ew", pady=(8, 0))
        self.apply_button = ttk.Button(editor, command=self.apply_selected)
        self.apply_button.grid(row=1, column=2, sticky="e", padx=(8, 0), pady=(8, 0))

        status = ttk.Label(root, textvariable=self.status_var, anchor="w", padding=(8, 0, 8, 8))
        status.grid(row=3, column=0, sticky="ew")

    def run(self) -> None:
        self.root.mainloop()

    def ui_language(self) -> str:
        return UI_LANGUAGE_CODES.get(self.ui_language_var.get(), "en")

    def tr(self, key: str, **kwargs: object) -> str:
        text = UI_TEXT.get(self.ui_language(), UI_TEXT["en"]).get(key, UI_TEXT["en"].get(key, key))
        return text.format(**kwargs) if kwargs else text

    def section_label(self, section: str) -> str:
        return self.tr(f"section_{section}")

    def entry_label(self, entry: TextEntry) -> str:
        if entry.section == "texture":
            label = SECTION_LABELS["texture"]
        elif entry.section in TRANSLATABLE_SECTIONS:
            label = self.section_label(entry.section)
        else:
            label = SECTION_LABELS.get(entry.section, entry.section)
        if entry.index >= 0:
            return f"{label} #{entry.index}"
        return label

    def on_ui_language_changed(self, _event: object | None = None) -> None:
        self.apply_ui_language()
        self.refresh_table()

    def apply_ui_language(self) -> None:
        self.root.title(self.tr("title"))
        self.open_button.configure(text=self.tr("open_pmx"))
        self.ui_label.configure(text=self.tr("ui"))
        self.target_label.configure(text=self.tr("target"))
        self.overwrite_local_check.configure(text=self.tr("overwrite_local"))
        self.only_empty_check.configure(text=self.tr("only_empty"))
        self.online_fallback_check.configure(text=self.tr("online_fallback"))
        self.auto_button.configure(text=self.tr("auto_translate"))
        self.clear_button.configure(text=self.tr("clear_changes"))
        self.save_button.configure(text=self.tr("save_as"))
        self.filters.configure(text=self.tr("translate_sections"))
        for section, checkbutton in self.section_checkbuttons.items():
            checkbutton.configure(text=self.section_label(section))
        self.sync_name_fields_check.configure(text=self.tr("sync_name_fields"))
        self.translate_textures_check.configure(text=self.tr("translate_textures"))
        self.delete_original_textures_check.configure(text=self.tr("delete_original_textures"))
        self.tree.heading("section", text=self.tr("column_object"))
        self.tree.heading("field", text=self.tr("column_field"))
        self.tree.heading("original", text=self.tr("column_original"))
        self.tree.heading("new", text=self.tr("column_new"))
        self.original_label.configure(text=self.tr("original"))
        self.new_label.configure(text=self.tr("new"))
        self.apply_button.configure(text=self.tr("apply_selected"))
        if not self.entries:
            self.status_var.set(self.tr("ready"))
        self.autoscale_window_to_content()

    def autoscale_window_to_content(self) -> None:
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        max_width = max(900, screen_width - 80)
        max_height = max(600, screen_height - 120)
        requested_width = self.root.winfo_reqwidth() + 36
        requested_height = self.root.winfo_reqheight() + 36
        target_width = min(max(1080, requested_width), max_width)
        target_height = min(max(680, requested_height), max_height)
        self.root.minsize(min(target_width, max_width), min(target_height, max_height))
        current_width = self.root.winfo_width()
        current_height = self.root.winfo_height()
        if current_width < target_width or current_height < target_height:
            self.root.geometry(f"{max(current_width, target_width)}x{max(current_height, target_height)}")

    def open_file(self) -> None:
        from tkinter import filedialog, messagebox

        filename = filedialog.askopenfilename(
            filetypes=[(self.tr("pmx_files"), "*.pmx"), (self.tr("all_files"), "*.*")]
        )
        if not filename:
            return
        try:
            path = Path(filename)
            data = path.read_bytes()
            entries = parse_pmx(data)
        except Exception as exc:  # noqa: BLE001 - GUI must report parse failures.
            messagebox.showerror(self.tr("open_error"), str(exc))
            return
        self.path = path
        self.data = data
        self.entries = entries
        self.replacements.clear()
        self.selected_id = None
        self.refresh_table()
        self.status_var.set(self.tr("loaded", name=path.name, count=len(entries)))

    def refresh_table(self) -> None:
        self.tree.delete(*self.tree.get_children())
        for entry in self.entries:
            if entry.section == "model":
                continue
            if entry.field == "memo":
                continue
            if entry.field == "path" and not (
                entry.section == "texture" and (self.translate_textures_var.get() or entry.id in self.replacements)
            ):
                continue
            new_value = self.replacements.get(entry.id, "")
            tags = ("needs_review",) if has_cjk(new_value or entry.value) else ()
            self.tree.insert(
                "",
                "end",
                iid=str(entry.id),
                values=(self.entry_label(entry), entry.field, entry.value, new_value),
                tags=tags,
            )

    def on_select(self, _event: object) -> None:
        selected = self.tree.selection()
        if not selected:
            return
        self.selected_id = int(selected[0])
        entry = self.entries[self.selected_id]
        self.original_var.set(entry.value)
        self.new_value_var.set(self.replacements.get(entry.id, entry.value))

    def apply_selected(self) -> None:
        if self.selected_id is None:
            return
        value = self.new_value_var.get()
        entry = self.entries[self.selected_id]
        if is_motion_local_name(entry):
            self.replacements.pop(entry.id, None)
            self.refresh_table()
            self.tree.selection_set(str(entry.id))
            self.status_var.set(self.tr("pending", count=len(self.replacements)))
            return
        if value == entry.value:
            self.replacements.pop(entry.id, None)
        else:
            self.replacements[entry.id] = value
        self.refresh_table()
        self.tree.selection_set(str(entry.id))
        self.status_var.set(self.tr("pending", count=len(self.replacements)))

    def selected_translate_sections(self) -> set[str]:
        return {
            section
            for section, var in self.section_vars.items()
            if var.get() and section not in DISABLED_TRANSLATION_SECTIONS
        }

    def on_translate_textures_toggle(self) -> None:
        if not self.translate_textures_var.get():
            self.delete_original_textures_var.set(False)
        self.refresh_table()

    def on_delete_original_textures_toggle(self) -> None:
        if self.delete_original_textures_var.get():
            self.translate_textures_var.set(True)
        self.refresh_table()

    def auto_translate(self) -> None:
        if not self.entries or self.is_translating:
            return
        translate_sections = self.selected_translate_sections()
        translate_textures = self.translate_textures_var.get()
        if not translate_sections and not translate_textures:
            self.status_var.set(self.tr("select_section"))
            return
        self.is_translating = True
        self.auto_button.configure(state="disabled")
        self.open_button.configure(state="disabled")
        self.clear_button.configure(state="disabled")
        self.save_button.configure(state="disabled")
        self.status_var.set(self.tr("translating"))

        entries_snapshot = list(self.entries)
        language = self.language_var.get()
        overwrite_local = self.overwrite_local_var.get()
        sync_name_fields = self.sync_name_fields_var.get()
        only_empty = self.only_empty_var.get()
        online_fallback = self.online_fallback_var.get()

        thread = threading.Thread(
            target=self._auto_translate_worker,
            args=(
                entries_snapshot,
                language,
                overwrite_local,
                sync_name_fields,
                translate_textures,
                only_empty,
                online_fallback,
                translate_sections,
            ),
            daemon=True,
        )
        thread.start()

    def _auto_translate_worker(
        self,
        entries: list[TextEntry],
        language: str,
        overwrite_local: bool,
        sync_name_fields: bool,
        translate_textures: bool,
        only_empty: bool,
        online_fallback: bool,
        translate_sections: set[str],
    ) -> None:
        try:
            cache = load_translation_cache(DEFAULT_CACHE_PATH) if online_fallback else None

            def report_progress(done: int, total: int) -> None:
                if total == 0 or done == total or done % 10 == 0:
                    self.root.after(0, self.status_var.set, self.tr("translating_progress", done=done, total=total))

            replacements = build_auto_replacements(
                entries,
                language,
                overwrite_local=overwrite_local,
                only_empty=only_empty,
                online_fallback=online_fallback,
                cache=cache,
                translate_sections=translate_sections,
                sync_name_fields=sync_name_fields,
                translate_textures=translate_textures,
                progress_callback=report_progress,
            )
            if cache is not None:
                save_translation_cache(cache, DEFAULT_CACHE_PATH)
        except Exception as exc:  # noqa: BLE001 - background task reports to UI.
            self.root.after(0, self._finish_auto_translate, None, exc)
            return
        self.root.after(0, self._finish_auto_translate, replacements, None)

    def _finish_auto_translate(self, replacements: dict[int, str] | None, error: Exception | None) -> None:
        self.is_translating = False
        self.auto_button.configure(state="normal")
        self.open_button.configure(state="normal")
        self.clear_button.configure(state="normal")
        self.save_button.configure(state="normal")
        if error is not None:
            self.status_var.set(self.tr("translate_failed", error=error))
            return
        if replacements:
            self.replacements.update(replacements)
        self.refresh_table()
        needs_review = count_untranslated_cjk(self.replacements)
        if needs_review:
            self.status_var.set(self.tr("pending_review", count=len(self.replacements), review=needs_review))
        else:
            self.status_var.set(self.tr("pending", count=len(self.replacements)))

    def clear_changes(self) -> None:
        self.replacements.clear()
        self.refresh_table()
        self.status_var.set(self.tr("cleared"))

    def save_as(self) -> None:
        from tkinter import filedialog, messagebox

        if self.data is None or self.path is None:
            return
        default = self.path.with_name(self.path.stem + f".{self.language_var.get()}.pmx")
        filename = filedialog.asksaveasfilename(
            defaultextension=".pmx",
            initialfile=default.name,
            filetypes=[(self.tr("pmx_files"), "*.pmx"), (self.tr("all_files"), "*.*")],
        )
        if not filename:
            return
        output_path = Path(filename)
        delete_originals = self.delete_original_textures_var.get() and has_texture_replacements(
            self.entries, self.replacements
        )
        if delete_originals:
            confirmed = messagebox.askyesno(
                self.tr("delete_title"),
                self.tr("delete_confirm"),
            )
            if not confirmed:
                delete_originals = False
        try:
            output_path.write_bytes(write_replacements(self.data, self.entries, self.replacements))
            copied = 0
            deleted = 0
            warnings: list[str] = []
            if has_texture_replacements(self.entries, self.replacements):
                copied, deleted, warnings = copy_replaced_textures(
                    self.path,
                    output_path,
                    self.entries,
                    self.replacements,
                    delete_originals=delete_originals,
                )
        except Exception as exc:  # noqa: BLE001 - GUI must report write failures.
            messagebox.showerror(self.tr("save_error"), str(exc))
            return
        status = self.tr("saved", name=os.path.basename(filename), count=len(self.replacements))
        if has_texture_replacements(self.entries, self.replacements):
            status += self.tr("copied", count=copied)
            if delete_originals:
                status += self.tr("deleted", count=deleted)
            if warnings:
                messagebox.showwarning(self.tr("texture_copy"), "\n".join(warnings[:12]))
        self.status_var.set(status)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Translate PMX object names to English or Vietnamese without accents.")
    parser.add_argument("input", nargs="?", help="Input .pmx file. Omit to open the GUI.")
    parser.add_argument("-o", "--output", help="Output .pmx path.")
    parser.add_argument(
        "-l",
        "--language",
        choices=(LANG_EN, LANG_VI),
        default=LANG_EN,
        help="Translation target: en or vi.",
    )
    parser.add_argument("--overwrite-local", action="store_true", help="Also rewrite Japanese/local name fields.")
    parser.add_argument(
        "--sync-name-fields",
        action="store_true",
        help="Translate from local_name and write the same result to both local_name and universal_name.",
    )
    parser.add_argument(
        "--translate-textures",
        action="store_true",
        help="Translate texture filenames, update PMX texture paths, and copy texture files to the new paths.",
    )
    parser.add_argument(
        "--delete-original-textures",
        action="store_true",
        help="After translated textures are copied, delete old texture files that are no longer referenced.",
    )
    parser.add_argument("--only-empty", action="store_true", help="Only fill empty fields.")
    parser.add_argument(
        "--sections",
        default="all",
        help=(
            "Comma-separated sections to translate: all, material/objects, bone, morph. "
            "Display, rigid_body, joint, and soft_body are temporarily disabled."
        ),
    )
    parser.add_argument(
        "--online",
        action="store_true",
        help="Use online machine translation only for names that remain untranslated after the local dictionary.",
    )
    parser.add_argument(
        "--source-language",
        default="auto",
        help="Source language for online fallback, for example auto, ja, zh-CN or zh-TW.",
    )
    parser.add_argument("--cache", help=f"Translation cache JSON path. Default: {DEFAULT_CACHE_PATH}")
    parser.add_argument("--dry-run", action="store_true", help="Print planned changes without writing a file.")
    parser.add_argument("--gui", action="store_true", help="Open the GUI.")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    if args.gui or not args.input:
        PmxTranslatorApp().run()
        return 0
    try:
        return run_cli(args)
    except Exception as exc:  # noqa: BLE001 - CLI should present concise user-facing errors.
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
