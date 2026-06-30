# douyin-product-link-parser

> **作者 / 投稿：常斌**　收录自团队内部分享，已征得原作者同意公开收录，方法与代码版权归原作者。

把抖音商品分享链接 / 口令自动解析成商品 ID 及详情（名称、价格、销量等）。装上后，给 Agent 发一条带抖音商品链接的消息，**无需任何提示词**即可自动提取，适合商品 case 排查、商品信息快速定位。

## 一键安装

把下面这句话发给你的 AI Agent（Claude Code / Cursor 等）：

```
帮我安装 douyin-product-link-parser skill：https://github.com/caojunjie0706-eng/agent-skills/tree/main/skills/douyin-product-link-parser
```

## 怎么用

装好后，直接把抖音 App「分享 → 复制链接」得到的链接或口令发给 Agent：

```
3.53 ... 【抖音商城】https://v.douyin.com/XXXXXX/ 某某商品 ... 长按复制此条消息，打开抖音搜索
```

Agent 会自动返回：

```
商品ID: 3822261619291980270
商品名称: ……
价格: ¥……
```

## 原理（简述）

1. 从消息中识别 `v.douyin.com` 短链
2. curl 跟随重定向，拿到 `haohuo.jinritemai.com` 真实商品页 URL（需移动端 User-Agent）
3. 用 `urllib.parse` 从 URL 的 `id` 参数取商品 ID，可选解析 `goods_detail` 取更多信息

## 注意

- 短链接可能过期，重定向失败时请重新复制链接
- 价格单位为分，需除以 100
- 仅支持抖音商品链接，其他平台不适用
