from ph4monitlib import get_runner
import time
import sys
from sarge import run

# time.sleep(1)

while True:
    runner = get_runner([f'/tmp/upsc.sh', "test"], shell=False)
    runner.preexec_setgrp = False
    # runner.capture_stdout_timeout = None
    # runner.capture_stderr_timeout = None
    runner.capture_stdout_buffer = -1
    runner.capture_stderr_buffer = -1
    runner.stdin = sys.stdin.buffer
    # runner.stdout = sys.stdout.buffer
    # runner.stderr = sys.stdout.buffer
    # runner.do_drain_streams = False
    runner.do_not_block_runner_thread_on_termination = False
    runner.start(wait_running=True, timeout=3.0)
    runner.wait(timeout=3.0)

    # run('/tmp/upsc.sh')


    time.sleep(0.5)

# time.sleep(1)

