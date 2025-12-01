from langchain_gigachat.chat_models import GigaChat
from pydantic import create_model
from rich import print

from enums import GigaChatAPIScope, GigaChatModel, TimezoneKey
from models import GigaChatSettings
from tools import GigaChatTokenReleaser


token_releaser = GigaChatTokenReleaser(TimezoneKey.ETC_GMT_3)

prompt = "Составь меню русской кухни"
fields = ["breakfast", "dinner", "supper"]
structured_output = None
default_settings = GigaChatSettings().model_dump()

Template = create_model(
    "Template",
    __doc__=prompt,
    **dict.fromkeys(fields, str)
)

while not isinstance(structured_output, Template):
    gigachat = GigaChat(
        access_token=token_releaser(),
        scope=GigaChatAPIScope.CORP,
        model=GigaChatModel.GIGACHAT2_PRO,
        verify_ssl_certs=False,
        **default_settings
    )

    # GigaChat re-init, timeit -n 100_000
    # 56.1 μs ± 470 ns per loop (mean ± std. dev. of 7 runs, 100,000 loops each)

    # token_releaser.n_tokens_released
    # 1

    gigachat = gigachat.with_structured_output(Template)
    structured_output = gigachat.invoke(prompt)

print(structured_output.model_dump())

# Пример ответа:
# {
#     'breakfast': 'Омлет с зеленью, блины с вареньем, чай с лимоном',
#     'dinner': 'Щи из свежей капусты, пельмени с сметаной, компот из сухофруктов',
#     'supper': 'Картофельное пюре, котлеты с грибным соусом, кефир'
# }
