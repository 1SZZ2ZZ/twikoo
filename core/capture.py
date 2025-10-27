from scapy.all import sniff, IP, TCP, Raw
import re
import threading
import time
from datetime import datetime


class PacketCapture:
    def __init__(self, logger):
        self.logger = logger
        self.is_capturing = False
        self.capture_thread = None
        self.callbacks = []
        self.server_address = None
        self.stream_code = None
        self.capture_threads = {}
        self.interface_status = {}
        self.lock = threading.RLock()  # 使用可重入锁，支持嵌套锁
        self.max_retries = 3  # 最大重试次数
        self.retry_interval = 5  # 重试间隔（秒）
        self.timeout = 120  # 总超时时间（秒）
        self.start_time = None  # 开始捕获时间

    def start(self, interface_display_name):
        """开始捕获数据包"""
        if self.is_capturing:
            self.logger.info("捕获已经在运行中")
            return

        try:
            # 快速清理之前的状态
            with self.lock:
                self.server_address = None
                self.stream_code = None
            
            # 从显示名称中提取实际的接口名称
            interface = interface_display_name.split(" [")[0].strip()

            # 获取Windows网络接口列表（使用缓存优化）
            from scapy.arch.windows import get_windows_if_list
            interfaces = get_windows_if_list()

            # 快速查找匹配的接口
            interface_found = None
            for iface in interfaces:
                if iface.get("name") == interface:
                    interface_found = iface.get("name")
                    break

            if not interface_found:
                self.logger.error(f"找不到网络接口: {interface}")
                return

            # 初始化接口状态
            self.interface_status = {interface_found: True}
            self.is_capturing = True
            
            # 创建新的捕获线程
            self.capture_thread = threading.Thread(
                target=self._start_capture, 
                args=(interface_found,),
                daemon=True  # 设置为守护线程，主程序结束时自动终止
            )
            self.capture_thread.start()
            self.logger.info(f"开始在接口 {interface_found} 上捕获数据包")
            
        except Exception as e:
            self.logger.error(f"启动捕获时发生错误: {str(e)}，如果检测可用，则忽略此错误")
            self.is_capturing = False
            # 确保接口状态被正确设置
            for iface in self.interface_status:
                self.interface_status[iface] = False

    def stop(self):
        """停止捕获数据包"""
        if not self.is_capturing:
            self.logger.info("捕获已经停止")
            return

        # 调用统一的停止方法
        self._stop_all_capture()

        # 等待主线程完成
        if hasattr(self, 'capture_thread') and self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=1.5)  # 减少等待时间以提高响应速度

        # 等待所有多接口捕获线程完成
        current_thread = threading.current_thread()
        active_threads = []
        for interface, thread in list(self.capture_threads.items()):
            if thread and thread.is_alive() and current_thread != thread:
                active_threads.append(thread)
                
        for thread in active_threads:
            thread.join(timeout=1.5)

        # 清理线程记录
        self.capture_threads.clear()
        self.capture_thread = None
        
        # 如果有回调函数，通知捕获完成
        with self.lock:
            if hasattr(self, 'on_complete') and self.on_complete and self.server_address and self.stream_code:
                try:
                    self.on_complete(self.server_address, self.stream_code)
                except Exception as e:
                    self.logger.error(f"执行完成回调时发生错误: {str(e)}")
                    
        self.logger.info("停止所有接口的数据包捕获")
        
    def _stop_all_capture(self):
        """内部方法：停止所有捕获并清理资源"""
        with self.lock:
            self.is_capturing = False
            # 设置所有接口状态为False，触发停止过滤条件
            for iface in self.interface_status:
                self.interface_status[iface] = False
                
    def _timeout_monitor(self):
        """监控捕获超时并自动停止"""
        start_time = self.start_time
        if not start_time:
            return
            
        while self.is_capturing:
            # 检查是否超时
            elapsed = (datetime.now() - start_time).total_seconds()
            if elapsed > self.timeout:
                self.logger.warning(f"捕获超时（{self.timeout}秒），自动停止")
                with self.lock:
                    if self.is_capturing:  # 再次检查，避免竞态条件
                        self._stop_all_capture()
                        # 如果没有找到数据，记录错误
                        if not self.server_address or not self.stream_code:
                            self.logger.error("捕获超时，未找到推流服务器地址或推流码")
                break
            
            # 每5秒检查一次
            time.sleep(5)


    def add_callback(self, callback):
        """添加回调函数"""
        self.callbacks.append(callback)

    def start_multi(self, interfaces):
        """开始多接口捕获"""
        if self.is_capturing:
            self.logger.info("捕获已经在运行中")
            return

        try:
            # 使用线程锁保护共享资源的初始化
            with self.lock:
                self.server_address = None
                self.stream_code = None
                self.start_time = datetime.now()
            
            # 初始化状态变量
            self.is_capturing = True
            self.capture_threads.clear()  # 清理之前的线程记录
            self.interface_status.clear()  # 清空接口状态
            
            # 启动超时监控线程
            threading.Thread(target=self._timeout_monitor, daemon=True).start()

            # 获取Windows网络接口列表（一次获取，多次使用）
            from scapy.arch.windows import get_windows_if_list
            windows_interfaces = get_windows_if_list()

            # 创建一个映射字典，支持模糊匹配
            interface_map = {}
            for iface in windows_interfaces:
                name = iface.get("name")
                if name:
                    interface_map[name.lower()] = name
                    # 添加友好名称支持
                    friendly_name = iface.get("description", "").lower()
                    if friendly_name:
                        interface_map[friendly_name] = name

            # 启动所有有效接口的捕获线程
            for interface_display_name in interfaces:
                try:
                    # 从显示名称中提取实际的接口名称
                    interface = interface_display_name.split(" [")[0].strip()
                    interface_lower = interface.lower()

                    # 优先精确匹配，然后尝试模糊匹配
                    interface_found = interface_map.get(interface_lower)
                    
                    # 如果精确匹配失败，尝试部分匹配
                    if not interface_found:
                        for key in interface_map:
                            if interface_lower in key or key in interface_lower:
                                interface_found = interface_map[key]
                                break

                    if interface_found:
                        # 初始化接口状态
                        self.interface_status[interface_found] = True
                        # 为每个接口创建独立的捕获线程
                        thread = threading.Thread(
                            target=self._start_capture, 
                            args=(interface_found,),
                            daemon=True
                        )
                        thread.start()
                        self.capture_threads[interface_found] = thread
                        self.logger.info(f"开始在接口 {interface_found} 上捕获数据包")
                except Exception as e:
                    self.logger.error(
                        f"启动接口 {interface_display_name} 捕获时发生错误: {str(e)}，如果检测可用，则忽略此错误"
                    )
                    
        except Exception as e:
            self.logger.error(f"启动多接口捕获时发生错误: {str(e)}")
            self.is_capturing = False
            # 确保所有接口状态被正确设置
            for iface in self.interface_status:
                self.interface_status[iface] = False

    def _start_capture(self, interface):
        """实际的捕获过程，包含重试逻辑"""
        retry_count = 0
        success = False
        
        while retry_count <= self.max_retries and self.is_capturing and not success:
            try:
                # 设置初始状态
                self.interface_status[interface] = True
                
                # 扩展过滤器以捕获更多可能的推流相关端口和协议
                # 包含RTMP(1935)、HTTP(80)、HTTPS(443)、RTSP(554)、HTTP替代端口(8080)等
                filter_str = "tcp port 1935 or tcp port 80 or tcp port 443 or tcp port 554 or tcp port 8080 or tcp port 8443 or tcp port 1936 or tcp port 8000"
                
                if retry_count > 0:
                    self.logger.info(f"接口 {interface} 重试捕获，第 {retry_count} 次尝试")
                
                # 优化sniff参数以提高性能
                sniff(
                    iface=interface,
                    prn=lambda x: self._packet_callback(x, interface), 
                    stop_filter=lambda x: not self.interface_status.get(interface, False),
                    filter=filter_str,
                    store=False,  # 不存储捕获的数据包，减少内存占用
                    timeout=40,   # 每次尝试的超时时间
                    session=None, # 不使用会话跟踪，减少处理开销
                    started_callback=lambda: self.logger.info(f"接口 {interface} 捕获已启动")
                )
                
                # 如果正常退出sniff函数，检查是否是因为找到了数据而停止
                success = self.server_address is not None and self.stream_code is not None
                if not success and self.is_capturing:
                    retry_count += 1
                    if retry_count <= self.max_retries:
                        self.logger.warning(f"接口 {interface} 未捕获到数据，将在 {self.retry_interval} 秒后重试")
                        time.sleep(self.retry_interval)
                        # 重新设置状态
                        with self.lock:
                            self.interface_status[interface] = True
                    else:
                        self.logger.error(f"接口 {interface} 已达到最大重试次数，停止捕获")
                        self.interface_status[interface] = False
                        # 检查是否所有接口都失败了
                        if all(not status for status in self.interface_status.values()) and self.is_capturing:
                            self.logger.error("所有接口均捕获失败，请检查网络连接和权限设置")
                            self._stop_all_capture()
            
            except Exception as e:
                retry_count += 1
                error_msg = str(e)
                # 忽略常见的非致命错误
                if "Permission denied" in error_msg:
                    self.logger.error(f"接口 {interface} 权限不足，请以管理员身份运行程序")
                    self.interface_status[interface] = False
                    break  # 权限错误不需要重试
                else:
                    self.logger.error(f"接口 {interface} 捕获过程中发生错误: {error_msg}")
                    if retry_count <= self.max_retries and self.is_capturing:
                        self.logger.info(f"{self.retry_interval} 秒后重试接口 {interface} 捕获")
                        time.sleep(self.retry_interval)
                    else:
                        self.logger.error(f"接口 {interface} 已达到最大重试次数，停止捕获")
                        self.interface_status[interface] = False

    def _packet_callback(self, packet, interface):
        """处理捕获的数据包，增强错误处理和鲁棒性"""
        try:
            # 快速判断 - 只处理包含IP、TCP和Raw层的数据包
            if IP in packet and TCP in packet and Raw in packet:
                # 使用线程锁检查是否已经找到所需信息，如果已找到则快速返回
                with self.lock:
                    if self.server_address and self.stream_code:
                        # 如果已经找到了服务器地址和推流码，停止捕获
                        self.interface_status[interface] = False
                        return
                
                try:
                    # 只在需要查找信息时才解码payload
                    payload_bytes = packet[Raw].load
                    # 尝试多种编码格式解码，提高成功率
                    encoding_attempts = ['utf-8', 'latin-1', 'cp1252']
                    payload = None
                    for encoding in encoding_attempts:
                        try:
                            payload = payload_bytes.decode(encoding)
                            break
                        except UnicodeDecodeError:
                            continue
                    
                    if payload is None:
                        # 如果所有编码都失败，使用错误忽略模式
                        payload = payload_bytes.decode('utf-8', errors='ignore')
                    
                    # 使用线程锁保护共享资源的访问
                    with self.lock:
                        # 扩展关键词匹配，支持多种可能的连接标识
                        if not self.server_address and any(kw in payload.lower() for kw in ["connect", "rtmp://", "tcurl"]):
                            # 优化后的服务器地址正则表达式，支持更多可能的格式
                            server_match = re.search(
                                r"(rtmp://[a-zA-Z0-9\-\.]+(:\d+)?/[^/\s\x00]+)", payload
                            )
                            if server_match:
                                # 清理可能的控制字符
                                self.server_address = server_match.group(1).split("\x00")[0].strip()
                                self.logger.info(f"\n>>> 找到推流服务器地址 <<<\n地址:{self.server_address}")

                        # 扩展关键词匹配，支持多种可能的推流发布标识
                        if not self.stream_code and any(kw in payload for kw in ["FCPublish", "publish", "stream-"]):
                            # 优化后的推流码正则表达式，支持更多字符类型和格式变化
                            code_match = re.search(
                                r"(stream-\d+\?[a-zA-Z0-9_\-]+=[a-zA-Z0-9_\-\%]+(?:&[a-zA-Z0-9_\-]+=[a-zA-Z0-9_\-\%]+)*)",
                                payload,
                            )
                            if code_match:
                                self.stream_code = code_match.group(1).strip()
                                if self.stream_code.endswith("C"):
                                    self.stream_code = self.stream_code[:-1]
                                self.logger.info(f"\n>>> 找到推流码 <<<\n推流码:{self.stream_code}")

                        # 当两个信息都获取到时，停止所有接口的捕获
                        if self.server_address and self.stream_code:
                            # 先触发回调
                            for callback in self.callbacks:
                                try:
                                    callback(self.server_address, self.stream_code)
                                except Exception as e:
                                    self.logger.error(f"执行回调函数时发生错误: {str(e)}")
                            # 停止所有接口的捕获
                            self._stop_all_capture()
                            self.logger.info("已获取所需信息，停止所有接口捕获")

                except Exception as inner_e:
                    # 更详细的错误处理，只记录重要错误
                    if isinstance(inner_e, UnicodeDecodeError):
                        # 忽略常见的解码错误
                        pass
                    else:
                        self.logger.debug(f"处理数据包时的次要错误: {str(inner_e)}")  # 使用debug级别避免日志过多

        except Exception as e:
            self.logger.error(f"处理数据包时发生严重错误: {str(e)}")

    def test_capture(self, interfaces, callback):
        """测试接口是否可以捕获到数据
        
        Args:
            interfaces: 要测试的接口列表
            callback: 测试完成的回调函数，参数为布尔值表示是否检测到数据
        """
        def _test():
            try:
                # 获取Windows网络接口列表
                from scapy.arch.windows import get_windows_if_list
                windows_interfaces = get_windows_if_list()
                
                has_data = False
                # 使用一个较短的超时时间和过滤器来提高效率
                short_timeout = 3  # 减少为3秒
                basic_filter = "tcp or udp"  # 只捕获TCP或UDP数据包
                
                for interface_display_name in interfaces:
                    # 从显示名称中提取实际的接口名称
                    interface = interface_display_name.split(" [")[0].strip()
                    
                    # 查找匹配的接口
                    interface_found = None
                    for iface in windows_interfaces:
                        if iface.get("name") == interface:
                            interface_found = iface.get("name")
                            break
                    
                    if interface_found:
                        # 使用回调函数来统计是否捕获到数据包
                        packet_found = [False]  # 使用列表作为可变对象来在回调中修改
                        
                        def packet_handler(packet):
                            packet_found[0] = True  # 设置标志表示找到了数据包
                            return True  # 继续捕获直到满足条件
                        
                        # 使用优化的参数进行短时间捕获
                        sniff(
                            iface=interface_found, 
                            timeout=short_timeout, 
                            filter=basic_filter,
                            store=False,
                            prn=packet_handler,
                            stop_filter=lambda p: packet_found[0],  # 一旦找到数据包就停止
                            count=1  # 只需要捕获1个包即可
                        )
                        
                        # 检查是否找到了数据包
                        if packet_found[0]:
                            has_data = True
                            break  # 找到一个可用接口就可以停止测试
                
                # 调用回调函数
                callback(has_data)
                
            except Exception as e:
                self.logger.error(f"测试捕获时发生错误: {str(e)}")
                callback(False)
        
        # 在新线程中运行测试
        threading.Thread(target=_test, daemon=True).start()
