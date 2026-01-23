/**
 * Sidenotes.js - 将 Markdown 脚注转换为 Tufte 风格的侧边注释
 * 
 * 这个脚本会：
 * 1. 找到所有脚注引用（footnote-ref）和脚注内容（footnotes）
 * 2. 将脚注内容提取出来，创建 sidenote 元素
 * 3. 将 sidenote 插入到脚注引用旁边
 * 4. 隐藏原始的底部脚注区域
 */

document.addEventListener('DOMContentLoaded', function () {
    // 查找所有脚注引用 - Python-Markdown 生成格式: <sup id="fnref:1"><a class="footnote-ref" href="#fn:1">1</a></sup>
    const footnoteRefs = document.querySelectorAll('sup[id^="fnref"] a.footnote-ref');

    if (footnoteRefs.length === 0) {
        return; // 没有脚注，直接返回
    }

    // 查找脚注内容区域（Python-Markdown 生成的）
    const footnotesDiv = document.querySelector('div.footnote');
    if (!footnotesDiv) {
        return;
    }

    // 获取所有脚注内容
    const footnoteItems = footnotesDiv.querySelectorAll('li[id^="fn:"]');
    const footnoteMap = new Map();

    footnoteItems.forEach(item => {
        // 脚注 ID 格式: fn:1, fn:2 等
        const id = item.id;
        if (id) {
            // 提取脚注编号 (fn:1 -> 1)
            const match = id.match(/fn:(.+)/);
            if (match) {
                const key = match[1];
                // 获取脚注内容（去除返回链接）
                const content = item.cloneNode(true);
                const backref = content.querySelector('a.footnote-backref');
                if (backref) {
                    backref.remove();
                }
                // 提取 <p> 标签内的内容，或者直接使用 innerHTML
                const paragraph = content.querySelector('p');
                if (paragraph) {
                    footnoteMap.set(key, paragraph.innerHTML.trim());
                } else {
                    footnoteMap.set(key, content.innerHTML.trim());
                }
            }
        }
    });

    // 为每个脚注引用创建 sidenote
    let sidenoteCounter = 0;
    footnoteRefs.forEach(ref => {
        sidenoteCounter++;
        const href = ref.getAttribute('href');
        if (!href) return;

        // 从 href 中提取脚注 ID (#fn:1 -> 1)
        const match = href.match(/#fn:(.+)/);
        if (!match) return;

        const key = match[1];
        const content = footnoteMap.get(key);
        if (!content) return;

        // 获取脚注引用的父元素 (sup)
        const supElement = ref.closest('sup');
        if (!supElement) return;

        // 创建 sidenote 元素
        const sidenote = document.createElement('span');
        sidenote.className = 'sidenote';
        sidenote.id = 'sidenote-' + sidenoteCounter;

        // 添加编号标签
        const label = document.createElement('span');
        label.className = 'sidenote-number';
        label.textContent = sidenoteCounter + '. ';

        // 创建内容容器
        const contentSpan = document.createElement('span');
        contentSpan.innerHTML = content;

        // 组装 sidenote
        sidenote.appendChild(label);
        sidenote.appendChild(contentSpan);

        // 将 sidenote 插入到 sup 元素之后
        supElement.parentNode.insertBefore(sidenote, supElement.nextSibling);

        // 为脚注引用添加关联
        ref.setAttribute('data-sidenote', sidenoteCounter);

        // 阻止默认的锚点跳转行为
        ref.addEventListener('click', function (e) {
            e.preventDefault();

            // 在移动端，滚动到 sidenote 并高亮
            if (window.innerWidth <= 760) {
                sidenote.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }

            // 高亮效果
            sidenote.classList.add('highlighted');
            setTimeout(() => sidenote.classList.remove('highlighted'), 2000);
        });
    });

    // 隐藏原始的底部脚注区域（CSS 也会隐藏，这是双重保险）
    footnotesDiv.style.display = 'none';
});
