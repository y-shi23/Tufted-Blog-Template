/**
 * 主题切换功能
 * 
 * 支持三种状态：
 * 1. 用户未设置偏好 - 跟随系统
 * 2. 用户手动选择深色模式
 * 3. 用户手动选择浅色模式
 */
(function() {
    const STORAGE_KEY = 'theme-preference';
    
    // 获取用户保存的主题偏好
    function getStoredTheme() {
        try {
            return localStorage.getItem(STORAGE_KEY);
        } catch (e) {
            return null;
        }
    }
    
    // 保存用户主题偏好
    function setStoredTheme(theme) {
        try {
            localStorage.setItem(STORAGE_KEY, theme);
        } catch (e) {
            // localStorage not available
        }
    }
    
    // 获取系统偏好的主题
    function getSystemTheme() {
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    
    // 获取当前应该应用的主题
    function getCurrentTheme() {
        const storedTheme = getStoredTheme();
        if (storedTheme) {
            return storedTheme;
        }
        return getSystemTheme();
    }
    
    // 应用主题到文档
    function applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        updateToggleButton(theme);
    }
    
    // 更新切换按钮的状态
    function updateToggleButton(theme) {
        const button = document.getElementById('theme-toggle');
        if (!button) return;
        
        if (theme === 'dark') {
            button.classList.add('is-dark');
            button.setAttribute('aria-label', '切换到浅色模式');
        } else {
            button.classList.remove('is-dark');
            button.setAttribute('aria-label', '切换到深色模式');
        }
    }
    
    // 切换主题
    function toggleTheme() {
        const currentTheme = getCurrentTheme();
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        setStoredTheme(newTheme);
        applyTheme(newTheme);
    }
    
    // 创建切换按钮 (DeepWiki 风格)
    function createToggleButton() {
        const button = document.createElement('button');
        button.id = 'theme-toggle';
        button.className = 'theme-toggle-btn';
        button.type = 'button';
        button.setAttribute('aria-label', '切换主题');
        
        // DeepWiki 风格: 两个图标并排，滑动指示器
        button.innerHTML = `
            <span class="toggle-track">
                <span class="toggle-icon toggle-icon-sun">
                    <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor">
                        <circle cx="12" cy="12" r="4"></circle>
                        <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"></path>
                    </svg>
                </span>
                <span class="toggle-icon toggle-icon-moon">
                    <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor">
                        <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
                    </svg>
                </span>
                <span class="toggle-thumb"></span>
            </span>
        `;
        
        button.addEventListener('click', toggleTheme);
        
        return button;
    }
    
    // 初始化
    function init() {
        // 在 DOM 加载完成前先应用主题以防止闪烁
        const theme = getCurrentTheme();
        document.documentElement.setAttribute('data-theme', theme);
        
        // DOM 加载完成后添加按钮
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', onDOMReady);
        } else {
            onDOMReady();
        }
    }
    
    function onDOMReady() {
        const button = createToggleButton();
        
        // 查找 header nav 元素，将按钮添加到导航栏中
        const nav = document.querySelector('header nav');
        if (nav) {
            nav.appendChild(button);
        } else {
            // 如果没有 nav，则添加到 body
            document.body.appendChild(button);
        }
        
        // 更新按钮状态
        updateToggleButton(getCurrentTheme());
        
        // 监听系统主题变化
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(e) {
            // 只有在用户没有手动设置偏好时才跟随系统
            if (!getStoredTheme()) {
                applyTheme(e.matches ? 'dark' : 'light');
            }
        });
    }
    
    // 立即执行初始化
    init();
})();
