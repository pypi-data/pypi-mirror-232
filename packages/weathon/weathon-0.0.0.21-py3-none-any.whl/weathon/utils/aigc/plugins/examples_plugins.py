import json
from semantic_kernel import SKContext
from semantic_kernel.skill_definition import sk_function, sk_function_context_parameter


class Examples:
    """
    example:
        from semantic_kernel.skill_definition import sk_function,sk_function_context_parameter
        from langchain.embeddings.huggingface import HuggingFaceEmbeddings
        from langchain.vectorstores import FAISS

        documents = [Document(page_content="花卉配饰", metadata={"input":"花卉配饰","output":['浪漫温馨','华丽奢华', '时尚潮流']}), 
                    Document(page_content="搓澡巾",metadata={"input":"搓澡巾","output":['清洁彻底','耐用持久']})]
                    
        embeddings = HuggingFaceEmbeddings(model_name="moka-ai/m3e-base",model_kwargs={'device': 'cpu'},encode_kwargs={'normalize_embeddings':True})
        faiss = FAISS.from_documents(documents=documents, embedding=embeddings)
        plugins_directory = "./weathon/utils/aigc/semantic/plugins"

        # Import the OrchestratorPlugin from the plugins directory.
        examples_plugin = kernel.import_skill(Examples(),skill_name="examples_plugin")

        # 创建一个新的上下文，并设置输入、历史和选项变量。
        context = sk.ContextVariables()
        context["embedding"] = faiss
        context["k"] = 1
        context["text"] = "鲜花" 


        # Run the GetIntent function with the context.
        result = await kernel.run_async(
            examples_plugin["relevance_examples"],
            input_vars=context
        )

    """

    @sk_function(name="relevance_examples",
                 description="Example of querying for k most similar texts in a vector index library")
    @sk_function_context_parameter(name="text", description="query text")
    @sk_function_context_parameter(name="embedding", description="vector index library")
    @sk_function_context_parameter(name="k", description="Query the most similar number from the vector index library")
    def relevance_examples(self, context: SKContext) -> str:
        embedding = context["embedding"]
        query = context["text"]
        k = int(context["k"])

        examples = embedding.similarity_search(query, k)
        datas = []
        for example in examples:
            datas.append(f"""INPUT: {example.metadata["input"]}\nOUTPUT: {example.metadata["output"]}""")
        return "\n".join(datas)

    @sk_function(name="max_marginal_relevance_search",
                 description="Query k examples of the most similar text in the vector index library, with as few examples as possible between them")
    @sk_function_context_parameter(name="text", description="query text")
    @sk_function_context_parameter(name="embedding", description="vector index library")
    @sk_function_context_parameter(name="k", description="Query the most similar number from the vector index library")
    def max_marginal_relevance_search(self, context: SKContext) -> str:
        embedding = context["embedding"]
        query = context["text"]
        k = int(context["k"])

        examples = embedding.max_marginal_relevance_search(query, k)
        datas = []
        for example in examples:
            datas.append(f"""INPUT: {example.metadata["input"]}\nOUTPUT: {example.metadata["output"]}""")
        return "\n".join(datas)
