from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
import os

# os.environ["OPENAI_API_KEY"] = "sk-...Qk0A"


def print_hi(name):
    # 在下面的代码行中使用断点来调试脚本。
    print(f'Hi, {name}')  # 按 ⌘F8 切换断点。


# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    print_hi('PyCharm')


    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()
    response = query_engine.query("Who is the author?")
    print(response)



# 访问 https://www.jetbrains.com/help/pycharm/ 获取 PyCharm 帮助
