"""
Define endpoints routes in python function fashion
example:

my_router = ModuleRouter("/cats", tag="Cats", description="Cats Resource description")

@my_router.get('/')
def index(request: Request):
    return {'detail': 'Welcome to Cats Resource'}
"""

from dataclasses import dataclass
from typing import List

from ellar.common import (
    DataclassSerializer,
    ModuleRouter,
    Provide,
    Req,
    render,
    render_template,
)
from ellar.openapi import ApiTags

from .services import CarRepository

router = ModuleRouter("/car-as-router")
tag = ApiTags(
    name="Router",
    description="Example of car Resource from a <strong>ModuleRouter</strong>",
)
tag(router.get_control_type())


@dataclass
class CarObject(DataclassSerializer):
    name: str
    model: str


@router.get(response={200: List[CarObject]})
async def get_cars(repo: CarRepository = Provide()):
    return repo.get_all()


@router.http_route("/html", methods=["get", "post"])
@render("index.html")
async def get_car_html(repo: CarRepository = Provide()):
    return repo.get_all()


@router.get("/html/outside")
async def get_car_html_with_render(repo: CarRepository = Provide(), request=Req()):
    return render_template("car/list.html", request=request, model=repo.get_all())
