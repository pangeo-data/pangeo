#!/usr/bin/env python
import os, sys, argparse, subprocess, re, time, logging
from dask.distributed import Client
logger = logging.getLogger(__name__)

def parse_command_line(args, description):
    parser = argparse.ArgumentParser(description=description,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--project",default=os.environ.get("PROJECT"),
                        help="Specify a project id for the case (optional)."
                        "Used for accounting when on a batch system."
                        "The default is user-specified environment variable PROJECT")
    parser.add_argument("--workers", default=0,
                        help="Number of client nodes to launch")
    parser.add_argument("--walltime", default="01:00:00",
                        help="Set the wallclock limit for all nodes. ")

    parser.add_argument("--workdir",
                        default=os.path.join("/glade","scratch",os.environ.get("USER")),
                        help="Set the working diirectory")

    parser.add_argument("--notebookdir",
                        default=os.path.join("/glade","p","work",os.environ.get("USER")),
                        help="Set the working diirectory")

    args = parser.parse_args(args)

    return args.project, args.workers, args.walltime, args.notebookdir, args.workdir

def launch_job(jobname, project, walltime):
    logger.info("submit job {}".format(jobname))
    proc = subprocess.Popen("qsub -A {} -l walltime={} {}".
                            format(project, walltime, jobname),
                            stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                            shell=True)

    output, errput = proc.communicate()
    stat = proc.wait()

    if stat != 0:
        print("ERROR stat {}".format(stat))

    search_jobid = re.search("^(\S+)$", output.decode('utf-8'))
    jobid = search_jobid.group(1)
    return jobid

def start_jlab(dask_scheduler, host=None, port='8888', notebook_dir=''):
    cmd = ['jupyter', 'lab', '--ip', host,
           '--no-browser', '--port', port,
           '--notebook-dir', notebook_dir]
    print(cmd)
    proc = subprocess.Popen(cmd)
    dask_scheduler.jlab_proc = proc

def get_logger(log_level):
    ch = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(' - '.join(
        ["%(asctime)s", "%(name)s", "%(levelname)s", "%(message)s"]))
    ch.setFormatter(formatter)
    logger = logging.getLogger(__file__)
    logger.setLevel(log_level)
    ch.setLevel(log_level)
    logger.addHandler(ch)
    return logger



def setup_jlab(scheduler_file, jlab_port, dash_port, notebook_dir,
        hostname):

    logger.info('getting client with scheduler file: %s' % scheduler_file)
    client = Client(scheduler_file=scheduler_file, timeout=30)
    logger.debug('Client: %s' % client)

    logger.debug('Getting hostname where scheduler is running')
    host = client.run_on_scheduler(socket.gethostname)
    logger.info('host is %s' % host)

    logger.info('Starting jupyter lab on host')
    client.run_on_scheduler(start_jlab, host=host, port=jlab_port,
                            notebook_dir=notebook_dir)
    logger.debug('Done.')

    user = os.environ['USER']
    print('Run the following command from your local machine:')
    print(f'ssh -N -L {jlab_port}:{host}:{jlab_port} '
          f'-L {dash_port}:{host}:8787 {user}@{hostname}')
    print('Then open the following URLs:')
    print(f'\tJupyter lab: http://localhost:{jlab_port}')
    print(f'\tDask dashboard: http://localhost:{dash_port}', flush=True)

def _main_func(args, description):
    project, workers, walltime, notebookdir, workdir = parse_command_line(args, description)
    global logger
    logger = get_logger("DEBUG")

    jobids = []
    jobids.append( launch_job("launch-dask-scheduler.sh", project, walltime))

    for i in range(1,workers):
        jobids.append(launch_job("launch-dask-worker.sh", project, walltime))

    for jobid in jobids:
        wait = True
        while wait:
            proc = subprocess.Popen("qstat {} ".
                                    format(jobid),
                                    stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                                    shell=True)

            output, errput = proc.communicate()
            output = output.decode('utf-8')
            stat = proc.wait()
            if ' R ' in output:
                logger.info(" jobid {} started".format(jobid))
                wait = False
            if ' Q ' in output:
                logger.info(" jobid {} in queue".format(jobid))
                time.sleep(5)

    setup_jlab(jlab_port=8877, dash_port=8878, notebook_dir=notebookdir,
               hostname="cheyenne.ucar.edu",
               scheduler_file=os.path.join(workdir,"scheduler.json"))


if __name__ == "__main__":
    _main_func(sys.argv[1:], __doc__)
