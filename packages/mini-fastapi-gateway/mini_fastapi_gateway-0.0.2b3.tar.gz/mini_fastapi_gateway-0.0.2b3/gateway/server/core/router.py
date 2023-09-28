from typing import Any

import cachetools
from fastapi import FastAPI, APIRouter, Depends
from sqlalchemy.orm import selectinload

from gateway.server.core.database import SessionLocal
from gateway.server.core.database.models import Scope
from gateway.server.core.database.crud import CRUD
from gateway.server.core.decorators import to_microservice
from gateway.server.utils.router import make_route, get_params_from_path, cache, import_from_module_string


class ApiGateway(APIRouter):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_routes_from_db()

    def add_routes_from_db(self):
        scope_crud = CRUD(Scope)
        with SessionLocal() as db:
            scopes = scope_crud.get_multi(db, options=[selectinload(Scope.microservice)])
            for scope in scopes:
                if scope.is_active:
                    params = get_params_from_path(scope.path)
                    func_name = scope.name.replace(' ', '_').lower()
                    decorated_func = to_microservice(make_route(func_name, scope, params), scope)
                    response_model = Any
                    dependencies = []
                    if scope.response_model:
                        response_model = import_from_module_string(scope.response_model) or Any
                    if scope.dependencies:
                        for dependency in scope.dependencies:
                            dep = import_from_module_string(dependency)
                            if dep:
                                dependencies.append(Depends(dep))

                    self.add_api_route(
                        scope.path,
                        decorated_func,
                        response_model=response_model,
                        dependencies=dependencies,
                        methods=[scope.method],
                        tags=[f"Microservice: {scope.microservice.name if scope.microservice else 'Without microservice'}"],
                    )


class GatewayRouter(FastAPI):
    _route_len: int = 0

    async def __call__(self, scope, receive, send):
        if not self._route_len or cache.get("need_reload", False):
            api_router = ApiGateway()
            if self._route_len:
                for route in self.routes[-self._route_len:]:
                    self.routes.remove(route)
            self.include_router(api_router)
            self._route_len = len(api_router.routes)
            cache["need_reload"] = False
        await super().__call__(scope, receive, send)

    @cachetools.cached(cache, key=lambda *args: "openapi_cache")
    def openapi(self):
        self.openapi_schema = None
        return super().openapi()
