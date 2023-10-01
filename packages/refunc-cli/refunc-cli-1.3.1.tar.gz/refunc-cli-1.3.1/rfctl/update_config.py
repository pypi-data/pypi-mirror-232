from rfctl.awslocal import lambda_command
import click


@click.command()
@click.pass_context
def update_config_command(ctx: click.Context):
    funcdef = ctx.obj["funcdef"]
    click.echo("Updating config for function %s/%s" % (funcdef["metadata"]["namespace"], funcdef["metadata"]["name"]))
    environment = []
    environment_spec:dict = funcdef["spec"].get("environment",{})
    for env,value in environment_spec.items():
        environment.append("{}={}".format(env,value))
    lambda_args = ["update-function-configuration",
                   "--function-name", funcdef["metadata"]["name"],
                   "--handler", funcdef["spec"]["handler"],
                   "--runtime", funcdef["spec"]["runtime"],
                   "--timeout", funcdef["spec"]["timeout"]]
    if environment:
        lambda_args.extend(["--environment", '''Variables={%s}''' % ",".join(environment)])
    lambda_command(ctx.obj["endpoint"], lambda_args)
    concurrency = funcdef["spec"].get("concurrency",1)
    lambda_args = ["put-function-concurrency",
                   "--function-name", funcdef["metadata"]["name"],
                   "--reserved-concurrent-executions", concurrency]
    lambda_command(ctx.obj["endpoint"], lambda_args)
