console.log('%cCopyright © 2024 zyyo.net',
    'background-color: #ff00ff; color: white; font-size: 24px; font-weight: bold; padding: 10px;'
);
console.log('%c   /\\_/\\', 'color: #8B4513; font-size: 20px;');
console.log('%c  ( o.o )', 'color: #8B4513; font-size: 20px;');
console.log(' %c  > ^ <', 'color: #8B4513; font-size: 20px;');
console.log('  %c /  ~ \\', 'color: #8B4513; font-size: 20px;');
console.log('  %c/______\\', 'color: #8B4513; font-size: 20px;');

document.addEventListener('contextmenu', function (event) {
    event.preventDefault();
});

function handlePress(event) {
    this.classList.add('pressed');
}

function handleRelease(event) {
    this.classList.remove('pressed');
}

function handleCancel(event) {
    this.classList.remove('pressed');
}

var buttons = document.querySelectorAll('.projectItem');
buttons.forEach(function (button) {
    button.addEventListener('mousedown', handlePress);
    button.addEventListener('mouseup', handleRelease);
    button.addEventListener('mouseleave', handleCancel);
    button.addEventListener('touchstart', handlePress);
    button.addEventListener('touchend', handleRelease);
    button.addEventListener('touchcancel', handleCancel);
});

function toggleClass(selector, className) {
    var elements = document.querySelectorAll(selector);
    elements.forEach(function (element) {
        element.classList.toggle(className);
    });
}

function pop(imageURL) {
    var tcMainElement = document.querySelector(".tc-img");
    // 移除之前添加的模态框内容
    const modalContent = document.getElementById('modalContent');
    if (modalContent) {
        modalContent.parentNode.removeChild(modalContent);
    }
    // 显示图片元素并设置最大尺寸
    tcMainElement.style.display = 'block';
    tcMainElement.style.maxWidth = '400px';
    tcMainElement.style.maxHeight = '500px';
    tcMainElement.style.width = 'auto';
    tcMainElement.style.height = 'auto';
    tcMainElement.style.objectFit = 'contain';
    if (imageURL) {
        tcMainElement.src = imageURL;
    }
    toggleClass(".tc-main", "active");
    toggleClass(".tc", "active");
}

var tc = document.getElementsByClassName('tc');
var tc_main = document.getElementsByClassName('tc-main');
tc[0].addEventListener('click', function (event) {
    pop();
});
tc_main[0].addEventListener('click', function (event) {
    event.stopPropagation();
});



function setCookie(name, value, days) {
    var expires = "";
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + days * 24 * 60 * 60 * 1000);
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + value + expires + "; path=/";
}

function getCookie(name) {
    var nameEQ = name + "=";
    var cookies = document.cookie.split(';');
    for (var i = 0; i < cookies.length; i++) {
        var cookie = cookies[i];
        while (cookie.charAt(0) == ' ') {
            cookie = cookie.substring(1, cookie.length);
        }
        if (cookie.indexOf(nameEQ) == 0) {
            return cookie.substring(nameEQ.length, cookie.length);
        }
    }
    return null;
}















document.addEventListener('DOMContentLoaded', function () {
    // 图片延迟加载函数
    function lazyLoadImages() {
        const lazyImages = document.querySelectorAll('[data-src]');
        const skillSection = document.querySelector('.skill');
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.style.display = 'block';
                    observer.unobserve(img);
                }
            });
        });
        
        lazyImages.forEach(img => {
            observer.observe(img);
        });
        
        // 降级方案：如果1秒内没有观察到元素，直接加载
        setTimeout(() => {
            lazyImages.forEach(img => {
                if (!img.src) {
                    img.src = img.dataset.src;
                    img.style.display = 'block';
                }
            });
        }, 1000);
    }
    
    // 初始化延迟加载
    lazyLoadImages();
    
    var html = document.querySelector('html');
    var themeState = getCookie("themeState") || "Light";
    var tanChiShe = document.getElementById("tanChiShe");






    function changeTheme(theme) {
        tanChiShe.src = "./static/svg/snake-" + theme + ".svg";
        html.dataset.theme = theme;
        setCookie("themeState", theme, 365);
        themeState = theme;
    }







    var Checkbox = document.getElementById('myonoffswitch')
    Checkbox.addEventListener('change', function () {
        if (themeState == "Dark") {
            changeTheme("Light");
        } else if (themeState == "Light") {
            changeTheme("Dark");
        } else {
            changeTheme("Dark");
        }
    });



    if (themeState == "Dark") {
        Checkbox.checked = false;
    }

    changeTheme(themeState);

    // 当前设备类型
    let currentDeviceType = 'pc';
    
    // 背景设置面板功能
    function initBackgroundSettings() {
        const settingsBtn = document.getElementById('settingsBtn');
        const panel = document.getElementById('backgroundSettingsPanel');
        const tabButtons = document.querySelectorAll('.tabButton');
        const tabContents = document.querySelectorAll('.tabContent');
        const bgTypeButtons = document.querySelectorAll('.bgTypeButton');
        const wallpaperOptions = document.querySelectorAll('.wallpaperOption');
        // 从cookie加载设备类型设置
        const savedDeviceType = getCookie('deviceType') || 'pc';
        
        // 设置当前设备类型
        currentDeviceType = savedDeviceType;
        
        // 滑块和颜色选择器
        const blurSlider = document.getElementById('blurSlider');
        const brightnessSlider = document.getElementById('brightnessSlider');
        const themeColorPicker = document.getElementById('themeColorPicker');
        const titleColorPicker = document.getElementById('titleColorPicker');
        
        // 按钮
        const resetSettingsBtn = document.getElementById('resetSettingsBtn');
        const cancelSettingsBtn = document.getElementById('cancelSettingsBtn');
        const applySettingsBtn = document.getElementById('applySettingsBtn');
        
        // 存储临时设置
        let tempSettings = {};
        
        // 初始化设置
        function loadSettings() {
            // 优先从localStorage加载，如果没有则从Cookie加载，最后使用默认值
            const savedThemeColor = localStorage.getItem('themeColor') || getCookie('themeColor') || '#FFFFFF';
            const savedTitleColor = localStorage.getItem('titleColor') || getCookie('titleColor') || '#FFFFFF';
            const savedBrightness = localStorage.getItem('backgroundBrightness') || getCookie('backgroundBrightness') || '85';
            const savedBlur = localStorage.getItem('backgroundBlur') || getCookie('backgroundBlur') || '20';
            const savedBackground = localStorage.getItem('backgroundImage') || getCookie('backgroundImage') || './static/img/background.jpg';
            
            // 设置UI元素的值
            themeColorPicker.value = savedThemeColor;
            titleColorPicker.value = savedTitleColor;
            brightnessSlider.value = savedBrightness;
            blurSlider.value = savedBlur;
            
            // 更新显示值
            document.getElementById('brightnessValue').textContent = `当前值: ${parseFloat(savedBrightness).toFixed(1)}`;
            document.getElementById('blurValue').textContent = `当前值: ${parseFloat(savedBlur).toFixed(1)}`;
            
            // 应用设置到页面
            applySettingsToPage(savedThemeColor, savedTitleColor, savedBrightness, savedBlur, savedBackground);
            
            // 更新选中的壁纸
            updateSelectedWallpaper(savedBackground);
            
            // 初始化临时设置
            tempSettings = {
                themeColor: savedThemeColor,
                titleColor: savedTitleColor,
                brightness: savedBrightness,
                blur: savedBlur,
                background: savedBackground
            };
            
            // 同步到全局变量，供其他脚本使用
            window.tempSettings = tempSettings;
        }
        
        // 应用设置到页面
        function applySettingsToPage(themeColor, titleColor, brightness, blur, background) {
            // 应用主题颜色和标题颜色
            document.documentElement.style.setProperty('--text_color', themeColor);
            
            // 应用背景亮度（通过滤镜实现）
            document.querySelector('.zyyo-filter').style.filter = `brightness(${brightness}%)`;
            
            // 应用模糊度
            document.documentElement.style.setProperty('--card_filter', blur + 'px');
            document.documentElement.style.setProperty('--back_filter', blur + 'px');
            
            // 应用背景图片
            document.body.style.backgroundImage = `url(${background})`;
            
            // 确保背景设置面板保持默认模糊效果，不受滑块调整影响
            const settingsPanel = document.getElementById('backgroundSettingsPanel');
            if (settingsPanel) {
                // 使用内联样式覆盖CSS变量，确保在所有浏览器中都能正确应用固定模糊度
                settingsPanel.style.setProperty('--card_filter', '15px', 'important');
                settingsPanel.style.setProperty('--back_filter', '15px', 'important');
                // 同时应用backdropFilter属性，提供更广泛的浏览器支持
                settingsPanel.style.backdropFilter = 'blur(15px)';
                settingsPanel.style.webkitBackdropFilter = 'blur(15px)';
            }
        }
        
        // 添加全局加载动画样式（只添加一次）
        if (!document.getElementById('loading-animation-style')) {
            const style = document.createElement('style');
            style.id = 'loading-animation-style';
            style.textContent = `
                @keyframes spin {
                    to { transform: rotate(360deg); }
                }
                .loading-spinner {
                    display: inline-block;
                    width: 16px;
                    height: 16px;
                    border: 2px solid rgba(255, 255, 255, 0.3);
                    border-radius: 50%;
                    border-top-color: white;
                    animation: spin 1s ease-in-out infinite;
                    margin-right: 8px;
                    vertical-align: middle;
                }
            `;
            document.head.appendChild(style);
        }
        
        // 设置按钮加载状态
        function setButtonLoading(button, isLoading) {
            if (isLoading) {
                // 保存原始文本
                button.dataset.originalText = button.textContent;
                // 设置按钮状态
                button.disabled = true;
                button.style.opacity = '0.7';
                // 使用简单的加载文本，避免创建复杂DOM
                button.innerHTML = '<span class="loading-spinner"></span>加载中...';
            } else {
                // 恢复按钮状态
                button.disabled = false;
                button.style.opacity = '1';
                button.textContent = button.dataset.originalText || button.textContent;
            }
        }
        
        // 保存设置到cookie
    function saveSettings(themeColor, titleColor, brightness, blur, background) {
        setCookie('themeColor', themeColor, 365);
        setCookie('titleColor', titleColor, 365);
        setCookie('backgroundBrightness', brightness, 365);
        setCookie('backgroundBlur', blur, 365);
        setCookie('backgroundImage', background, 365);
        setCookie('deviceType', currentDeviceType, 365);
    }
        
        // 显示成功提示
        function showSuccessMessage(message) {
            // 直接创建模态框，不依赖图片
            const modal = document.createElement('div');
            modal.id = 'successModal';
            modal.style.position = 'fixed';
            modal.style.top = '0';
            modal.style.left = '0';
            modal.style.width = '100%';
            modal.style.height = '100%';
            modal.style.background = 'rgba(0, 0, 0, 0.5)';
            modal.style.display = 'flex';
            modal.style.justifyContent = 'center';
            modal.style.alignItems = 'center';
            modal.style.zIndex = '9999';
            
            // 创建模态框内容
            const modalContent = document.createElement('div');
            modalContent.style.background = 'rgba(255, 255, 255, 0.95)';
            modalContent.style.backdropFilter = 'blur(10px)';
            modalContent.style.borderRadius = '16px';
            modalContent.style.padding = '40px';
            modalContent.style.maxWidth = '400px';
            modalContent.style.width = '90%';
            modalContent.style.textAlign = 'center';
            modalContent.style.boxShadow = '0 12px 40px rgba(0, 0, 0, 0.2)';
            modalContent.style.border = '1px solid rgba(255, 255, 255, 0.3)';
            
            modalContent.innerHTML = '<div style="margin-bottom: 20px; font-size: 48px; color: #4CAF50;">✓</div>' +
                                   `<div style="margin-bottom: 30px; font-weight: 500; font-size: 18px; color: var(--text_color);">${message}</div>` +
                                   '<button id="confirmBtn" style="padding: 12px 40px; background: #4CAF50; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; transition: all 0.3s ease;">确定</button>';
            
            modal.appendChild(modalContent);
            document.body.appendChild(modal);
            
            // 添加关闭事件
            document.getElementById('confirmBtn').addEventListener('click', function() {
                document.body.removeChild(modal);
            });
            
            // 点击背景也可以关闭
            modal.addEventListener('click', function(event) {
                if (event.target === modal) {
                    document.body.removeChild(modal);
                }
            });
        }
        
        // 更新选中的壁纸边框
        function updateSelectedWallpaper(src) {
            wallpaperOptions.forEach(option => {
                if (option.dataset.src === src) {
                    option.style.borderColor = 'var(--primary_color)';
                } else {
                    option.style.borderColor = 'transparent';
                }
            });
        }
        
        // 选项卡切换
        tabButtons.forEach(button => {
            button.addEventListener('click', function() {
                const tabId = this.dataset.tab;
                
                // 移除所有active类
                tabButtons.forEach(btn => btn.classList.remove('active'));
                tabContents.forEach(content => content.classList.remove('active'));
                
                // 添加当前active类
                this.classList.add('active');
                document.getElementById(tabId + 'Tab').classList.add('active');
            });
        });
        
        // 背景类型切换
        bgTypeButtons.forEach(button => {
            button.addEventListener('click', function() {
                const type = this.dataset.type;
                
                // 更新按钮样式
                bgTypeButtons.forEach(btn => {
                    btn.classList.remove('active');
                    btn.style.background = 'none';
                    btn.style.color = 'var(--primary_color)';
                });
                this.classList.add('active');
                this.style.background = 'var(--primary_color)';
                this.style.color = 'white';
                
                // 显示对应内容
                document.getElementById('imageWallpapers').style.display = type === 'image' ? 'block' : 'none';
                // 移除了动态壁纸功能
            });
        });
        
        // 壁纸选择
        wallpaperOptions.forEach(option => {
            option.addEventListener('click', function() {
                const src = this.dataset.src;
                updateSelectedWallpaper(src);
                tempSettings.background = src;
                window.tempSettings = tempSettings; // 同步到全局
                // 实时预览
                document.body.style.backgroundImage = `url(${src})`;
            });
        });
        
        // 主题颜色变化
        themeColorPicker.addEventListener('input', function() {
            tempSettings.themeColor = this.value;
            document.documentElement.style.setProperty('--text_color', this.value);
        });
        
        // 标题颜色变化
        titleColorPicker.addEventListener('input', function() {
            tempSettings.titleColor = this.value;
            // 这里可以添加标题颜色的实时预览
        });
        
        // 亮度滑块变化
        brightnessSlider.addEventListener('input', function() {
            tempSettings.brightness = this.value;
            document.getElementById('brightnessValue').textContent = `当前值: ${parseFloat(this.value).toFixed(1)}`;
            document.querySelector('.zyyo-filter').style.filter = `brightness(${this.value}%)`;
        });
        
        // 模糊度滑块变化
        blurSlider.addEventListener('input', function() {
            tempSettings.blur = this.value;
            document.getElementById('blurValue').textContent = `当前值: ${parseFloat(this.value).toFixed(1)}`;
            document.documentElement.style.setProperty('--card_filter', this.value + 'px');
            document.documentElement.style.setProperty('--back_filter', this.value + 'px');
        });
        
        // 恢复按钮 - 重写版本
        resetSettingsBtn.addEventListener('click', function() {
            const button = this;
            const originalText = button.textContent;
            
            // 显示加载状态
            button.disabled = true;
            button.textContent = '恢复中...';
            button.style.opacity = '0.7';
            
            setTimeout(function() {
                try {
                    // 使用默认值
                    const defaultThemeColor = '#FFFFFF';
                    const defaultTitleColor = '#FFFFFF';
                    const defaultBrightness = '85';
                    const defaultBlur = '20';
                    const defaultBackground = './static/img/background.jpg';
                    
                    // 重置UI
                    themeColorPicker.value = defaultThemeColor;
                    titleColorPicker.value = defaultTitleColor;
                    brightnessSlider.value = defaultBrightness;
                    blurSlider.value = defaultBlur;
                    
                    // 更新显示值
                    document.getElementById('brightnessValue').textContent = `当前值: ${parseFloat(defaultBrightness).toFixed(1)}`;
                    document.getElementById('blurValue').textContent = `当前值: ${parseFloat(defaultBlur).toFixed(1)}`;
                    
                    // 更新临时设置
                    window.tempSettings = {
                        themeColor: defaultThemeColor,
                        titleColor: defaultTitleColor,
                        brightness: defaultBrightness,
                        blur: defaultBlur,
                        background: defaultBackground
                    };
                    
                    // 应用设置（预览）
                    applySettingsToPage(defaultThemeColor, defaultTitleColor, defaultBrightness, defaultBlur, defaultBackground);
                    
                    // 恢复按钮状态
                    button.disabled = false;
                    button.textContent = originalText;
                    button.style.opacity = '1';
                    
                    console.log('已恢复默认设置');
                } catch (error) {
                    console.error('恢复失败:', error);
                    button.disabled = false;
                    button.textContent = originalText;
                    button.style.opacity = '1';
                    alert('恢复失败，请重试');
                }
            }, 500);
        });
        
        // 取消按钮
        cancelSettingsBtn.addEventListener('click', function() {
            panel.style.display = 'none';
            // 重新加载保存的设置
            loadSettings();
        });
        
        // 确认按钮 - 重写版本
        applySettingsBtn.addEventListener('click', function() {
            const button = this;
            const originalText = button.textContent;
            
            // 显示加载状态
            button.disabled = true;
            button.textContent = '保存中...';
            button.style.opacity = '0.7';
            
            setTimeout(function() {
                try {
                    // 获取当前设置值
                    const themeColor = themeColorPicker.value || '#FFFFFF';
                    const titleColor = titleColorPicker.value || '#FFFFFF';
                    const brightness = brightnessSlider.value || '85';
                    const blur = blurSlider.value || '20';
                    const background = (window.tempSettings && window.tempSettings.background) || localStorage.getItem('backgroundImage') || './static/img/background.jpg';
                    
                    // 保存到localStorage（永久缓存）
                    localStorage.setItem('themeColor', themeColor);
                    localStorage.setItem('titleColor', titleColor);
                    localStorage.setItem('backgroundBrightness', brightness);
                    localStorage.setItem('backgroundBlur', blur);
                    localStorage.setItem('backgroundImage', background);
                    
                    // 保存到Cookie作为备份
                    setCookie('themeColor', themeColor, 365);
                    setCookie('titleColor', titleColor, 365);
                    setCookie('backgroundBrightness', brightness, 365);
                    setCookie('backgroundBlur', blur, 365);
                    setCookie('backgroundImage', background, 365);
                    
                    // 应用设置到页面
                    applySettingsToPage(themeColor, titleColor, brightness, blur, background);
                    
                    // 恢复按钮状态
                    button.disabled = false;
                    button.textContent = originalText;
                    button.style.opacity = '1';
                    
                    // 关闭面板
                    panel.style.display = 'none';
                    
                    console.log('设置已保存');
                } catch (error) {
                    console.error('保存失败:', error);
                    button.disabled = false;
                    button.textContent = originalText;
                    button.style.opacity = '1';
                    alert('保存失败，请重试');
                }
            }, 500);
        });
        
        // 设置按钮点击事件
        settingsBtn.addEventListener('click', function() {
            panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
            if (panel.style.display === 'block') {
                // 重新加载当前设置到临时变量
                loadSettings();
            }
        });
        
        // 点击面板外的区域关闭面板
        document.addEventListener('click', function(event) {
            if (panel.style.display === 'block' && 
                !settingsBtn.contains(event.target) && 
                !panel.contains(event.target)) {
                panel.style.display = 'none';
            }
        });
        
        // 初始化加载设置
        loadSettings();
        // 设备类型设置已移除，仅保留必要的cookie存储功能
    }
    
    // 初始化背景设置功能
        if (document.getElementById('settingsBtn') && document.getElementById('backgroundSettingsPanel')) {
            initBackgroundSettings();
        }

    var fpsElement = document.createElement('div');
    fpsElement.id = 'fps';
    fpsElement.style.zIndex = '10000';
    fpsElement.style.position = 'fixed';
    fpsElement.style.left = '0';
    document.body.insertBefore(fpsElement, document.body.firstChild);

    var showFPS = (function () {
        var requestAnimationFrame = window.requestAnimationFrame ||
            window.webkitRequestAnimationFrame ||
            window.mozRequestAnimationFrame ||
            window.oRequestAnimationFrame ||
            window.msRequestAnimationFrame ||
            function (callback) {
                window.setTimeout(callback, 1000 / 60);
            };

        var fps = 0,
            last = Date.now(),
            offset, step, appendFps;

        step = function () {
            offset = Date.now() - last;
            fps += 1;

            if (offset >= 1000) {
                last += offset;
                appendFps(fps);
                fps = 0;
            }

            requestAnimationFrame(step);
        };

        appendFps = function (fpsValue) {
            fpsElement.textContent = 'FPS: ' + fpsValue;
        };

        step();
    })();
    
    
    
    //pop('./static/img/tz.jpg')
    
    
    
});




var pageLoading = document.querySelector("#zyyo-loading");
// 优化加载动画：设置最大加载时间，避免页面长时间不显示
let loadingTimeout;

function hideLoading() {
    pageLoading.style.opacity = "0";
    pageLoading.style.pointerEvents = "none";
    setTimeout(function() {
        pageLoading.style.display = "none";
    }, 500); // 减少淡出时间，更快显示内容
}

// 监听DOMContentLoaded而不是window.load，更快隐藏加载动画
document.addEventListener('DOMContentLoaded', function() {
    // 设置最长加载时间为1.5秒
    loadingTimeout = setTimeout(hideLoading, 1500);
});

// 如果页面完全加载，也隐藏加载动画
window.addEventListener('load', function() {
    clearTimeout(loadingTimeout);
    hideLoading();
});

