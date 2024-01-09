# 中文wiki
安装
pip install re-gpt  第一安装

更新 
先删除
pip uninstall re-gpt
再重新安装

pip install re-gpt


同步

from re_gpt import SyncChatGPT

session_token = "__Secure-next-auth.session-token here"
conversation_id = None # conversation ID here


with SyncChatGPT(session_token=session_token) as chatgpt:
    prompt = input("Enter your prompt: ")

    if conversation_id:
        conversation = chatgpt.get_conversation(conversation_id)
    else:
        conversation = chatgpt.create_new_conversation()

    for message in conversation.chat(prompt):
        print(message["content"], flush=True, end="")
