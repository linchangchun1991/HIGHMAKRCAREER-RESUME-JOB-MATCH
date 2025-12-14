#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试脚本：测试各平台选择器是否生效
"""

from DrissionPage import ChromiumPage, ChromiumOptions
import time
import os

def debug():
    """调试抖音和小红书的选择器"""
    
    try:
        # 尝试连接调试端口
        try:
            page = ChromiumPage(addr='127.0.0.1:9222')
            print("✅ 成功连接到 Chrome 调试端口 (9222)")
        except:
            print("⚠️ 无法连接调试端口，使用普通模式")
            co = ChromiumOptions()
            co.headless(False)
            page = ChromiumPage(addr_or_opts=co)
        
        print("\n" + "="*60)
        print("🔍 调试抖音 - 综合搜索")
        print("="*60)
        
        # 访问抖音搜索页
        page.get("https://www.douyin.com/search/留学辅导?type=general")
        time.sleep(5)
        
        # 尝试点击"综合"Tab
        try:
            general_tab = page.ele('text:综合', timeout=3)
            if general_tab:
                general_tab.click()
                print("✅ 已点击'综合'Tab")
                time.sleep(2)
        except:
            print("⚠️ 未找到'综合'Tab")
        
        # 截图
        try:
            page.get_screenshot(name='douyin_debug.png', full_page=True)
            print("📸 截图已保存: douyin_debug.png")
        except:
            pass
        
        # 打印当前URL
        print(f"当前URL: {page.url}")
        
        # 打印页面HTML前500字符
        try:
            html_preview = page.html[:500] if hasattr(page, 'html') else "无法获取HTML"
            print(f"页面前500字符: {html_preview}")
        except:
            pass
        
        # 尝试多种选择器
        print("\n尝试查找元素:")
        selectors_to_try = [
            'css:div[data-e2e="scroll-list"]',
            'css:ul.search-result-list',
            'css:div.search-result-card',
            'css:li[class*="result"]',
            'css:a[href*="/video/"]',
            'xpath://div[contains(@class, "search-result")]',
            'xpath://a[contains(@href, "/video/")]',
            'xpath://div[contains(@data-e2e, "scroll")]',
        ]
        
        for sel in selectors_to_try:
            try:
                eles = page.eles(sel, timeout=3)
                print(f"  ✅ {sel}: 找到 {len(eles)} 个元素")
                if eles and len(eles) > 0:
                    try:
                        first_text = eles[0].text[:50] if eles[0].text else 'no text'
                        print(f"      首个元素文本: {first_text}")
                    except:
                        pass
            except Exception as e:
                print(f"  ❌ {sel}: 失败 - {str(e)[:50]}")
        
        print("\n" + "="*60)
        print("🔍 调试小红书")
        print("="*60)
        
        # 访问小红书搜索页
        page.get("https://www.xiaohongshu.com/search_result?keyword=留学辅导&source=web_search_result_notes")
        time.sleep(5)
        
        # 截图
        try:
            page.get_screenshot(name='xhs_debug.png', full_page=True)
            print("📸 截图已保存: xhs_debug.png")
        except:
            pass
        
        # 打印当前URL
        print(f"当前URL: {page.url}")
        
        # 尝试多种选择器
        print("\n尝试查找元素:")
        selectors_to_try = [
            'css:section.note-item',
            'css:div.note-item',
            'css:div[class*="note-item"]',
            'css:a.cover',
            'css:div[class*="note"]',
            'xpath://section[contains(@class, "note")]',
            'xpath://div[contains(@class, "note-item")]',
            'xpath://a[contains(@href, "/explore/")]',
        ]
        
        for sel in selectors_to_try:
            try:
                eles = page.eles(sel, timeout=3)
                print(f"  ✅ {sel}: 找到 {len(eles)} 个元素")
                if eles and len(eles) > 0:
                    try:
                        first_text = eles[0].text[:50] if eles[0].text else 'no text'
                        print(f"      首个元素文本: {first_text}")
                    except:
                        pass
            except Exception as e:
                print(f"  ❌ {sel}: 失败 - {str(e)[:50]}")
        
        print("\n" + "="*60)
        print("✅ 调试完成！请查看截图确认页面是否正常加载。")
        print("="*60)
        
    except Exception as e:
        print(f"❌ 调试过程出错: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug()
