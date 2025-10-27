import os
import re
import time
import threading
from datetime import datetime
from pathlib import Path

class LogCapture:
    def __init__(self, logger):
        self.logger = logger
        self.is_capturing = False
        self.capture_thread = None
        self.callbacks = []
        self.server_address = None
        self.stream_code = None
        self.lock = threading.Lock()  # 添加线程锁保护共享资源
        self.last_position = {}
        self.last_log_file = None
        self.start_time = 0

    def add_callback(self, callback):
        """添加回调函数"""
        self.callbacks.append(callback)

    def start(self):
        """启动日志模式抓取推流"""
        with self.lock:
            if self.is_capturing:
                self.logger.info("日志抓取已经在运行中")
                return False
            
            self.server_address = None
            self.stream_code = None
            self.last_position.clear()
            self.last_log_file = None
            self.start_time = time.time()
            
            # 获取日志文件夹路径
            log_dir = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "webcast_mate", "logs" )
            
            if not os.path.exists(log_dir):
                self.logger.info("日志文件夹不存在，请确认直播伴侣正确安装")
                return False
                
            self.is_capturing = True
            self.capture_thread = threading.Thread(target=self._capture_log, args=(log_dir,), daemon=True)
            self.capture_thread.start()
            self.logger.info("启动日志模式抓取推流系统")
            return True
    
    def stop(self):
        """停止日志模式抓取推流"""
        with self.lock:
            self.is_capturing = False
        
        if self.capture_thread:
            self.capture_thread.join(timeout=1.5)  # 设置超时避免阻塞
            self.capture_thread = None
        
        self.logger.info("停止日志模式抓取推流系统")
        
    def _get_latest_log_file(self, log_dir):
        """获取最新的日志文件"""
        try:
            # 获取当前时间
            current_time = time.time()
            
            # 优化文件筛选，避免不必要的函数调用
            files = []
            for f in os.listdir(log_dir):
                if "client" in f:  # 先快速筛选，减少系统调用
                    file_path = os.path.join(log_dir, f)
                    if os.path.isfile(file_path):
                        # 只检查较新的文件（3分钟内）
                        if (current_time - os.path.getmtime(file_path)) <= 180:
                            files.append(file_path)
                            
            if not files:
                return None
                
            # 返回修改时间最新的文件
            return max(files, key=os.path.getmtime)
        except Exception as e:
            self.logger.info(f"获取最新日志文件失败: {e}")
            return None
    
    def format_text(self, input_text):
        input_text = input_text.replace('\n', '')
        input_text = ' '.join(input_text.split())
        input_text = input_text.replace('\\', '')
        input_text = input_text.replace('\t', '')
        input_text = input_text.replace('\r', '')
        input_text = input_text.replace('\b', '')
        input_text = input_text.replace('\f', '')
        return input_text

    def _parse_stream_info(self, content):
        """解析推流地址和推流码"""
        try:
            # 优化正则表达式，使用更精确和灵活的匹配
            # 增加多个可能的成功标志匹配
            success_pattern = re.compile(r'(\[startStream\]success|streaming started|推流成功)', re.MULTILINE | re.IGNORECASE)
            
            # 先快速检查是否包含成功标志，避免不必要的复杂匹配
            if success_pattern.search(content):
                # 一次编译多个正则表达式，增加容错性
                url_pattern = re.compile(r'"url":"([^"]+)"')
                # 增加备选匹配模式，适应可能的格式变化
                url_pattern_alt = re.compile(r'url=["\']?([^"\'\s]+)["\']?')
                key_pattern = re.compile(r'"key":"([^"]+)"')
                # 增加备选匹配模式，适应可能的格式变化
                key_pattern_alt = re.compile(r'key=["\']?([^"\'\s]+)["\']?')
                timestamp_pattern = re.compile(r'"timestamp":"([^"]+)"')
                timestamp_pattern_alt = re.compile(r'timestamp=([^\s&]+)')
    
                # 提取信息，尝试多种匹配模式
                url_match = url_pattern.search(content)
                if not url_match:
                    url_match = url_pattern_alt.search(content)
                    
                key_match = key_pattern.search(content)
                if not key_match:
                    key_match = key_pattern_alt.search(content)
                    
                timestamp_match = timestamp_pattern.search(content)
                if not timestamp_match:
                    timestamp_match = timestamp_pattern_alt.search(content)
                    
                if url_match and key_match and timestamp_match:
                    url = url_match.group(1)
                    key = key_match.group(1)
                    timestamp = timestamp_match.group(1)
                    
                    # 清理提取的信息，去除可能的转义字符
                    url = url.replace('\\', '')
                    key = key.replace('\\', '')
                    
                    # 检查时间戳有效性
                    try:
                        current_time = int(time.time())
                        timestamp_value = int(timestamp)
                        # 判断 timestamp 是否在 1 分钟内
                        if current_time - timestamp_value <= 60:  # 增加到1分钟，提高匹配率
                            with self.lock:
                                found_new = False
                                if url != self.server_address:
                                    self.server_address = url
                                    found_new = True
                                    self.logger.info(f"找到推流地址")
                                
                                if key != self.stream_code:
                                    self.stream_code = key
                                    found_new = True
                                    self.logger.info(f"找到推流码")
                                
                                # 如果找到新信息，触发回调
                                if found_new and self.server_address and self.stream_code:
                                    self.is_capturing = False
                                    for callback in self.callbacks:
                                        try:
                                            callback(self.server_address, self.stream_code)
                                        except Exception as e:
                                            self.logger.info(f"回调执行失败: {e}")
                    except ValueError:
                        self.logger.info("无效的时间戳格式")
        except Exception as e:
            self.logger.info(f"解析推流信息失败: {e}")
            
    def _capture_log(self, log_dir):
        """监控日志文件并解析推流信息（使用增量读取优化性能）"""
        log_counter = 0
        check_interval = 2  # 基础检查间隔
        
        while self.is_capturing:
            try:
                # 检查是否超时（10分钟）
                if time.time() - self.start_time > 600:
                    self.logger.info("日志捕获超时，已自动停止")
                    with self.lock:
                        self.is_capturing = False
                    break
                
                # 获取最新日志文件
                current_file = self._get_latest_log_file(log_dir)
                if not current_file:
                    time.sleep(check_interval)
                    continue
                
                # 增量读取文件内容，只读取新的部分
                try:
                    with open(current_file, 'r', encoding='utf-8', errors='ignore') as f:
                        # 获取文件大小
                        f.seek(0, os.SEEK_END)
                        file_size = f.tell()
                        
                        # 确定从哪里开始读取
                        if current_file in self.last_position:
                            start_pos = self.last_position[current_file]
                            # 如果文件变小了（可能是新文件），从头开始读取
                            if start_pos > file_size:
                                start_pos = 0
                        else:
                            start_pos = 0
                        
                        # 只读取新增的内容
                        if start_pos < file_size:
                            f.seek(start_pos)
                            content = f.read()
                            
                            # 更新最后读取位置
                            self.last_position[current_file] = file_size
                            
                            # 只有在有新内容时才进行处理
                            if content.strip():
                                # 每5次检查才输出一次日志，减少日志输出频率
                                log_counter += 1
                                if log_counter % 5 == 0:
                                    self.logger.info("正在通过日志模式获取推流信息，请在直播伴侣开始直播...")
                                    log_counter = 0
                                
                                # 解析新增内容
                                self._parse_stream_info(content)
                                
                                # 如果找到信息，提前结束循环
                                if not self.is_capturing:
                                    break
                except Exception as e:
                    self.logger.info(f"文件读取失败: {e}")
                    # 发生异常时重置位置，下次从头开始读取
                    if current_file in self.last_position:
                        del self.last_position[current_file]
                        
            except Exception as e:
                self.logger.info(f"日志监控异常: {e}")
            
            # 使用自适应检查间隔
            if check_interval < 3 and time.time() - self.start_time > 10:
                check_interval = 3  # 10秒后增加检查间隔，减少CPU使用
                
            time.sleep(check_interval)
        
        self.logger.info("日志捕获已完成或停止")
            
    