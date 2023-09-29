# coding: utf-8

from matplotlib import pyplot as plt
import numpy as np
import os
import shutil

from pytest_pitch import khuller_moss_naor as KMN
from pytest_donde.outcome import Outcome

''' Demo script to generate (time, coverage) statistics.

This demonstrates the use of pytest_pitch as a library rather than as a pytest plugin.
While pytest is still run in a pre-step, plugin itself is unused.

This can also be used to analyze and compare new algorithmic approaches
without (or before) implementing a new plugin.

Additional dependencies may occur as this is not considered as a functional part of the package.
'''

class MKRBenchmarker:

    def __init__(self, pytest_cmd, src_dir, fname_json):
        self.pytest_cmd = pytest_cmd
        self.src_dir = src_dir
        self.fname_json = fname_json

    def record(self):
        # run donde recorder
        os.system(f'{self.pytest_cmd} --donde={self.src_dir}')
        # backup results
        shutil.copy('donde.json', self.fname_json)

    def visualize(self, outcome, example_name=None, fname=None,
                  plot_ff=True, plot_kmn=True, plot_normal=True):
        T_flow, C_flow = self.compute_session_history_normal(outcome)
        Tmax = T_flow[-1]
        Cmax = C_flow[-1]

        if plot_normal:
            self._visualize_conv_plt(T_flow, C_flow, Tmax, Cmax, '-k',
                                     label='pytest')

        if plot_ff:
            T_ff, C_ff = self.evaluate_data_series_fast_first(outcome)
            self._visualize_conv_plt(T_ff, C_ff, Tmax, Cmax, '-', c='lime',
                                     label='pytest --fast-first')

        if plot_kmn:
            T_kmn, C_kmn = self.compute_session_history_kmn(outcome, Tmax+0.1)
            self._visualize_conv_plt(T_kmn, C_kmn, Tmax, Cmax, '-', c='lime',
                                     label='pytest --pitch')

        plt.xlabel('time $T/T_{tot}$')
        plt.ylabel('coverage $C/C_{tot}$')

        title = ''
        if example_name:
            title += example_name + '\n'
        title += '$T_{{tot}}={:d}$ sec\t'.format(int(Tmax))
        title += '$C_{{tot}}={}$ LOC'.format(Cmax)

        plt.title(title)
        plt.legend()

        if fname is None:
            plt.show()
        else:
            plt.savefig(fname)

    def compute_session_history_normal(self, outcome):
        nodeids = list(sorted(set(outcome.nodeids.val_to_index)))
        return self.compute_session_history(outcome, nodeids)

    def evaluate_data_series_fast_first(self, outcome):
        # simulate pytest-fast-first behavior
        nodeids = list(sorted(set(outcome.nodeids.val_to_index),
                              key=outcome.nodeid_to_duration))
        return self.compute_session_history(outcome, nodeids)

    def compute_session_history_kmn(self, outcome, budget):
        nodeids, _, _ = self._eval_kmn(outcome, budget)
        return self.compute_session_history(outcome, nodeids)

    def compute_session_history(self, outcome, nodeids):
        # compute (time, coverage) value pairs from (0,0) to (1,1)
        # with increasing values for successively adding another nodeid
        T, C = [], []
        for ind in range(len(nodeids)+1):
            nodeids_sub = nodeids[:ind]
            t, c = self.evaluate_data_point_for_test_selection(outcome, nodeids_sub)
            T.append(t)
            C.append(c)
        return T, C

    def evaluate_data_point_for_test_selection(self, outcome, nodeids):
        duration = self._compute_duration(outcome, nodeids)
        coverage = self._compute_coverage(outcome, nodeids)
        return (duration, coverage)

    def _eval_kmn(self, outcome, budget):
            nindices, duration, coverage = KMN.algorithm(outcome.nindex_to_duration, outcome.nindex_to_lindices, budget)
            nodeids = [outcome.nodeids.from_index(nind) for nind in nindices]
            return nodeids, duration, coverage

    def _visualize_conv_plt(self, T, C, Tmax, Cmax, *a, label='', **kw):
        Tn = np.array(T) / Tmax
        Cn = np.array(C) / Cmax
        for i in range(len(T)):
            if Cn[i] > 0.99:
                pos = i
                break
        else:
            pos = len(T)-1

        label += '\n$0.99 C_{{tot}}$ @ ${:02.2f}T_{{tot}}$'.format(Tn[pos])
        plt.plot(Tn, Cn, *a, **kw, label=label)
        return Tn, Cn, Tn[pos]

    def _compute_duration(self, outcome, nodeids):
        return sum(outcome.nodeid_to_duration(nid) for nid in nodeids)

    def _compute_coverage(self, outcome, nodeids):
        covered = set()
        for nodeid in nodeids:
            nindex = outcome.nodeids.to_index(nodeid)
            covered.update(outcome.nindex_to_lindices[nindex])
        return len(covered)


if __name__ == '__main__':
    import sys

    pytest_cmd, src_dir, fname_json = sys.argv[1:]
    b = MKRBenchmarker(pytest_cmd, src_dir, fname_json)

    # you way want to comment out this line to reuse the same donde.json,
    # if you just want to change the processing part
    # b.record()

    outcome = Outcome.from_file(fname_json)
    b.visualize(outcome, example_name='example project', plot_ff=0)

    
