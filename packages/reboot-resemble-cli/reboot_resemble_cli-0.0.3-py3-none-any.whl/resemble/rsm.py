import asyncio
import colorama
import concurrent
import git
import glob
import os
import psutil
import pyprctl
import random
import resemble.rc as rc
import subprocess
import sys
import threading
from contextlib import asynccontextmanager, contextmanager
from resemble.monkeys import monkeys, no_chaos_monkeys
from resemble.rc import fail, info, warn
from typing import AsyncIterator, Iterable, Optional
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer


@asynccontextmanager
async def watch(
    application: str, paths: list[str]
) -> AsyncIterator[asyncio.Task[FileSystemEvent]]:
    """Helper for watching the provided paths on file system. Implemented
    as a context manager to ensure proper cleanup of the watches."""
    loop = asyncio.get_running_loop()

    class EventHandler(FileSystemEventHandler):

        def __init__(self, events: asyncio.Queue[FileSystemEvent]):
            self._events = events

        def on_modified(self, event):
            loop.call_soon_threadsafe(lambda: self._events.put_nowait(event))

    events: asyncio.Queue[FileSystemEvent] = asyncio.Queue()

    handler = EventHandler(events)

    observer: Optional[Observer] = None

    # It's possible that the application or other watch paths may get
    # deleted and then (re)created by a build system so rather than
    # fail if we can't find them we'll retry but print out a warning
    # after so many retries.
    #
    # We've picked 10 based on how long we've noticed some builds
    # taking.
    def warn_every_n_retries(retries: int, message: str):
        if retries != 0 and retries % 10 == 0:
            warn(message)

    retries = 0
    while True:
        # Construct a new observer everytime to avoid re-adding the
        # same path and raising an error.
        observer = Observer()

        try:
            if not os.path.isfile(application):
                warn_every_n_retries(
                    retries,
                    f"Missing application at '{application}' "
                    "(is it being rebuilt?)",
                )
                raise RuntimeError('Retry')

            if not os.access(application, os.X_OK):
                fail(f"Expecting executable application at '{application}'")

            observer.schedule(handler, path=application, recursive=False)

            # We want to (re)determine the paths to watch _every_ time
            # to find any new subdirectories added by the developer
            # which they surely expect we will properly watch as well.
            for unglobed_path in paths:
                has_globbed_paths = False
                for path in glob.iglob(unglobed_path, recursive=True):
                    has_globbed_paths = True

                    if not os.access(path, os.R_OK):
                        fail('Expecting path passed to --watch to be readable')

                    observer.schedule(handler, path=path, recursive=False)

                if not has_globbed_paths:
                    warn(f"'{unglobed_path}' did not match any files")

            observer.start()
            break
        except:
            # NOTE: we capture all exceptions here because
            # 'observer.schedule()' may raise if a file that we had
            # globbed gets removed before calling it (e.g., by a build
            # system) and we just want to retry since the build system
            # should be completing and not removing files out from
            # underneath us all the time.
            retries += 1
            await asyncio.sleep(0.5)
            continue

    # Ok, should have a valid observer now!
    assert observer is not None

    events_get = asyncio.create_task(events.get())

    try:
        yield events_get
    finally:
        events_get.cancel()
        observer.stop()
        observer.join()


async def terminate(process: subprocess.Popen | asyncio.subprocess.Process):
    """Helper for terminating a process and all of its descendants.

    This is non-trivial to do as processes may have double forked and
    are no longer part of the process tree, but there are a handful of
    different mechanisms that we document extensively within the
    implementation for how we try and kill all possible descedants of
    a process.
    """
    while True:
        # Try and get all the processes descendants first, before we
        # try and terminate it and lose the process tree.
        descendants = set()

        # (1) Add processes with same PGID as 'process'.
        #
        # This gets all processes that 'process' created that did not
        # create a new process group, even if they double forked and
        # are no longer direct descendants of 'process'.
        try:
            pgid = os.getpgid(process.pid)
        except ProcessLookupError:
            # Process might have already exited, e.g., because it
            # crashed, or we already killed it.
            #
            # Use the PID as PGID as they should be the same since
            # when the process was created it created a new process
            # group whose ID is the same as the PID.
            pgid = process.pid

        for p in psutil.process_iter():
            try:
                if os.getpgid(p.pid) == pgid:
                    descendants.add(p)
            except ProcessLookupError:
                # Process might have already exited, e.g., because it
                # crashed, or we already killed it.
                pass

        # (2) Add descendants of 'process'.
        #
        # This gets processes that might have changed their process
        # group but are still descendants of 'process'.
        try:
            for p in psutil.Process(process.pid).children(recursive=True):
                descendants.add(p)
        except psutil.NoSuchProcess:
            # Process 'process' might have already exited, e.g.,
            # because it crashed, or we already killed it.
            pass

        # Send SIGTERM to the process _but not_ the descendants to let
        # it try and clean up after itself first.
        #
        # Give it some time, but not too much time, before we try and
        # terminate everything.
        try:
            process.terminate()
            await asyncio.sleep(0.1)
        except ProcessLookupError:
            # Process might have already exited, e.g., because it
            # crashed, or we already killed it.
            pass

        # (3) Add _our_ descendants that have a different PGID.
        #
        # On Linux when we enable the subreaper so any processes that
        # both changed their process group and tried to double fork so
        # that they were no longer a descendant of 'process' should
        # now be a descendant of us however they will be in a
        # different process group than us.
        #
        # Note that while using the subreaper on Linux implies that
        # (3) subsumes (1), because the subreaper is best effort (as
        # in, we don't rely on having the requisite capabilities to
        # use the subreaper), we include them both.
        pgid = os.getpgid(os.getpid())

        for p in psutil.Process(os.getpid()).children(recursive=True):
            try:
                if os.getpgid(p.pid) != pgid:
                    descendants.add(p)
            except ProcessLookupError:
                # Process 'p' might have already exited, e.g., because
                # it crashed or we already killed it (but it actually
                # exited after it was determined one of our children).
                pass

        # Don't try and terminate ourselves! This can happen when we
        # try and terminate any processes that we were not able to put
        # into a separate process group.
        descendants = set(
            [
                descendant for descendant in descendants
                if descendant.pid != os.getpid()
            ]
        )

        if len(descendants) == 0:
            break

        for descendant in descendants:
            try:
                descendant.terminate()
            except psutil.NoSuchProcess:
                # Process might have already exited, e.g., because it
                # crashed, or we already killed it.
                pass

        _, alive = psutil.wait_procs(descendants, timeout=1)

        for descendant in alive:
            try:
                descendant.kill()
            except psutil.NoSuchProcess:
                # Process might have already exited, e.g., because
                # it crashed, or we already killed it.
                pass

        # Can wait forever here because a process can't ignore kill.
        psutil.wait_procs(alive)


@asynccontextmanager
async def run(application, *, launcher: Optional[str]):
    """Helper for running the application with an optional launcher."""
    process = await asyncio.create_subprocess_exec(
        application,
        # NOTE: starting a new sesssion will also put the
        # process into its own new process group. Each time we
        # restart the application we need to kill all
        # processes which are not in our process group as that
        # implies that they are processes that were created by
        # the application or one of its descendants.
        start_new_session=True,
    ) if launcher is None else await asyncio.create_subprocess_exec(
        launcher,
        application,
        # NOTE: see comment above on sessions.
        start_new_session=True,
    )
    try:
        yield process
    finally:
        await terminate(process)


default_local_envoy_port: int = 9991


def dot_rsm_directory() -> str:
    """Helper for determining the '.rsm' directory."""
    try:
        repo = git.Repo(search_parent_directories=True)
    except git.exc.InvalidGitRepositoryError:
        return os.path.join(os.getcwd(), '.rsm/dev')
    else:
        return os.path.join(repo.working_dir, '.rsm/dev')


async def run_background_command(background_command: str):
    info(f"Running background command '{background_command}'")
    process = await asyncio.create_subprocess_shell(background_command)
    try:
        await process.wait()
    except asyncio.CancelledError:
        await terminate(process)
    else:
        if process.returncode != 0:
            fail(
                f"Failed to run background command '{background_command}', "
                f"exited with {process.returncode}"
            )
        else:
            warn(
                f"Background command '{background_command}' exited without errors"
            )


@contextmanager
def chdir(directory):
    """Context manager that changes into a directory and then changes back
    into the original directory before control is returned."""
    cwd = os.getcwd()
    try:
        os.chdir(directory)
        yield
    finally:
        os.chdir(cwd)


async def dev(args, *, parser: rc.ArgumentParser):
    """Implementation of the 'dev' subcommand."""
    # Determine the working directory and move into it.
    working_directory = args.working_directory

    if '--working-directory' in parser.expanded_flags:
        assert parser.dot_rc is not None
        working_directory = os.path.relpath(
            working_directory,
            start=os.path.dirname(parser.dot_rc),
        )

    working_directory = os.path.abspath(working_directory)

    info(f"Using working directory {working_directory}\n")

    with chdir(working_directory):
        application = os.path.abspath(args.application)

        # If on Linux try and become a child subreaper so that we can
        # properly clean up all processes descendant from us!
        if sys.platform == 'linux':
            try:
                pyprctl.set_child_subreaper(True)
            except:
                warn(
                    "Failed to become child subreaper, we'll do our "
                    "best to ensure all created processes are terminated"
                )
                pass

        # Run any background commands.
        background_command_tasks: list[asyncio.Task] = []

        for background_command in args.background_command:
            background_command_tasks.append(
                asyncio.create_task(
                    run_background_command(background_command)
                )
            )

        # Set all the environment variables that
        # 'resemble.aio.Application' will be looking for.

        os.environ['RSM_DEV'] = 'true'

        if args.name is not None:
            os.environ['RSM_DEV_NAME'] = args.name
            os.environ['RSM_DOT_RSM_DIRECTORY'] = dot_rsm_directory()

        os.environ['RSM_DEV_LOCAL_ENVOY'
                  ] = 'true' if args.local_envoy else 'false'

        os.environ['RSM_DEV_LOCAL_ENVOY_PORT'] = str(
            args.local_envoy_port or default_local_envoy_port
        )

        if not args.chaos:
            warn(
                '\n' + random.choice(no_chaos_monkeys) + '\n'
                'You Have Disabled Chaos Monkey! (see --chaos)\n'
                '\n'
                'Only You (And Chaos Monkey) Can Prevent Bugs!'
                '\n'
            )

        try:
            while True:
                if args.name is None:
                    warn(
                        '\n'
                        'Starting an ANONYMOUS application; to reuse state '
                        'across application restarts use --name'
                        '\n'
                    )

                async with watch(
                    application, args.watch or []
                ) as file_system_event_task:
                    # TODO(benh): catch just failure to create the subprocess
                    # so that we can either try again or just listen for a
                    # modified event and then try again.
                    async with run(
                        application,
                        # TODO(benh): use executable in env var
                        # $PYTHON if it exists.
                        launcher='python' if args.python is not None else None,
                    ) as process:
                        process_wait_task = asyncio.create_task(process.wait())

                        if args.chaos:
                            chaos_task = asyncio.create_task(
                                asyncio.sleep(random.randint(30, 60))
                            )

                        completed, pending = await asyncio.wait(
                            [file_system_event_task, process_wait_task] +
                            ([chaos_task] if args.chaos else []),
                            return_when=asyncio.FIRST_COMPLETED,
                        )

                        # Cancel chaos task regardless of what task
                        # completed first as we won't ever wait on it.
                        if args.chaos:
                            chaos_task.cancel()

                        task = completed.pop()

                        if task is process_wait_task:
                            warn(
                                '\n'
                                'Application exited unexpectedly '
                                '... waiting for modification'
                                '\n'
                            )
                            # NOTE: we'll wait for a file system event
                            # below to signal a modification!
                        elif args.chaos and task is chaos_task:
                            warn(
                                '\n'
                                'Chaos Monkey Is Restarting Your Application'
                                '\n' + random.choice(monkeys) + '\n'
                                '... disable via --no-chaos if you must'
                                '\n'
                                '\n'
                            )
                            continue

                        file_system_event: FileSystemEvent = await file_system_event_task

                        info(
                            '\n'
                            'Application modified; restarting ... '
                            '\n'
                        )
        except:
            for background_command_task in background_command_tasks:
                background_command_task.cancel()

            await asyncio.wait(
                background_command_tasks,
                return_when=asyncio.ALL_COMPLETED,
            )

            raise


async def rsm():
    colorama.init()

    parser = rc.ArgumentParser(
        program='rsm',
        filename='.rsmrc',
        subcommands=['dev'],
    )

    parser.subcommand('dev').add_argument(
        '--working-directory',
        type=str,
        help="directory in which to execute",
        required=True,
    )

    parser.subcommand('dev').add_argument(
        '--name',
        type=str,
        help="name of instance; state will be persisted using this name in "
        f"'{dot_rsm_directory()}'",
    )

    parser.subcommand('dev').add_argument(
        '--background-command',
        type=str,
        repeatable=True,
        help=
        'command(s) to execute in the background (multiple instances of this '
        'flag are supported)',
    )

    parser.subcommand('dev').add_argument(
        '--local-envoy',
        type=bool,
        default=True,
        help='whether or not to bring up a local Envoy'
    )

    parser.subcommand('dev').add_argument(
        '--local-envoy-port',
        type=int,
        help=f'port for local Envoy; defaults to {default_local_envoy_port}',
    )

    parser.subcommand('dev').add_argument(
        '--python',
        type=bool,
        default=False,
        help="whether or not to launch the application by "
        "passing it as an argument to 'python'",
    )

    parser.subcommand('dev').add_argument(
        '--watch',
        type=str,
        repeatable=True,
        help=
        'path to watch; multiple instances are allowed; globbing is supported',
    )

    parser.subcommand('dev').add_argument(
        '--chaos',
        type=bool,
        default=True,
        help='whether or not to randomly induce failures',
    )

    parser.subcommand('dev').add_argument(
        'application',
        type=str,  # TODO: consider argparse.FileType('e')
        help='path to application to execute',
    )

    args = parser.parse_args()

    if args.subcommand == 'dev':
        await dev(args, parser=parser)


# This is a separate function (rather than just being in `__main__`) so that we
# can refer to it as a `script` in our `pyproject.rsm.toml` file.
def main():
    try:
        asyncio.run(rsm())
    except KeyboardInterrupt:
        # Don't print an exception and stack trace if the user does a
        # Ctrl-C.
        pass


if __name__ == '__main__':
    main()
