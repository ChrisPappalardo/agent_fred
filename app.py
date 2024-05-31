import gradio as gr
import pandas as pd

from haystack import Pipeline
from haystack.document_stores.in_memory import InMemoryDocumentStore

from agent_fred.config import config
from agent_fred.core import fred_api_to_documents, load_prompt
from agent_fred.pipelines import fred_chat_pipeline


class Context:
    agent_prompt_template: str = load_prompt("src/agent_fred/prompts/agent.txt")
    chat_prompt_template: str = load_prompt("src/agent_fred/prompts/chat.txt")
    data: pd.DataFrame = pd.DataFrame(columns=["date", "value"])
    document_store: InMemoryDocumentStore = InMemoryDocumentStore()
    pipeline: Pipeline = Pipeline()
    series: str = ""


# create global context
ctx = Context()

# create pipeline, document store, and document embedder
ctx.pipeline, ctx.document_store = fred_chat_pipeline(
    agent_prompt_template=ctx.agent_prompt_template,
    chat_prompt_template=ctx.chat_prompt_template,
    api_key=config.fred_api_key,
    agent_llm_kwargs={
        "model": config.llm,
        "generation_kwargs": {"temperature": float(config.temperature)},
    },
    chat_llm_kwargs={
        "model": config.llm,
        "generation_kwargs": {"temperature": float(config.temperature)},
    },
)


# create fred agent
def fred(question, history, ctx=ctx) -> tuple[pd.DataFrame, pd.DataFrame]:
    response = ctx.pipeline.run(
        {
            "chat_prompt_builder": {
                "template_variables": {"question": question, "history": history},
            },
            "prompt_builder": {"question": question},
            "router": {"question": question},
        }
    )
    if "cleaner" in response.keys():
        doc = response["cleaner"]["documents"][0]
        # ctx.document_store = InMemoryDocumentStore()
        documents = fred_api_to_documents(doc.json, doc.meta)
        ctx.document_store.write_documents(documents)
        # post-process for gradio components
        ctx.series = " ".join(doc.meta["fred_url_kwargs"].values())
        ctx.data = pd.DataFrame(doc.json)
        ctx.data["date"] = pd.to_datetime(ctx.data["date"])
        ctx.data["value"] = pd.to_numeric(ctx.data["value"])
        history.append((question, "Dashboard updated!"))
        return ctx.data, ctx.data, ctx.series, "", history
    else:
        history.append((question, response["chat_llm"]["replies"][0].content))
        return ctx.data, ctx.data, ctx.series, "", history


def fred_clear(ctx=ctx) -> tuple[str, list]:
    """clear ctx and history"""
    ctx.document_store = InMemoryDocumentStore()
    ctx.series = ""
    ctx.data = pd.DataFrame(columns=["date", "value"])
    return ctx.data, ctx.data, ctx.series, "", []


# create gradio app
with gr.Blocks(title="Agent FRED") as demo:
    with gr.Row():
        with gr.Column():
            chatbot = gr.Chatbot(
                label="Agent FRED",
                height=650,
            )
            question = gr.Textbox(
                label="Question",
                placeholder="What was GDP from 2021-01-01 through 2023-12-31?",
            )
            clear = gr.ClearButton([chatbot, question])
        with gr.Column():
            series = gr.Textbox(
                label="Series Info",
                interactive=False,
            )
            lineplot = gr.LinePlot(
                x="date",
                y="value",
                height=300,
                width=600,
                interactive=False,
                show_label=False,
            )
            dataframe = gr.Dataframe(
                height=300,
                interactive=False,
                show_label=False,
            )
    question.submit(
        fn=fred,
        inputs=[question, chatbot],
        outputs=[lineplot, dataframe, series, question, chatbot],
    )
    clear.click(
        fn=fred_clear,
        inputs=None,
        outputs=[lineplot, dataframe, series, question, chatbot],
    )

demo.launch()
