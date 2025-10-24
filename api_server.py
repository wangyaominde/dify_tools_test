#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Mobile Control Tool API Server
移动设备控制工具API服务器

提供RESTful API接口，允许远程访问移动设备控制功能
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import logging
from typing import Dict, Any
from main import MobileControlTool

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 初始化工具
tool = MobileControlTool()

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        "status": "healthy",
        "service": "Mobile Control Tool API",
        "version": "1.0.0"
    })

@app.route('/api/mobile-control', methods=['POST'])
def mobile_control():
    """移动设备控制主接口"""
    try:
        # 获取请求数据
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "message": "请求体不能为空"
            }), 400

        action = data.get('action')
        if not action:
            return jsonify({
                "success": False,
                "message": "缺少action参数"
            }), 400

        # 根据action执行相应操作
        result = None

        if action == "phonebook_list":
            result = tool.phonebook_list()

        elif action == "phonebook_add":
            name = data.get('contact_name')
            phone = data.get('phone_number')
            alias = data.get('contact_alias', '')
            result = tool.phonebook_add(name, phone, alias)

        elif action == "phonebook_delete":
            name = data.get('contact_name')
            result = tool.phonebook_delete(name)

        elif action == "call":
            phone = data.get('phone_number')
            result = tool.make_call(phone)

        elif action == "sms":
            phone = data.get('phone_number')
            message = data.get('sms_message')
            result = tool.send_sms(phone, message)

        elif action == "volume":
            level = data.get('volume_level')
            if level is not None:
                level = int(level)
            result = tool.control_volume(level)

        elif action == "brightness":
            level = data.get('brightness_level')
            if level is not None:
                level = int(level)
            result = tool.control_brightness(level)

        elif action == "theme":
            mode = data.get('theme_mode')
            result = tool.control_theme(mode)

        else:
            result = {
                "success": False,
                "message": f"未知操作: {action}"
            }

        # 记录操作日志
        logger.info(f"执行操作: {action}, 结果: {result.get('success', False)}")

        return jsonify(result)

    except Exception as e:
        logger.error(f"API调用异常: {e}")
        return jsonify({
            "success": False,
            "message": f"服务器内部错误: {str(e)}"
        }), 500

@app.route('/api/phonebook', methods=['GET'])
def get_phonebook():
    """获取电话本"""
    try:
        result = tool.phonebook_list()
        return jsonify(result)
    except Exception as e:
        logger.error(f"获取电话本异常: {e}")
        return jsonify({
            "success": False,
            "message": f"获取电话本失败: {str(e)}"
        }), 500

@app.route('/api/phonebook', methods=['POST'])
def add_contact():
    """添加联系人"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "message": "请求体不能为空"
            }), 400

        name = data.get('name')
        phone = data.get('phone')
        alias = data.get('alias', '')

        result = tool.phonebook_add(name, phone, alias)
        return jsonify(result)
    except Exception as e:
        logger.error(f"添加联系人异常: {e}")
        return jsonify({
            "success": False,
            "message": f"添加联系人失败: {str(e)}"
        }), 500

@app.route('/api/phonebook/<name>', methods=['DELETE'])
def delete_contact(name):
    """删除联系人"""
    try:
        result = tool.phonebook_delete(name)
        return jsonify(result)
    except Exception as e:
        logger.error(f"删除联系人异常: {e}")
        return jsonify({
            "success": False,
            "message": f"删除联系人失败: {str(e)}"
        }), 500

@app.route('/api/system/volume', methods=['POST'])
def control_system_volume():
    """控制系统音量"""
    try:
        data = request.get_json()
        level = data.get('level')
        if level is not None:
            level = int(level)
        result = tool.control_volume(level)
        return jsonify(result)
    except Exception as e:
        logger.error(f"控制音量异常: {e}")
        return jsonify({
            "success": False,
            "message": f"控制音量失败: {str(e)}"
        }), 500

@app.route('/api/system/brightness', methods=['POST'])
def control_system_brightness():
    """控制屏幕亮度"""
    try:
        data = request.get_json()
        level = data.get('level')
        if level is not None:
            level = int(level)
        result = tool.control_brightness(level)
        return jsonify(result)
    except Exception as e:
        logger.error(f"控制亮度异常: {e}")
        return jsonify({
            "success": False,
            "message": f"控制亮度失败: {str(e)}"
        }), 500

@app.route('/api/system/theme', methods=['POST'])
def control_system_theme():
    """控制系统主题"""
    try:
        data = request.get_json()
        mode = data.get('mode')
        result = tool.control_theme(mode)
        return jsonify(result)
    except Exception as e:
        logger.error(f"控制主题异常: {e}")
        return jsonify({
            "success": False,
            "message": f"控制主题失败: {str(e)}"
        }), 500

@app.route('/api/communication/call', methods=['POST'])
def make_phone_call():
    """拨打电话"""
    try:
        data = request.get_json()
        phone = data.get('phone_number')
        result = tool.make_call(phone)
        return jsonify(result)
    except Exception as e:
        logger.error(f"拨打电话异常: {e}")
        return jsonify({
            "success": False,
            "message": f"拨打电话失败: {str(e)}"
        }), 500

@app.route('/api/communication/sms', methods=['POST'])
def send_sms_message():
    """发送短信"""
    try:
        data = request.get_json()
        phone = data.get('phone_number')
        message = data.get('message')
        result = tool.send_sms(phone, message)
        return jsonify(result)
    except Exception as e:
        logger.error(f"发送短信异常: {e}")
        return jsonify({
            "success": False,
            "message": f"发送短信失败: {str(e)}"
        }), 500

@app.errorhandler(404)
def not_found(error):
    """处理404错误"""
    return jsonify({
        "success": False,
        "message": "接口不存在"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """处理500错误"""
    return jsonify({
        "success": False,
        "message": "服务器内部错误"
    }), 500

if __name__ == '__main__':
    # 获取环境变量中的配置
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'

    print(f"启动Mobile Control Tool API服务器...")
    print(f"服务器地址: http://{host}:{port}")
    print(f"健康检查: http://{host}:{port}/health")
    print(f"API文档: http://{host}:{port}/api/mobile-control")

    app.run(host=host, port=port, debug=debug)
