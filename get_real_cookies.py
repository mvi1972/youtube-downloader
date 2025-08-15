#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для получения реальных cookies из браузера через Selenium
"""
import os
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import browser_cookie3
import requests

class CookieExtractor:
    def __init__(self):
        self.cookies_dir = "cookies"
        os.makedirs(self.cookies_dir, exist_ok=True)
        
    def get_cookies_chrome(self):
        """Получение cookies из Chrome браузера"""
        try:
            # Получаем cookies для YouTube из Chrome
            cj = browser_cookie3.chrome(domain_name='.youtube.com')
            cookies = []
            for cookie in cj:
                cookies.append({
                    'name': cookie.name,
                    'value': cookie.value,
                    'domain': cookie.domain,
                    'path': cookie.path,
                    'expires': cookie.expires,
                    'secure': cookie.secure,
                    'httpOnly': cookie.has_nonstandard_attr('HttpOnly')
                })
            return cookies
        except Exception as e:
            print(f"Ошибка при получении cookies из Chrome: {e}")
            return []

    def get_cookies_firefox(self):
        """Получение cookies из Firefox браузера"""
        try:
            cj = browser_cookie3.firefox(domain_name='.youtube.com')
            cookies = []
            for cookie in cj:
                cookies.append({
                    'name': cookie.name,
                    'value': cookie.value,
                    'domain': cookie.domain,
                    'path': cookie.path,
                    'expires': cookie.expires,
                    'secure': cookie.secure,
                    'httpOnly': cookie.has_nonstandard_attr('HttpOnly')
                })
            return cookies
        except Exception as e:
            print(f"Ошибка при получении cookies из Firefox: {e}")
            return []

    def get_cookies_selenium(self, email=None, password=None):
        """Получение cookies через Selenium с авторизацией"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Открываем YouTube
            driver.get("https://www.youtube.com")
            time.sleep(3)
            
            # Если указаны email и password, выполняем вход
            if email and password:
                # Кликаем на кнопку входа
                sign_in_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[@aria-label='Sign in']"))
                )
                sign_in_button.click()
                
                # Вводим email
                email_field = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "identifierId"))
                )
                email_field.send_keys(email)
                email_field.send_keys(Keys.RETURN)
                
                time.sleep(2)
                
                # Вводим пароль
                password_field = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.NAME, "Passwd"))
                )
                password_field.send_keys(password)
                password_field.send_keys(Keys.RETURN)
                
                # Ждем загрузки страницы
                time.sleep(5)
            
            # Получаем cookies
            cookies = driver.get_cookies()
            driver.quit()
            
            return cookies
            
        except Exception as e:
            print(f"Ошибка при получении cookies через Selenium: {e}")
            return []

    def save_cookies_netscape(self, cookies, filename="cookies.txt"):
        """Сохранение cookies в формате Netscape"""
        try:
            filepath = os.path.join(self.cookies_dir, filename)
            with open(filepath, 'w') as f:
                f.write("# Netscape HTTP Cookie File\n")
                f.write("# This is a generated file! Do not edit.\n")
                
                for cookie in cookies:
                    domain = cookie['domain']
                    if not domain.startswith('.'):
                        domain = '.' + domain
                    
                    secure = 'TRUE' if cookie.get('secure', False) else 'FALSE'
                    http_only = 'TRUE' if cookie.get('httpOnly', False) else 'FALSE'
                    expires = str(int(cookie.get('expires', 0))) if cookie.get('expires') else '0'
                    
                    f.write(f"{domain}\t{http_only}\t{cookie.get('path', '/')}\t{secure}\t{expires}\t{cookie['name']}\t{cookie['value']}\n")
            
            print(f"Cookies сохранены в {filepath}")
            return filepath
            
        except Exception as e:
            print(f"Ошибка при сохранении cookies: {e}")
            return None

    def save_cookies_json(self, cookies, filename="cookies.json"):
        """Сохранение cookies в JSON формате"""
        try:
            filepath = os.path.join(self.cookies_dir, filename)
            with open(filepath, 'w') as f:
                json.dump(cookies, f, indent=2)
            print(f"Cookies сохранены в {filepath}")
            return filepath
        except Exception as e:
            print(f"Ошибка при сохранении cookies в JSON: {e}")
            return None

    def verify_cookies(self, cookies_file):
        """Проверка работоспособности cookies"""
        try:
            with open(cookies_file, 'r') as f:
                cookies = []
                for line in f:
                    if line.startswith('#') or not line.strip():
                        continue
                    parts = line.strip().split('\t')
                    if len(parts) >= 7:
                        cookies.append({
                            'name': parts[5],
                            'value': parts[6],
                            'domain': parts[0]
                        })
            
            # Проверяем наличие важных cookies
            important_cookies = ['SAPISID', 'HSID', 'SSID', 'SID', 'LOGIN_INFO', 'PREF']
            found_cookies = [c['name'] for c in cookies]
            
            print(f"Найденные важные cookies: {set(important_cookies) & set(found_cookies)}")
            return len(set(important_cookies) & set(found_cookies)) >= 3
            
        except Exception as e:
            print(f"Ошибка при проверке cookies: {e}")
            return False

def main():
    extractor = CookieExtractor()
    
    print("=== Получение cookies для YouTube ===")
    
    # Пробуем получить cookies из браузеров
    print("\n1. Попытка получить cookies из Chrome...")
    chrome_cookies = extractor.get_cookies_chrome()
    
    print("\n2. Попытка получить cookies из Firefox...")
    firefox_cookies = extractor.get_cookies_firefox()
    
    # Используем cookies из Chrome если они есть, иначе из Firefox
    cookies = chrome_cookies if chrome_cookies else firefox_cookies
    
    if cookies:
        print(f"\nНайдено {len(cookies)} cookies")
        
        # Сохраняем в формате Netscape для yt-dlp
        netscape_file = extractor.save_cookies_netscape(cookies)
        
        # Сохраняем в JSON для отладки
        json_file = extractor.save_cookies_json(cookies)
        
        # Проверяем cookies
        if netscape_file:
            is_valid = extractor.verify_cookies(netscape_file)
            print(f"\nCookies валидны: {is_valid}")
            
            print(f"\nГотово! Используйте файл: {netscape_file}")
    else:
        print("\nCookies не найдены. Попробуйте войти в YouTube в браузере и запустите скрипт снова.")
        
        # Предлагаем ручной ввод
        choice = input("\nХотите получить cookies через Selenium? (y/n): ")
        if choice.lower() == 'y':
            email = input("Email YouTube (оставьте пустым для пропуска): ").strip()
            password = input("Пароль (оставьте пустым для пропуска): ").strip()
            
            selenium_cookies = extractor.get_cookies_selenium(
                email if email else None,
                password if password else None
            )
            
            if selenium_cookies:
                netscape_file = extractor.save_cookies_netscape(selenium_cookies)
                print(f"\nCookies получены через Selenium: {netscape_file}")

if __name__ == "__main__":
    main()