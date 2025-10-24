#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mobile device control tool implementation for Dify."""

from __future__ import annotations

import json
import logging
import os
import platform
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Dify compatibility layer
# ---------------------------------------------------------------------------
try:  # pragma: no cover - only executed in real Dify runtime
    from core.tools.tool.builtin_tool import BuiltinTool
    from core.tools.entities.tool_entities import ToolInvokeMessage
except ImportError:  # Local development fallback

    class BuiltinTool:  # type: ignore[too-few-public-methods]
        """Fallback base class matching Dify's BuiltinTool interface."""

    class ToolInvokeMessage(dict):  # pragma: no cover - simple stub
        """Simplified fallback implementation for local development."""

        @staticmethod
        def Text(content: str) -> "ToolInvokeMessage":
            return ToolInvokeMessage({"type": "text", "content": content})


# ---------------------------------------------------------------------------
# Data models and helpers
# ---------------------------------------------------------------------------
@dataclass
class Contact:
    """Represents a phonebook contact."""

    name: str
    phone: str
    alias: str = ""

    def to_dict(self) -> Dict[str, str]:
        return {"name": self.name, "phone": self.phone, "alias": self.alias}


class PhonebookRepository:
    """Persistence layer for phonebook data stored in JSON format."""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self._ensure_file()

    def _ensure_file(self) -> None:
        if not self.file_path.exists():
            logger.debug("Creating phonebook file at %s", self.file_path)
            self._write({})

    def _read(self) -> Dict[str, Dict[str, str]]:
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
        except (FileNotFoundError, json.JSONDecodeError):
            logger.warning("Phonebook file missing or corrupt, resetting to empty")
            return {}

        # Backward compatibility with legacy format {"name": "phone"}
        if data and isinstance(next(iter(data.values())), str):
            logger.debug("Detected legacy phonebook format, converting")
            data = {name: {"phone": phone, "alias": ""} for name, phone in data.items()}
        return data

    def _write(self, data: Dict[str, Dict[str, str]]) -> None:
        with self.file_path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)

    def list_contacts(self) -> List[Contact]:
        phonebook = self._read()
        return [Contact(name, info.get("phone", ""), info.get("alias", "")) for name, info in phonebook.items()]

    def add_contact(self, contact: Contact) -> bool:
        phonebook = self._read()
        if contact.name in phonebook:
            return False
        phonebook[contact.name] = {"phone": contact.phone, "alias": contact.alias}
        self._write(phonebook)
        return True

    def delete_contact(self, name: str) -> Optional[Contact]:
        phonebook = self._read()
        info = phonebook.pop(name, None)
        if info is None:
            return None
        self._write(phonebook)
        return Contact(name, info.get("phone", ""), info.get("alias", ""))


class SystemController:
    """Encapsulates system level operations for different platforms."""

    def __init__(self, system_name: Optional[str] = None):
        self.system = (system_name or platform.system()).lower()

    # Phone & SMS ------------------------------------------------------------
    def dial(self, phone_number: str) -> str:
        self._require_value(phone_number, "电话号码不能为空")

        if self.system == "darwin":
            subprocess.run(["open", f"tel:{phone_number}"], check=True)
        elif self.system == "windows":
            subprocess.run(["start", f"tel:{phone_number}"], shell=True, check=True)
        elif self.system == "linux":
            subprocess.run(["xdg-open", f"tel:{phone_number}"], check=True)
        else:
            raise ValueError(f"不支持的操作系统: {self.system}")

        return f"正在拨打: {phone_number}"

    def send_sms(self, phone_number: str, message: str) -> str:
        self._require_value(phone_number, "电话号码不能为空")
        self._require_value(message, "短信内容不能为空")

        if self.system == "darwin":
            subprocess.run(["open", f"sms:{phone_number}&body={message}"], check=True)
        elif self.system == "windows":
            subprocess.run(["start", f"sms:{phone_number}?body={message}"], shell=True, check=True)
        elif self.system == "linux":
            subprocess.run(["xdg-open", f"sms:{phone_number}?body={message}"], check=True)
        else:
            raise ValueError(f"不支持的操作系统: {self.system}")

        preview = message[:50]
        if len(message) > 50:
            preview += "..."
        return f"正在发送短信到 {phone_number}: {preview}"

    # Volume ----------------------------------------------------------------
    def set_volume(self, level: int) -> str:
        self._validate_percentage(level, "音量等级必须是0-100之间的整数")

        if self.system == "darwin":
            volume_percent = int((level / 100) * 7)
            subprocess.run(["osascript", "-e", f"set volume output volume {volume_percent}"], check=True)
        elif self.system == "windows":
            try:
                subprocess.run(["nircmd.exe", "setsysvolume", str(int((level / 100) * 65535))], check=True)
            except FileNotFoundError as exc:
                raise FileNotFoundError("需要安装nircmd工具来控制Windows音量") from exc
        elif self.system == "linux":
            try:
                subprocess.run(["amixer", "sset", "Master", f"{level}%"], check=True)
            except FileNotFoundError as exc:
                raise FileNotFoundError("需要安装alsa-utils来控制Linux音量") from exc
        else:
            raise ValueError(f"不支持的操作系统: {self.system}")

        return f"音量已设置为 {level}%"

    # Brightness ------------------------------------------------------------
    def set_brightness(self, level: int) -> str:
        self._validate_percentage(level, "亮度等级必须是0-100之间的整数")

        if self.system == "darwin":
            try:
                subprocess.run(["brightness", str(level / 100)], check=True)
            except FileNotFoundError as exc:
                raise FileNotFoundError("需要安装brightness工具来控制macOS亮度") from exc
        elif self.system == "windows":
            try:
                subprocess.run(
                    [
                        "powershell",
                        "-Command",
                        f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, {level})",
                    ],
                    check=True,
                )
            except subprocess.CalledProcessError as exc:
                raise PermissionError("Windows亮度控制需要管理员权限或特定工具") from exc
        elif self.system == "linux":
            try:
                subprocess.run(["brightnessctl", "set", f"{level}%"], check=True)
            except FileNotFoundError as exc:
                raise FileNotFoundError("需要安装brightnessctl来控制Linux亮度") from exc
        else:
            raise ValueError(f"不支持的操作系统: {self.system}")

        return f"亮度已设置为 {level}%"

    # Theme -----------------------------------------------------------------
    def set_theme(self, mode: str) -> str:
        valid_modes = ["light", "dark", "auto"]
        if mode not in valid_modes:
            raise ValueError(f"无效的主题模式，可选值: {', '.join(valid_modes)}")

        if self.system == "darwin":
            if mode == "dark":
                subprocess.run(
                    [
                        "osascript",
                        "-e",
                        'tell application "System Events" to tell appearance preferences to set dark mode to true',
                    ],
                    check=True,
                )
            elif mode == "light":
                subprocess.run(
                    [
                        "osascript",
                        "-e",
                        'tell application "System Events" to tell appearance preferences to set dark mode to false',
                    ],
                    check=True,
                )
            else:
                raise NotImplementedError("macOS自动主题模式暂不支持")
        elif self.system == "windows":
            if mode == "dark":
                subprocess.run(
                    [
                        "reg",
                        "add",
                        "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize",
                        "/v",
                        "AppsUseLightTheme",
                        "/t",
                        "REG_DWORD",
                        "/d",
                        "0",
                        "/f",
                    ],
                    check=True,
                )
                subprocess.run(
                    [
                        "reg",
                        "add",
                        "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize",
                        "/v",
                        "SystemUsesLightTheme",
                        "/t",
                        "REG_DWORD",
                        "/d",
                        "0",
                        "/f",
                    ],
                    check=True,
                )
            elif mode == "light":
                subprocess.run(
                    [
                        "reg",
                        "add",
                        "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize",
                        "/v",
                        "AppsUseLightTheme",
                        "/t",
                        "REG_DWORD",
                        "/d",
                        "1",
                        "/f",
                    ],
                    check=True,
                )
                subprocess.run(
                    [
                        "reg",
                        "add",
                        "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize",
                        "/v",
                        "SystemUsesLightTheme",
                        "/t",
                        "REG_DWORD",
                        "/d",
                        "1",
                        "/f",
                    ],
                    check=True,
                )
            else:
                raise NotImplementedError("Windows自动主题模式暂不支持")
        elif self.system == "linux":
            try:
                if mode == "dark":
                    subprocess.run(["gsettings", "set", "org.gnome.desktop.interface", "gtk-theme", "Adwaita-dark"], check=True)
                elif mode == "light":
                    subprocess.run(["gsettings", "set", "org.gnome.desktop.interface", "gtk-theme", "Adwaita"], check=True)
                else:
                    raise NotImplementedError("Linux自动主题模式暂不支持")
            except FileNotFoundError as exc:
                raise FileNotFoundError("需要GNOME桌面环境或安装gsettings来控制主题") from exc
        else:
            raise ValueError(f"不支持的操作系统: {self.system}")

        return f"主题已设置为: {mode}"

    # Validators ------------------------------------------------------------
    @staticmethod
    def _require_value(value: Optional[str], error_message: str) -> None:
        if not value:
            raise ValueError(error_message)

    @staticmethod
    def _validate_percentage(value: Any, error_message: str) -> None:
        if not isinstance(value, int) or not (0 <= value <= 100):
            raise ValueError(error_message)


# ---------------------------------------------------------------------------
# Tool implementation
# ---------------------------------------------------------------------------
class MobileControlTool(BuiltinTool):
    """Mobile device control tool compatible with Dify's tool interface."""

    def __init__(self, phonebook_path: Optional[Path] = None, system_controller: Optional[SystemController] = None):
        self.phonebook = PhonebookRepository(phonebook_path or Path("phonebook.json"))
        self.system_controller = system_controller or SystemController()

    # Phonebook -------------------------------------------------------------
    def phonebook_list(self) -> Dict[str, Any]:
        try:
            contacts = self.phonebook.list_contacts()
            if not contacts:
                return {"success": True, "message": "电话本为空", "data": []}

            contact_dicts = [contact.to_dict() for contact in contacts]
            return {
                "success": True,
                "message": f"找到 {len(contact_dicts)} 个联系人",
                "data": contact_dicts,
            }
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("查看电话本失败: %s", exc)
            return {"success": False, "message": f"查看电话本失败: {exc}", "data": []}

    def phonebook_add(self, name: Optional[str], phone: Optional[str], alias: str = "") -> Dict[str, Any]:
        try:
            if not name or not phone:
                raise ValueError("姓名和电话号码不能为空")

            added = self.phonebook.add_contact(Contact(name=name, phone=phone, alias=alias or ""))
            if not added:
                raise ValueError(f"联系人 '{name}' 已存在")

            alias_info = f" (别名: {alias})" if alias else ""
            return {"success": True, "message": f"成功添加联系人 '{name}'{alias_info}: {phone}"}
        except Exception as exc:
            logger.error("添加联系人失败: %s", exc)
            return {"success": False, "message": f"添加联系人失败: {exc}"}

    def phonebook_delete(self, name: Optional[str]) -> Dict[str, Any]:
        try:
            if not name:
                raise ValueError("联系人姓名不能为空")

            deleted = self.phonebook.delete_contact(name)
            if deleted is None:
                raise ValueError(f"联系人 '{name}' 不存在")

            alias_info = f" (别名: {deleted.alias})" if deleted.alias else ""
            return {"success": True, "message": f"成功删除联系人 '{name}'{alias_info}: {deleted.phone}"}
        except Exception as exc:
            logger.error("删除联系人失败: %s", exc)
            return {"success": False, "message": f"删除联系人失败: {exc}"}

    # System operations -----------------------------------------------------
    def make_call(self, phone_number: Optional[str]) -> Dict[str, Any]:
        try:
            message = self.system_controller.dial(phone_number or "")
            return {"success": True, "message": message}
        except subprocess.CalledProcessError as exc:
            logger.error("拨打电话失败: %s", exc)
            return {"success": False, "message": f"拨打电话失败: {exc}"}
        except Exception as exc:
            logger.error("拨打电话异常: %s", exc)
            return {"success": False, "message": f"拨打电话异常: {exc}"}

    def send_sms(self, phone_number: Optional[str], message: Optional[str]) -> Dict[str, Any]:
        try:
            response_message = self.system_controller.send_sms(phone_number or "", message or "")
            return {"success": True, "message": response_message}
        except subprocess.CalledProcessError as exc:
            logger.error("发送短信失败: %s", exc)
            return {"success": False, "message": f"发送短信失败: {exc}"}
        except Exception as exc:
            logger.error("发送短信异常: %s", exc)
            return {"success": False, "message": f"发送短信异常: {exc}"}

    def control_volume(self, level: Optional[int]) -> Dict[str, Any]:
        try:
            if level is None:
                raise ValueError("音量等级必须是0-100之间的整数")
            message = self.system_controller.set_volume(int(level))
            return {"success": True, "message": message}
        except subprocess.CalledProcessError as exc:
            logger.error("控制音量失败: %s", exc)
            return {"success": False, "message": f"控制音量失败: {exc}"}
        except Exception as exc:
            logger.error("控制音量异常: %s", exc)
            return {"success": False, "message": f"控制音量异常: {exc}"}

    def control_brightness(self, level: Optional[int]) -> Dict[str, Any]:
        try:
            if level is None:
                raise ValueError("亮度等级必须是0-100之间的整数")
            message = self.system_controller.set_brightness(int(level))
            return {"success": True, "message": message}
        except subprocess.CalledProcessError as exc:
            logger.error("控制亮度失败: %s", exc)
            return {"success": False, "message": f"控制亮度失败: {exc}"}
        except Exception as exc:
            logger.error("控制亮度异常: %s", exc)
            return {"success": False, "message": f"控制亮度异常: {exc}"}

    def control_theme(self, mode: Optional[str]) -> Dict[str, Any]:
        try:
            message = self.system_controller.set_theme(mode or "")
            return {"success": True, "message": message}
        except subprocess.CalledProcessError as exc:
            logger.error("控制主题失败: %s", exc)
            return {"success": False, "message": f"控制主题失败: {exc}"}
        except Exception as exc:
            logger.error("控制主题异常: %s", exc)
            return {"success": False, "message": f"控制主题异常: {exc}"}

    # Dify entrypoint -------------------------------------------------------
    def invoke(self, user_id: str, tool_parameters: Dict[str, Any]) -> List[ToolInvokeMessage]:  # pragma: no cover
        return self._invoke(user_id, tool_parameters)

    def _invoke(self, user_id: str, tool_parameters: Dict[str, Any]) -> List[ToolInvokeMessage]:
        try:
            action = tool_parameters.get("action")
            result: Dict[str, Any]

            if action == "phonebook_list":
                result = self.phonebook_list()
            elif action == "phonebook_add":
                result = self.phonebook_add(
                    tool_parameters.get("contact_name"),
                    tool_parameters.get("phone_number"),
                    tool_parameters.get("contact_alias", ""),
                )
            elif action == "phonebook_delete":
                result = self.phonebook_delete(tool_parameters.get("contact_name"))
            elif action == "call":
                result = self.make_call(tool_parameters.get("phone_number"))
            elif action == "sms":
                result = self.send_sms(
                    tool_parameters.get("phone_number"),
                    tool_parameters.get("sms_message"),
                )
            elif action == "volume":
                level = tool_parameters.get("volume_level")
                result = self.control_volume(int(level) if level is not None else None)
            elif action == "brightness":
                level = tool_parameters.get("brightness_level")
                result = self.control_brightness(int(level) if level is not None else None)
            elif action == "theme":
                result = self.control_theme(tool_parameters.get("theme_mode"))
            else:
                result = {"success": False, "message": f"未知操作: {action}"}

            return [ToolInvokeMessage.Text(json.dumps(result, ensure_ascii=False, indent=2))]
        except Exception as exc:
            logger.error("Dify工具调用异常: %s", exc)
            error_payload = {"success": False, "message": f"工具调用失败: {exc}"}
            return [ToolInvokeMessage.Text(json.dumps(error_payload, ensure_ascii=False, indent=2))]


# ---------------------------------------------------------------------------
# Command line interface for local testing
# ---------------------------------------------------------------------------
def parse_cli_arguments(arguments: Iterable[str]) -> Dict[str, Any]:
    parsed: Dict[str, Any] = {}
    for arg in arguments:
        if "=" in arg:
            key, value = arg.split("=", 1)
            parsed[key] = value
        else:
            parsed["action"] = arg
    return parsed


def main() -> None:
    import sys

    if len(sys.argv) < 2:
        print(json.dumps({"error": "缺少参数。请提供action参数。"}, ensure_ascii=False))
        return

    args = parse_cli_arguments(sys.argv[1:])
    action = args.get("action")
    if not action:
        print(json.dumps({"error": "缺少action参数。"}, ensure_ascii=False))
        return

    tool = MobileControlTool()

    try:
        if action == "phonebook_list":
            result = tool.phonebook_list()
        elif action == "phonebook_add":
            result = tool.phonebook_add(
                args.get("contact_name"),
                args.get("phone_number"),
                args.get("contact_alias", ""),
            )
        elif action == "phonebook_delete":
            result = tool.phonebook_delete(args.get("contact_name"))
        elif action == "call":
            result = tool.make_call(args.get("phone_number"))
        elif action == "sms":
            result = tool.send_sms(
                args.get("phone_number"),
                args.get("sms_message"),
            )
        elif action == "volume":
            level = args.get("volume_level")
            result = tool.control_volume(int(level) if level is not None else None)
        elif action == "brightness":
            level = args.get("brightness_level")
            result = tool.control_brightness(int(level) if level is not None else None)
        elif action == "theme":
            result = tool.control_theme(args.get("theme_mode"))
        else:
            result = {"success": False, "message": f"未知操作: {action}"}

        print(json.dumps(result, ensure_ascii=False))
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.error("执行操作失败: %s", exc)
        print(json.dumps({"success": False, "message": f"执行操作失败: {exc}"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
