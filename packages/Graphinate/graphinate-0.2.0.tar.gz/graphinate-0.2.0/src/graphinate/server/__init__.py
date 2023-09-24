import webbrowser

import strawberry
from starlette.applications import Starlette
from strawberry.asgi import GraphQL
from strawberry.extensions.tracing import OpenTelemetryExtension

from .starlette import routes

DEFAULT_PORT: int = 8072


def run_graphql(graphql_schema: strawberry.Schema, port: int = DEFAULT_PORT):
    graphql_schema.extensions.append(OpenTelemetryExtension)

    def open_url():
        for app_name in ('voyager', 'graphiql', 'viewer'):
            webbrowser.open(f'http://localhost:{port}/{app_name}')

    graphql_app = GraphQL(graphql_schema)
    app = Starlette(
        routes=routes(),
        on_startup=[open_url])
    app.add_route("/graphql", graphql_app)
    app.add_websocket_route("/graphql", graphql_app)

    from starlette_prometheus import PrometheusMiddleware, metrics
    app.add_middleware(PrometheusMiddleware)
    app.add_route("/metrics", metrics)

    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=port)
