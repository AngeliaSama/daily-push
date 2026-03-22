import requests
import os 
from bs4 import BeautifulSoup
from datetime import datetime

# ========== 配置信息（请务必修改）==========
SENDKEY = os.environ.get('SENDKEY')   # 从环境变量获取 SendKey
if not SENDKEY:
    raise ValueError("❌ 错误：环境变量 SENDKEY 未设置！请检查 GitHub Secrets 配置。")
LATITUDE = 27.1                # 纬度
LONGITUDE = 119.63              # 经度
# ==========================================

def send_serverchan(title, content):
    """通过 Server 酱推送消息"""
    url = f"https://sctapi.ftqq.com/{SENDKEY}.send"
    data = {"title": title, "desp": content}
    try:
        r = requests.post(url, data=data, timeout=10)
        if r.json().get('code') == 0:
            print("推送成功")
        else:
            print("推送失败")
    except Exception as e:
        print(f"推送异常: {e}")

def get_weather():
    """获取实时天气以及今日最高/最低气温"""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "current_weather": True,                # 获取当前天气
        "daily": ["temperature_2m_max", "temperature_2m_min"],  # 获取每日最高/最低
        "timezone": "Asia/Shanghai"
    }
    r = requests.get(url, params=params).json()
    
    # 当前天气
    temp = r["current_weather"]["temperature"]
    code = r["current_weather"]["weathercode"]
    
    # 天气代码转文字
    wmap = {0:"晴朗",1:"多云",2:"多云",3:"阴",51:"小雨",61:"雨",71:"雪"}
    weather = wmap.get(code, "未知")
    
    # 今日最高/最低气温（daily 数组第一个元素是今天）
    max_temp = r["daily"]["temperature_2m_max"][0]
    min_temp = r["daily"]["temperature_2m_min"][0]
    
    return temp, max_temp, min_temp, weather

def get_exchange_rate():
    """获取美元汇率（exchangerate-api 免费）"""
    url = "https://api.exchangerate-api.com/v4/latest/USD"
    r = requests.get(url).json()
    return r["rates"]["CNY"]

def get_wuxing_color():
    """爬取五行穿衣颜色，返回格式化的多行字符串"""
    url = "https://www.5adanci.com/wuxingchuanyi/article/jrcydjs.html"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    print(f"网页请求状态: {response.status_code}")

    if response.status_code != 200:
        return "今日五行穿衣：暂未获取到"

    soup = BeautifulSoup(response.text, "lxml")
    container = soup.find(class_="container")
    if not container:
        return "未找到颜色信息"

    # 收集颜色指南行
    color_lines = []
    for p in container.find_all('p'):
        text = p.text.strip()
        # 只提取以数字开头且包含顿号的段落（即1、2、3... 五行指南）
        if text and text[0].isdigit() and '、' in text[:5]:
            color_lines.append(text)

    if not color_lines:
        return "今日五行穿衣：无具体数据"

    # 用换行符连接成多行文本
    return "\n".join(color_lines)

def main():
    temp, max_temp, min_temp, weather = get_weather()   # 现在接收4个返回值
    rate = get_exchange_rate()
    color_raw = get_wuxing_color()

    color_lines = color_raw.split('\n')
    formatted_color = "\n".join([f"- {line}" for line in color_lines])

    today = datetime.now().strftime("%Y年%m月%d日 %A")
    title = f"🌞 {today} 早安提醒"
    content = f"""
### 🌤️ 今日天气
- **当前温度**：{temp}°C
- **最高温度**：{max_temp}°C
- **最低温度**：{min_temp}°C
- **天气状况**：{weather}

### 👕 今日五行穿衣
{formatted_color}

### 💵 美元汇率
- **1 USD** ≈ **{rate:.2f} CNY**

---
✨ 愿你拥有美好的一天！
"""
    send_serverchan(title, content)

if __name__ == "__main__":
    main()
