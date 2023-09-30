import logging
import os
import time

import click

from flameshow import __version__
from flameshow.const import MAX_RENDER_DEPTH, MIN_RENDER_DEPTH
from flameshow.pprof_parser import parse_profile
from flameshow.render import FlameGraphApp


logger = logging.getLogger(__name__)


def setup_log(enabled, level, loglocation):
    if enabled:
        logging.basicConfig(
            filename=os.path.expanduser(loglocation),
            filemode="a",
            format=(
                "%(asctime)s %(levelname)5s (%(module)sL%(lineno)d)"
                " %(message)s"
            ),
            level=level,
        )
    else:
        logging.disable(logging.CRITICAL)
    logger.info("------ flameshow ------")


LOG_LEVEL = {
    0: logging.CRITICAL,
    1: logging.WARNING,
    2: logging.INFO,
    3: logging.DEBUG,
}


def run_app(verbose, log_to, profile_f, _debug_exit_after_rednder):
    log_level = LOG_LEVEL[verbose]
    setup_log(log_to is not None, log_level, log_to)

    t0 = time.time()
    profile_data = profile_f.read()

    profile = parse_profile(profile_data, profile_f.name)

    t01 = time.time()
    logger.info("Parse profile, took %.3fs", t01 - t0)
    render_depth = MAX_RENDER_DEPTH - int(profile.total_sample / 100)
    # limit to 3 - 10
    render_depth = max(MIN_RENDER_DEPTH, render_depth)
    render_depth = min(MAX_RENDER_DEPTH, render_depth)

    logger.info(
        "Start to render app, total samples=%d, render_depth=%d",
        profile.total_sample,
        render_depth,
    )

    app = FlameGraphApp(
        profile,
        render_depth,
        _debug_exit_after_rednder,
    )
    app.run()


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(__version__)
    ctx.exit()


@click.command()
@click.option(
    "-v",
    "--verbose",
    count=True,
    default=2,
    help="Add log verbose level, using -v, -vv, -vvv for printing more logs.",
)
@click.option(
    "-l",
    "--log-to",
    type=click.Path(),
    default=None,
    help="Printing logs to a file, for debugging, default is no logs.",
)
@click.option(
    "--version",
    is_flag=True,
    callback=print_version,
    expose_value=False,
    is_eager=True,
)
@click.argument("profile", type=click.File("rb"))
def main(verbose, log_to, profile):
    run_app(verbose, log_to, profile, _debug_exit_after_rednder=False)


if __name__ == "__main__":
    main(True, 3, "lucky.log")
