#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import subprocess
import platform
from typing import Dict, List, Any, Optional
import logging

# 尝试导入Dify相关模块，如果不可用则使用兼容模式
try:
    from core.tools.tool.builtin_tool import BuiltinTool
    from core.tools.entities.tool_entities import ToolInvokeMessage
    DIFYY_ENV = True
except ImportError:
    # 本地测试环境，没有Dify模块
    DIFYY_ENV = False

    # 定义兼容的基类和消息类
    class BuiltinTool:
        def create_text_message(self, text: str):
            return {"type": "text", "message": text}

    class ToolInvokeMessage:
        pass

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MobileControlTool(BuiltinTool):
    """移动设备控制工具类"""

    def __init__(self):
        self.phonebook_file = "phonebook.json"
        self.system = platform.system().lower()
        self._ensure_phonebook_file()

    def _ensure_phonebook_file(self):
        """确保电话本文件存在"""
        if not os.path.exists(self.phonebook_file):
            with open(self.phonebook_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)

    def _load_phonebook(self) -> Dict[str, Dict[str, str]]:
        """加载电话本数据"""
        try:
            with open(self.phonebook_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 兼容旧格式，如果是旧格式则转换
                if data and isinstance(next(iter(data.values())), str):
                    # 旧格式: {"name": "phone"}
                    # 新格式: {"name": {"phone": "phone", "alias": ""}}
                    converted_data = {}
                    for name, phone in data.items():
                        converted_data[name] = {"phone": phone, "alias": ""}
                    return converted_data
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_phonebook(self, phonebook: Dict[str, Dict[str, str]]):
        """保存电话本数据"""
        with open(self.phonebook_file, 'w', encoding='utf-8') as f:
            json.dump(phonebook, f, ensure_ascii=False, indent=2)

    def phonebook_list(self) -> Dict[str, Any]:
        """查看电话本"""
        try:
            phonebook = self._load_phonebook()
            if not phonebook:
                return {
                    "success": True,
                    "message": "电话本为空",
                    "data": []
                }

            contacts = []
            for name, info in phonebook.items():
                contact = {
                    "name": name,
                    "phone": info.get("phone", ""),
                    "alias": info.get("alias", "")
                }
                contacts.append(contact)

            return {
                "success": True,
                "message": f"找到 {len(contacts)} 个联系人",
                "data": contacts
            }
        except Exception as e:
            logger.error(f"查看电话本失败: {e}")
            return {
                "success": False,
                "message": f"查看电话本失败: {str(e)}",
                "data": []
            }

    def phonebook_add(self, name: str, phone: str, alias: str = "") -> Dict[str, Any]:
        """添加联系人"""
        try:
            if not name or not phone:
                return {
                    "success": False,
                    "message": "姓名和电话号码不能为空"
                }

            phonebook = self._load_phonebook()

            if name in phonebook:
                return {
                    "success": False,
                    "message": f"联系人 '{name}' 已存在"
                }

            phonebook[name] = {
                "phone": phone,
                "alias": alias or ""
            }
            self._save_phonebook(phonebook)

            alias_info = f" (别名: {alias})" if alias else ""
            return {
                "success": True,
                "message": f"成功添加联系人 '{name}'{alias_info}: {phone}"
            }
        except Exception as e:
            logger.error(f"添加联系人失败: {e}")
            return {
                "success": False,
                "message": f"添加联系人失败: {str(e)}"
            }

    def phonebook_delete(self, name: str) -> Dict[str, Any]:
        """删除联系人"""
        try:
            if not name:
                return {
                    "success": False,
                    "message": "联系人姓名不能为空"
                }

            phonebook = self._load_phonebook()

            if name not in phonebook:
                return {
                    "success": False,
                    "message": f"联系人 '{name}' 不存在"
                }

            deleted_contact = phonebook.pop(name)
            self._save_phonebook(phonebook)

            alias_info = f" (别名: {deleted_contact.get('alias', '')})" if deleted_contact.get('alias') else ""
            return {
                "success": True,
                "message": f"成功删除联系人 '{name}'{alias_info}: {deleted_contact.get('phone', '')}"
            }
        except Exception as e:
            logger.error(f"删除联系人失败: {e}")
            return {
                "success": False,
                "message": f"删除联系人失败: {str(e)}"
            }

    def make_call(self, phone_number: str) -> Dict[str, Any]:
        """拨打电话"""
        try:
            if not phone_number:
                return {
                    "success": False,
                    "message": "电话号码不能为空"
                }

            # 根据不同操作系统执行相应的拨号命令
            if self.system == "darwin":  # macOS
                # 在macOS上打开FaceTime或其他电话应用
                subprocess.run(["open", f"tel:{phone_number}"], check=True)
                message = f"正在拨打: {phone_number}"
            elif self.system == "windows":
                # Windows上可能需要特定的电话应用
                subprocess.run(["start", f"tel:{phone_number}"], shell=True, check=True)
                message = f"正在拨打: {phone_number}"
            elif self.system == "linux":
                # Linux上可能需要特定的电话应用
                # 这里使用xdg-open尝试打开tel:链接
                subprocess.run(["xdg-open", f"tel:{phone_number}"], check=True)
                message = f"正在拨打: {phone_number}"
            else:
                return {
                    "success": False,
                    "message": f"不支持的操作系统: {self.system}"
                }

            return {
                "success": True,
                "message": message
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"拨打电话失败: {e}")
            return {
                "success": False,
                "message": f"拨打电话失败: {str(e)}"
            }
        except Exception as e:
            logger.error(f"拨打电话异常: {e}")
            return {
                "success": False,
                "message": f"拨打电话异常: {str(e)}"
            }

    def send_sms(self, phone_number: str, message: str) -> Dict[str, Any]:
        """发送短信"""
        try:
            if not phone_number:
                return {
                    "success": False,
                    "message": "电话号码不能为空"
                }

            if not message:
                return {
                    "success": False,
                    "message": "短信内容不能为空"
                }

            # 根据不同操作系统执行相应的发短信命令
            if self.system == "darwin":  # macOS
                # 在macOS上打开Messages应用
                subprocess.run(["open", f"sms:{phone_number}&body={message}"], check=True)
                result_message = f"正在发送短信到 {phone_number}: {message[:50]}{'...' if len(message) > 50 else ''}"
            elif self.system == "windows":
                # Windows上可能需要特定的短信应用
                subprocess.run(["start", f"sms:{phone_number}?body={message}"], shell=True, check=True)
                result_message = f"正在发送短信到 {phone_number}: {message[:50]}{'...' if len(message) > 50 else ''}"
            elif self.system == "linux":
                # Linux上可能需要特定的短信应用
                subprocess.run(["xdg-open", f"sms:{phone_number}?body={message}"], check=True)
                result_message = f"正在发送短信到 {phone_number}: {message[:50]}{'...' if len(message) > 50 else ''}"
            else:
                return {
                    "success": False,
                    "message": f"不支持的操作系统: {self.system}"
                }

            return {
                "success": True,
                "message": result_message
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"发送短信失败: {e}")
            return {
                "success": False,
                "message": f"发送短信失败: {str(e)}"
            }
        except Exception as e:
            logger.error(f"发送短信异常: {e}")
            return {
                "success": False,
                "message": f"发送短信异常: {str(e)}"
            }

    def control_volume(self, level: int) -> Dict[str, Any]:
        """控制音量"""
        try:
            if not isinstance(level, int) or not (0 <= level <= 100):
                return {
                    "success": False,
                    "message": "音量等级必须是0-100之间的整数"
                }

            if self.system == "darwin":  # macOS
                # 使用osascript控制音量
                volume_percent = int((level / 100) * 7)  # macOS音量范围是0-7
                subprocess.run([
                    "osascript", "-e",
                    f"set volume output volume {volume_percent}"
                ], check=True)
                message = f"音量已设置为 {level}%"
            elif self.system == "windows":
                # Windows上使用nircmd或其他工具
                try:
                    subprocess.run([
                        "nircmd.exe", "setsysvolume",
                        str(int((level / 100) * 65535))
                    ], check=True)
                    message = f"音量已设置为 {level}%"
                except FileNotFoundError:
                    return {
                        "success": False,
                        "message": "需要安装nircmd工具来控制Windows音量"
                    }
            elif self.system == "linux":
                # Linux上使用amixer或其他工具
                try:
                    subprocess.run([
                        "amixer", "sset", "Master", f"{level}%"
                    ], check=True)
                    message = f"音量已设置为 {level}%"
                except FileNotFoundError:
                    return {
                        "success": False,
                        "message": "需要安装alsa-utils来控制Linux音量"
                    }
            else:
                return {
                    "success": False,
                    "message": f"不支持的操作系统: {self.system}"
                }

            return {
                "success": True,
                "message": message
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"控制音量失败: {e}")
            return {
                "success": False,
                "message": f"控制音量失败: {str(e)}"
            }
        except Exception as e:
            logger.error(f"控制音量异常: {e}")
            return {
                "success": False,
                "message": f"控制音量异常: {str(e)}"
            }

    def control_brightness(self, level: int) -> Dict[str, Any]:
        """控制屏幕亮度"""
        try:
            if not isinstance(level, int) or not (0 <= level <= 100):
                return {
                    "success": False,
                    "message": "亮度等级必须是0-100之间的整数"
                }

            if self.system == "darwin":  # macOS
                # macOS上控制亮度比较复杂，可能需要安装brightness工具
                try:
                    subprocess.run([
                        "brightness", str(level / 100)
                    ], check=True)
                    message = f"亮度已设置为 {level}%"
                except FileNotFoundError:
                    return {
                        "success": False,
                        "message": "需要安装brightness工具来控制macOS亮度"
                    }
            elif self.system == "windows":
                # Windows上使用powercfg或其他工具
                try:
                    # 这是一个简化的实现，实际可能需要更复杂的命令
                    subprocess.run([
                        "powershell", "-Command",
                        f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, {level})"
                    ], check=True)
                    message = f"亮度已设置为 {level}%"
                except Exception:
                    return {
                        "success": False,
                        "message": "Windows亮度控制需要管理员权限或特定工具"
                    }
            elif self.system == "linux":
                # Linux上使用brightnessctl或其他工具
                try:
                    subprocess.run([
                        "brightnessctl", "set", f"{level}%"
                    ], check=True)
                    message = f"亮度已设置为 {level}%"
                except FileNotFoundError:
                    return {
                        "success": False,
                        "message": "需要安装brightnessctl来控制Linux亮度"
                    }
            else:
                return {
                    "success": False,
                    "message": f"不支持的操作系统: {self.system}"
                }

            return {
                "success": True,
                "message": message
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"控制亮度失败: {e}")
            return {
                "success": False,
                "message": f"控制亮度失败: {str(e)}"
            }
        except Exception as e:
            logger.error(f"控制亮度异常: {e}")
            return {
                "success": False,
                "message": f"控制亮度异常: {str(e)}"
            }

    def control_theme(self, mode: str) -> Dict[str, Any]:
        """控制系统主题"""
        try:
            valid_modes = ["light", "dark", "auto"]
            if mode not in valid_modes:
                return {
                    "success": False,
                    "message": f"无效的主题模式，可选值: {', '.join(valid_modes)}"
                }

            if self.system == "darwin":  # macOS
                if mode == "dark":
                    subprocess.run([
                        "osascript", "-e",
                        'tell application "System Events" to tell appearance preferences to set dark mode to true'
                    ], check=True)
                elif mode == "light":
                    subprocess.run([
                        "osascript", "-e",
                        'tell application "System Events" to tell appearance preferences to set dark mode to false'
                    ], check=True)
                elif mode == "auto":
                    # macOS auto mode需要更复杂的设置
                    return {
                        "success": False,
                        "message": "macOS自动主题模式暂不支持"
                    }
                message = f"主题已设置为: {mode}"
            elif self.system == "windows":
                # Windows主题控制
                if mode == "dark":
                    subprocess.run([
                        "reg", "add", "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize",
                        "/v", "AppsUseLightTheme", "/t", "REG_DWORD", "/d", "0", "/f"
                    ], check=True)
                    subprocess.run([
                        "reg", "add", "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize",
                        "/v", "SystemUsesLightTheme", "/t", "REG_DWORD", "/d", "0", "/f"
                    ], check=True)
                elif mode == "light":
                    subprocess.run([
                        "reg", "add", "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize",
                        "/v", "AppsUseLightTheme", "/t", "REG_DWORD", "/d", "1", "/f"
                    ], check=True)
                    subprocess.run([
                        "reg", "add", "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize",
                        "/v", "SystemUsesLightTheme", "/t", "REG_DWORD", "/d", "1", "/f"
                    ], check=True)
                elif mode == "auto":
                    return {
                        "success": False,
                        "message": "Windows自动主题模式暂不支持"
                    }
                message = f"主题已设置为: {mode}"
            elif self.system == "linux":
                # Linux主题控制因桌面环境而异，这里提供一个通用的方案
                # 大多数Linux发行版使用gsettings
                try:
                    if mode == "dark":
                        subprocess.run([
                            "gsettings", "set", "org.gnome.desktop.interface", "gtk-theme", "Adwaita-dark"
                        ], check=True)
                    elif mode == "light":
                        subprocess.run([
                            "gsettings", "set", "org.gnome.desktop.interface", "gtk-theme", "Adwaita"
                        ], check=True)
                    elif mode == "auto":
                        return {
                            "success": False,
                            "message": "Linux自动主题模式暂不支持"
                        }
                    message = f"主题已设置为: {mode}"
                except FileNotFoundError:
                    return {
                        "success": False,
                        "message": "需要GNOME桌面环境或安装gsettings来控制主题"
                    }
            else:
                return {
                    "success": False,
                    "message": f"不支持的操作系统: {self.system}"
                }

            return {
                "success": True,
                "message": message
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"控制主题失败: {e}")
            return {
                "success": False,
                "message": f"控制主题失败: {str(e)}"
            }
        except Exception as e:
            logger.error(f"控制主题异常: {e}")
            return {
                "success": False,
                "message": f"控制主题异常: {str(e)}"
            }

    def _invoke(self, user_id: str, tool_parameters: Dict[str, Any]) -> list:
        """
        Dify工具调用入口方法
        """
        try:
            action = tool_parameters.get('action', '')

            if action == "phonebook_list":
                result = self.phonebook_list()
            elif action == "phonebook_add":
                name = tool_parameters.get('contact_name')
                phone = tool_parameters.get('phone_number')
                alias = tool_parameters.get('contact_alias', '')
                result = self.phonebook_add(name, phone, alias)
            elif action == "phonebook_delete":
                name = tool_parameters.get('contact_name')
                result = self.phonebook_delete(name)
            elif action == "call":
                phone = tool_parameters.get('phone_number')
                result = self.make_call(phone)
            elif action == "sms":
                phone = tool_parameters.get('phone_number')
                message = tool_parameters.get('sms_message')
                result = self.send_sms(phone, message)
            elif action == "volume":
                level = tool_parameters.get('volume_level')
                if level is not None:
                    level = int(level)
                result = self.control_volume(level)
            elif action == "brightness":
                level = tool_parameters.get('brightness_level')
                if level is not None:
                    level = int(level)
                result = self.control_brightness(level)
            elif action == "theme":
                mode = tool_parameters.get('theme_mode')
                result = self.control_theme(mode)
            else:
                result = {
                    "success": False,
                    "message": f"未知操作: {action}"
                }

            # 返回ToolInvokeMessage格式的结果
            return [self.create_text_message(json.dumps(result, ensure_ascii=False))]

        except Exception as e:
            logger.error(f"工具调用异常: {e}")
            return [self.create_text_message(json.dumps({
                "success": False,
                "message": f"工具调用失败: {str(e)}"
            }, ensure_ascii=False))]


# Dify工具不需要main函数，Dify会直接调用MobileControlTool类
