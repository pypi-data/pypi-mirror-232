import logging
import json
import click

from quart import Quart, request, render_template, redirect

from .data_provider import DataProvider
from .types import Message
from .server import BlueprintForActors
from .server.verify_actor import ActorVerifier

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.command()
@click.option("--only_generate_config", default=False, is_flag=True)
@click.option("--port", default=2909, help="port to run on")
@click.option(
    "--domain", default="localhost:2909", help="domain the service is running on"
)
def verify_actor(only_generate_config, port, domain):
    dp = DataProvider.generate_and_load(only_generate_config)
    app = Quart(__name__)

    actor_list = dp.possible_actors + [dp.one_actor]
    app.register_blueprint(BlueprintForActors(actor_list).blueprint)

    @app.get("/")
    async def index():
        return await render_template("index.html.j2")

    @app.post("/verify")
    async def verify():
        form_data = await request.form
        actor_uri = form_data.get("actor_uri")
        if not actor_uri:
            return redirect("/")

        message = Message()
        message.add(f"Got Actor Uri {actor_uri}")

        verifier = ActorVerifier(
            actor_list=actor_list, remote_uri=actor_uri, message=message, domain=domain
        )

        result = await verifier.verify()

        if "json" in request.headers.get("accept"):
            return {
                "result": result,
                "messages": json.dumps(message.response, indent=2),
            }

        return await render_template(
            "verify_actor_result.html.j2",
            messages=json.dumps(message.response, indent=2),
            result=result,
            actor_uri=actor_uri,
        )

    app.run(port=port, host="0.0.0.0", use_reloader=True)


if __name__ == "__main__":
    verify_actor()
