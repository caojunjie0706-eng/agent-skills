---
name: douyin-product-link-parser
description: >-
  自动识别并解析抖音商品分享链接，提取商品ID及详情。
  当用户消息中包含 v.douyin.com 短链接，或出现"抖音商城"+"长按复制此条消息，打开抖音搜索"等典型抖音分享口令格式时，必须立即触发此 Skill，无需等待用户明确说出"解析"或"提取"。
  用户发来这类链接的默认意图就是获取商品信息，直接解析输出，不要反问确认。
  适用于商品case排查、商品信息快速定位等场景。
  USE WHEN: 用户消息中包含抖音商品分享链接或口令。
  DO NOT USE WHEN: 非抖音链接、其他电商平台链接。
---

## 触发规则（最高优先级）

**当用户消息中包含以下任一特征时，立即自动执行解析，不要反问、不要确认、不要等待用户补充信息：**

1. 包含 `https://v.douyin.com/` 短链接
2. 包含 `【抖音商城】` + `长按复制此条消息，打开抖音搜索`
3. 包含 `haohuo.jinritemai.com/ecommerce/trade/detail/` 商品详情链接

用户发来这类消息的唯一目的就是获取商品信息，直接解析输出即可。

## 功能说明

从抖音App分享的商品链接中提取商品ID。用户通过抖音App → 分享 → 复制链接，将链接发送给你，你需要解析出商品ID。

## 核心流程

### 1. 识别链接

从用户消息中提取 v.douyin.com 短链接。典型格式：
```
3.53 01/12 sEh:/ H@V.YM 【抖音商城】https://v.douyin.com/Riw-sVBtUlY/ KWEICHOW MOUTAI/贵州茅台... 长按复制此条消息，打开抖音搜索，查看商品详情！
```

链接特征是 `https://v.douyin.com/` 开头的短URL。

### 2. 跟随重定向获取真实URL

使用 curl 跟随短链接重定向，获取 `haohuo.jinritemai.com` 的真实商品页URL：

```bash
curl -sL -o /dev/null -w "%{url_effective}" "https://v.douyin.com/XXXXX/" \
  -H "User-Agent: Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36" \
  --max-time 15
```

关键参数说明：
- `-sL`: 静默模式 + 自动跟随重定向
- `-w "%{url_effective}"`: 输出最终重定向后的URL
- `-o /dev/null`: 丢弃响应体，只关心URL
- 必须使用移动端 User-Agent，否则可能无法正确重定向

### 3. 从URL中提取商品ID

真实URL格式为 `haohuo.jinritemai.com/ecommerce/trade/detail/index.html?...&id=3822261619291980270&...`

商品ID位于URL查询参数 `id` 中。使用 Python 的 `urllib.parse` 解析：

```python
import urllib.parse
parsed = urllib.parse.urlparse(url)
params = urllib.parse.parse_qs(parsed.query)
product_id = params.get('id', [''])[0]
```

### 4. 可选：提取更多商品信息

URL中还包含 `goods_detail` 参数，经过URL编码的JSON，包含商品名称、价格、销量、图片等信息。如需排查case，可一并解析：

```python
import json
goods_detail_raw = params.get('goods_detail', [''])[0]
if goods_detail_raw:
    goods = json.loads(urllib.parse.unquote(goods_detail_raw))
    # goods['title'], goods['min_price'], goods['sales'], goods['img']
```

## 输出格式

纯文本，简洁输出商品ID。如有需要可附带商品名称和价格作为参考：

```
商品ID: 3822261619291980270
商品名称: KWEICHOW MOUTAI/贵州茅台茅台珍品铁盖1996年 JP-96024 53度
价格: ¥9,999,998.00
```

## 注意事项

- 短链接可能过期，如重定向失败提示用户重新复制链接
- 移动端User-Agent是必须的，否则抖音可能返回PC版页面而非商品详情页
- 价格单位为分，需除以100转换为元
