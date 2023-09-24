from pydantic.dataclasses import dataclass
@dataclass
class API:

    mt_openai_key:str = "1700006389466390612"
    mt_openai_endpoint:str = "https://aigc.sankuai.com/v1/openai/native"
    custom_openai_key:str = "sk-mN6VtvtOugQk8MV22eBdA69aE49345EeA3EfFa0f4e3d15F6"
    custom_openai_endpoint:str = "https://chatapi.omycloud.site/"
    serpapi_api_key:str = "2448ba6361437353026c6cc15fe4a30d2328fd6ae6008dfdfb0b5d1bc32013d8"
    google_ces_id:str = "a063f4f2d2c9a4a2b"

    model_name = "gpt-3.5-turbo-16k-0613"
    

