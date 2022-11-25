import os
import subprocess
import os.path as op


fsl_home='/home/prior/vep_pipeline/fsl'
freesurfer_home='/home/prior/vep_pipeline/freesurfer'
mrtrix_home='/home/prior/vep_pipeline/mrtrix3-0.3.16'

def _fsl_env():
    proc = subprocess.Popen(['bash'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    proc.stdin.write(f'''
env > tmp1
source {fsl_home}/fslpython/bin/activate
env > tmp2
diff tmp1 tmp2 | grep '>' | sed 's,^> ,,g'
'''.encode('ascii'))
    stdout, _ = proc.communicate()
    fsl_env = os.environ.copy()
    for line in stdout.decode('ascii').strip().split('\n'):
        key, val = line.strip().split("=")
        fsl_env[key] = val
    return fsl_env


def _mrt_env():
    proc = subprocess.Popen(['bash'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    proc.stdin.write(f'''
env > tmp1
source {mrtrix_home}/activate
env > tmp2
diff tmp1 tmp2 | grep '>' | sed 's,^> ,,g'
'''.encode('ascii'))
    stdout, _ = proc.communicate()
    mrt_env = os.environ.copy()
    for line in stdout.decode('ascii').strip().split('\n'):
        key, val = line.strip().split("=")
        mrt_env[key] = val
    return mrt_env



def _fs_env():
    proc = subprocess.Popen(['bash'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    proc.stdin.write(f'''
env > tmp1
export FREESURFER_HOME={freesurfer_home}
source $FREESURFER_HOME/FreeSurferEnv.sh
env > tmp2
diff tmp1 tmp2 | grep '>' | sed 's,^> ,,g'
'''.encode('ascii'))
    stdout, stderr = proc.communicate()
    fs_env = os.environ.copy()
    for line in stdout.decode('ascii').strip().split('\n'):
        key, val = line.strip().split("=")
        fs_env[key] = val
    fs_env['PATH'] = ':'.join([fs_env.get('PATH', ''), f'{freesurfer_home}/bin:{freesurfer_home}/fsfast/bin:{freesurfer_home}/tktools:{freesurfer_home}/mni/bin'])
    return fs_env


def run_opts(env, cmd, *args, stdin=None):
    cmd = [cmd] + [str(_) for _ in args]
    maybe_stdin = {}
    if stdin is not None:
        maybe_stdin['stdin'] = subprocess.PIPE
    proc = subprocess.Popen(
        cmd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        **maybe_stdin
    )
    if stdin is not None:
        proc.stdin.write(stdin.encode('ascii'))
        stdout, stderr = proc.communicate()
    else:
        proc.wait()
        stdout = proc.stdout.read()
    return stdout.decode()


def fsl(cmd, *args, fsl_env=_fsl_env(), stdin=None):
    # return run_opts(fsl_env, '/soft/fsl/bin/' + cmd, *args, stdin=stdin)
    return run_opts(fsl_env, op.join(fsl_home, 'bin', cmd), *args, stdin=stdin)


def fs(cmd, *args, fs_env=_fs_env(), stdin=None):
    # return run_opts(fs_env, '/soft/freesurfer-6/bin/' + cmd, *args, stdin=stdin)
    return run_opts(fs_env, op.join(freesurfer_home, 'bin', cmd), *args, stdin=stdin)


def mrt_bin(cmd, *args, mrt_env=_mrt_env(), stdin=None):
    # return run_opts(mrt_env, '/soft/mrtrix3-0.3.16/release/bin/' + cmd, *args, stdin=stdin)
    return run_opts(mrt_env, op.join(mrtrix_home, 'release/bin', cmd), *args, stdin=stdin)