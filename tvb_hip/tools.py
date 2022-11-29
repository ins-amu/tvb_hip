"""
This module provides small wrappers for some command line tools
we want to use, with site-specific installation options.

"""

import os
import subprocess
import os.path as op
import logging
import functools

logger = logging.getLogger(__name__)


class Site:
    "Tool installation is site specific."

    fsl_home = None
    freesurfer_home = None
    mrtrix_home = None

    def _log_home(self, tool, home):
        if home is None:
            logger.warn('%s has no home set!', tool)
        else:
            logger.debug('%s in %s', tool, home)

    @functools.cached_property
    def fsl_env(self):
        self._log_home('fsl', self.fsl_home)
        proc = subprocess.Popen(['bash'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        proc.stdin.write(f'''
env > tmp1
source {self.fsl_home}/fslpython/bin/activate
env > tmp2
diff tmp1 tmp2 | grep '>' | sed 's,^> ,,g'
'''.encode('ascii'))
        stdout, _ = proc.communicate()
        fsl_env = os.environ.copy()
        for line in stdout.decode('ascii').strip().split('\n'):
            key, val = line.strip().split("=")
            fsl_env[key] = val
        logger.debug('fsl env is %r', fsl_env)
        return fsl_env

    @functools.cached_property
    def mrt_env(self):
        self._log_home('mrtrix', self.mrtrix_home)
        mrt_env = os.environ.copy()
        mrt_env['PATH'] = os.path.join(self.mrtrix_home, 'bin') + ':' + mrt_env['PATH']
        logger.debug('mrtrix env is %r', mrt_env)
        return mrt_env

    @functools.cached_property
    def fs_env(self):
        self._log_home('freesurfer', self.freesurfer_home)
        proc = subprocess.Popen(['bash'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        proc.stdin.write(f'''
env > tmp1
export FREESURFER_HOME={self.freesurfer_home}
source $FREESURFER_HOME/FreeSurferEnv.sh
env > tmp2
diff -b tmp1 tmp2 | grep '>' | grep -v '_=/usr/bin/env' | sed 's,^> ,,g'
'''.encode('ascii'))
        stdout, stderr = proc.communicate()
        fs_env = os.environ.copy()
        for line in stdout.decode('ascii').strip().split('\n'):
            key, val = line.strip().split("=")
            fs_env[key] = val
        fs_env['PATH'] = ':'.join([fs_env.get('PATH', ''), f'{self.freesurfer_home}/bin:{self.freesurfer_home}/fsfast/bin:{self.freesurfer_home}/tktools:{self.freesurfer_home}/mni/bin'])
        logging.debug('freesurfer env is %r', fs_env)
        return fs_env

    def run_opts(self, env, cmd, *args, stdin=None):
        cmd = [cmd] + [str(_) for _ in args]
        maybe_stdin = {}
        if stdin is not None:
            maybe_stdin['stdin'] = subprocess.PIPE
        logger.debug('cmd = %r', cmd)
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

    def fsl(self, cmd, *args, stdin=None):
        return self.run_opts(self.fsl_env, op.join(self.fsl_home, 'bin', cmd), *args, stdin=stdin)

    def fs(self, cmd, *args, stdin=None):
        return self.run_opts(self.fs_env, op.join(self.freesurfer_home, 'bin', cmd), *args, stdin=stdin)

    def mrt_bin(self, cmd, *args, stdin=None):
        return self.run_opts(self.mrt_env, op.join(self.mrtrix_home, 'bin', cmd), *args, stdin=stdin)

    def tool_ok(self, f, name):
        try:
            f(name)
            return True
        except Exception as exc:
            logger.warn('tool not ok %r', exc)
            return False

    @functools.cached_property
    def fs_ok(self):
        return self.tool_ok(self.fs, 'mri_convert')

    @functools.cached_property
    def mrt_ok(self):
        return self.tool_ok(self.mrt_bin, 'dwifslpreproc')

    @functools.cached_property
    def fsl_ok(self):
        return self.tool_ok(self.fsl, 'flirt')

    @property
    def all_ok(self):
        return self.fs_ok and self.fsl_ok and self.mrt_ok


# might still work
class VepStation(Site):
    fsl_home = '/home/prior/vep_pipeline/fsl'
    freesurfer_home = '/home/prior/vep_pipeline/freesurfer'
    mrtrix_home = '/home/prior/vep_pipeline/mrtrix3-0.3.16'


# probably derps
class InsCluster(Site):
    fsl_home = '/soft/fsl/bin'
    freesurfer_home = '/home/freesurfer-6/bin'
    mrtrix_home = '/soft/mrtrix3-0.3.16/release/bin'


# TODO make this equivalent to the docker image used in hip_deploy
#      repo, and make that repo a submodule of this one or something.
class HIP(Site):
    pass


class Local(Site):
    # guess for typical macos/linux paths
    fsl_home = '/usr/local/fsl'
    freesurfer_home = '/Applications/freesurfer/7.3.2'
    mrtrix_home = '/usr/local/mrtrix3'

