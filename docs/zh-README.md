<div align="center">
  <a href="https://github.com/Zai-Kun/reverse-engineered-chatgpt"></a>

<h1 align="center">Reverse Engineered <a href="https://openai.com/blog/chatgpt">ChatGPT</a> API</h1>

  <p align="center">
    无需API密钥在Python代码中使用OpenAI ChatGPT

[![Stargazers][stars-badge]][stars-url]
[![Forks][forks-badge]][forks-url]
[![Discussions][discussions-badge]][discussions-url]
[![Issues][issues-badge]][issues-url]
[![MIT许可证][license-badge]][license-url]

  [English](../README.md) | 简体中文 
  </p>
    <p align="center">
    <a href="https://github.com/Zai-Kun/reverse-engineered-chatgpt"></a>
    <a href="https://github.com/Zai-Kun/reverse-engineered-chatgpt/issues">报告Bug</a>
    |
    <a href="https://github.com/Zai-Kun/reverse-engineered-chatgpt/discussions">请求新功能</a>
  </p>
</div>

<!-- 目录 -->
<details>
  <summary>目录</summary>
  <ol>
    <li>
      <a href="#关于本项目">关于本项目</a>
      <ul>
        <li><a href="#灵感来源">灵感来源</a></li>
        <li><a href="#工作原理">工作原理</a></li>
        <li><a href="#构建使用">构建使用</a></li>
      </ul>
    </li>
    <li>
      <a href="#开始使用">开始使用</a>
      <ul>
        <li><a href="#前提条件">前提条件</a></li>
        <li><a href="#安装">安装</a></li>
        <li><a href="#获取会话令牌">获取会话令牌</a></li>
      </ul>
    </li>
    <li><a href="#使用方法">使用方法</a>
        <ul>
        <li><a href="#基本示例">基本示例</a></li>
        </ul>
    </li>
    <li><a href="#路线图">路线图</a></li>
    <li><a href="#贡献">贡献</a></li>
    <li><a href="#许可证">许可证</a></li>
    <li><a href="#联系方式">联系方式</a></li>
    <li><a href="#致谢">致谢</a></li>
  </ol>
</details>

## 关于本项目

该项目可用于将OpenAI的ChatGPT服务集成到您的Python代码中。您可以使用这个项目直接从python中提示ChatGPT响应，而无需使用官方API密钥。

如果你想不通过[ChatGPT Plus](https://openai.com/blog/chatgpt-plus)账户使用ChatGPT API，这将非常有用。

### 灵感来源

ChatGPT有一个官方API，可以用于将您的Python代码与之接口，但它需要使用API密钥。这个API密钥只能通过拥有[ChatGPT Plus](https://openai.com/blog/chatgpt-plus)账户获得，这需要20美元/月（截至2023年5月11日）。但是，您可以通过使用[ChatGPT网页界面](https://chat.openai.com/)免费使用ChatGPT。本项目旨在将您的代码与ChatGPT网页版本接口，这样您就可以在不使用API密钥的情况下在Python代码中使用ChatGPT。

### 工作原理

[ChatGPT](https://chat.openai.com/)网页界面的请求已经被反向工程，并直接集成到Python请求中。因此，使用此脚本进行的任何请求都模拟为用户直接在网站上进行的请求。因此，它是免费的，不需要API密钥。

### 构建使用

- [![Python][python-badge]][python-url]

## 开始使用

### 前提条件

- Python >= 3.9

### 安装

```sh
pip install re-gpt
```

## 使用方法

### 简单示例

``` python
from re_gpt import SyncChatGPT

session_token = "__Secure-next-auth.session-token here"
conversation_id = None # 这里填写对话ID


with SyncChatGPT(session_token=session_token) as chatgpt:
    prompt = input("输入你的提示：")

    if conversation_id:
        conversation = chatgpt.get_conversation(conversation_id)
    else:
        conversation = chatgpt.create_new_conversation()

    for message in conversation.chat(prompt):
        print(message["content"], flush=True, end="")

```

### 简单异步示例

``` python
import asyncio
import sys

from re_gpt import AsyncChatGPT

session_token = "__Secure-next-auth.session-token here"
conversation_id = None # 这里填写对话ID

if sys.version_info >= (3, 8) and sys.platform.lower().startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def main():
    async with AsyncChatGPT(session_token=session_token) as chatgpt:
        prompt = input("输入你的提示：")

        if conversation_id:
            conversation = chatgpt.get_conversation(conversation_id)
        else:
            conversation = chatgpt.create_new_conversation()

        async for message in conversation.chat(prompt):
            print(message["content"], flush=True, end="")


if __name__ == "__main__":
    asyncio.run(main())
```

## 更多示例

要查看更复杂的示例，请查看存储库中的[examples](/examples)文件夹。

### 获取会话令牌

1. 访问<https://chat.openai.com/chat>并登录或注册。
2. 打开浏览器的开发者工具。
3. 转到`Application`标签页并打开`Cookies`部分。
4. 复制`__Secure-next-auth.session-token`的值并保存。

## 待办事项

- [x] 添加更多示例
- [ ] 添加更好的错误处理
- [x] 实现检索所有ChatGPT聊天的功能
- [ ] 改进文档

## 贡献

贡献是开源社区成为学习、启发和创造的绝佳场所的原因之一。您所做的任何贡献都**非常感激**。

如果您有一个好的建议，可以使这个项目变得更好，请fork本仓库并创建一个拉取请求。
不要忘了给项目加星！再次感谢！

1. Fork项目
2. 创建您的功能分支（`git checkout -b feature/AmazingFeature`）
3. 提交您的更改（`git commit -m 'Add some AmazingFeature'`）
4. 推送到分支（`git push origin feature/AmazingFeature`）
5. 提交拉取请求

## 许可证

根据Apache许可证2.0分发。更多信息请参见[`LICENSE`](https://github.com/Zai-Kun/reverse-engineered-chatgpt/blob/main/LICENSE)。

## 联系/报告Bug

Zai-Kun - [Discord Server](https://discord.gg/ymcqxudVJG)

仓库链接: <https://github.com/Zai-Kun/reverse-engineered-chatgpt>

## 致谢

- [sudoAlphaX (for writing this readme)](https://github.com/sudoAlphaX)

- [yifeikong (curl-cffi module)](https://github.com/yifeikong/curl_cffi)

- [acheong08 (implementation to obtain arkose_token)](https://github.com/acheong08/funcaptcha)

- [pyca (cryptography module)](https://github.com/pyca/cryptography/)

- [Legrandin (pycryptodome module)](https://github.com/Legrandin/pycryptodome/)

- [othneildrew (README Template)](https://github.com/othneildrew)

<!-- MARKDOWN LINKS & IMAGES -->

[forks-badge]: https://img.shields.io/github/forks/Zai-Kun/reverse-engineered-chatgpt
[forks-url]: https://github.com/Zai-Kun/reverse-engineered-chatgpt/network/members
[stars-badge]: https://img.shields.io/github/stars/Zai-Kun/reverse-engineered-chatgpt
[stars-url]: https://github.com/Zai-Kun/reverse-engineered-chatgpt/stargazers
[issues-badge]: https://img.shields.io/github/issues/Zai-Kun/reverse-engineered-chatgpt
[issues-url]: https://github.com/Zai-Kun/reverse-engineered-chatgpt/issues
[discussions-badge]: https://img.shields.io/github/discussions/Zai-Kun/reverse-engineered-chatgpt
[discussions-url]: https://github.com/Zai-Kun/reverse-engineered-chatgpt/discussions
[python-badge]: https://img.shields.io/badge/Python-blue?logo=python&logoColor=yellow
[python-url]: https://www.python.org/
[license-badge]: https://img.shields.io/github/license/Zai-Kun/reverse-engineered-chatgpt
[license-url]: https://github.com/Zai-Kun/reverse-engineered-chatgpt/blob/main/LICENSE
