import csv
import logging
import shutil
import tempfile
import os
import subprocess
import config
import numpy as np
import pandas as pd
import itertools
from decimal import Decimal
import matplotlib.pyplot as plt

from parameter_cube import ParameterCube
from gnuplot import Gnuplot
from exceptions import UnknownTest
from config import OUTPUT_TYPES, NUMBER_OF_REGEXES_IN_TASK, ALGORITHMS
from collections import defaultdict
from math import sqrt


class Analysis:
    def __init__(self, logs_dir=None, files=[]):
        self.logs = []
        self.logs_dir = Analysis.fix_paths(logs_dir, files)
        self.cube = ParameterCube()
        self.metafile = None

    def _plot_non_consecutive_graph(self, graph_type):
        """TODO: Docstring for _plot_non_consecutive_graph.
        :returns: TODO

        """
        cuts = Cut.all_cuts(self.cube)
        with open('output/detailed_output.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([graph_type])
            writer.writerow(['filename', 'dependant', 'parameters'])

            for i, cut in enumerate(cuts):
                self.cube.populate_cut(cut)
                with Gnuplot() as plot:
                    plot.output = "%s_cut_%d" % (graph_type, i)

                    plot.xlabel = cut.dep
                    plot.benchdata = self._format_data_for_gnuplot(
                        cut, graph_type)
                    plot.run()
                    writer.writerow(
                        [plot.output, cut.dep,
                         cut.parameters.items()])

    def _format_data_for_gnuplot(self, cut, graph_type):
        """TODO: Docstring for _format_data_for_gnuplot.

        """
        formatted_data = defaultdict(list)

        for i, alg_name in enumerate(ALGORITHMS):
            for idx, cut_point in enumerate(cut.data[i]):
                dep_col_names = self.cube.cols[cut.dep]
                formatted_data[alg_name].append(
                    [dep_col_names[idx], cut_point[graph_type]])
        return formatted_data

    def analyze_logs(self):
        shutil.rmtree('output', ignore_errors=True)
        os.makedirs("output")

        self._add_log_data_to_parameter_cube()
        self._add_statistical_information_to_parameter_cube()
        self._plot_graphs()

    def _plot_graphs(self):
        """TODO: Docstring for _plot_graphs.

        :arg1: TODO
        :returns: TODO

        """
        for graph_type in OUTPUT_TYPES:
            if graph_type != 'consecutive_matches':
                self._plot_non_consecutive_graph(graph_type)
            else:
                self._plot_consecutive_graph()

    def _format_data_for_boxchart(self, cell):
        """TODO: Docstring for _format_data_for_boxchart.

        :cell: TODO
        :returns: TODO

        """
        boxdata = []
        for idx, nth_match in enumerate(cell['consecutive_matches']['stats']):
            max_boxes = NUMBER_OF_REGEXES_IN_TASK * \
                        config.BOXCHART_MATCH_LIMIT_PERCENTAGE
            if int(nth_match['count']) > max_boxes:
                break

            boxdata.append([
                "{} | {}".format(idx + 1, int(nth_match['count'])), {
                    'avg': nth_match['avg'],
                    'min_time': nth_match['min_time'],
                    'max_time': nth_match['max_time'],
                    'first_quartile': nth_match['first_quartile'],
                    'median': nth_match['median'],
                    'third_quartile': nth_match['third_quartile']
                }
            ])
        minmax = []
        labels = []

        for match in boxdata:
            labels.append(match[0])
            minmax.append(
                [float(match[1][i]) for i in ('min_time', 'max_time')])
        return boxdata, minmax, labels

    def _plot_consecutive_graph(self):
        """TODO: Docstring for _plot_consecutive_graph.

        :returns: TODO

        """
        iterator = self.cube.data.flat
        cur_coords = iterator.coords
        for cell in iterator:
            boxdata, minmax, labels = self._format_data_for_boxchart(cell)

            output_graph_name = "consecutive matches - {}".format(cur_coords)

            df = pd.DataFrame(np.array(minmax).T.tolist(), columns=labels)

            axes, boxplot = df.plot.box(
                return_type='both',
                figsize=[90, 7],
                fontsize=8,
                rot=90,
                showfliers=False)

            for box_num in range(0, len(labels)):
                q1, median, q3 = [
                    float(boxdata[box_num][1][quart]) for quart in
                    ["first_quartile", 'median', "third_quartile"]
                ]
                boxplot['boxes'][box_num].set_ydata([q1, q1, q3, q3, q1])
                boxplot['medians'][box_num].set_ydata([median, median])

                minimum, maximum = minmax[box_num]

                # Lower whiskers
                boxplot['whiskers'][2 * box_num].set_ydata([minimum, q1])

                # Upper whiskers
                boxplot['whiskers'][2 * box_num + 1].set_ydata([q3, maximum])

            axes.set_ylabel('time')
            axes.set_xlabel("n'th match | #regexes with this many matches")

            point_parameters = [ALGORITHMS[cur_coords[0]]] + [
                list(self.cube.cols.values())[coord_idx][coord]
                for coord_idx, coord in enumerate(cur_coords[1:])
            ]
            title = "consecutive matches with Algorithm: %s,  " % \
                point_parameters[0]
            for i, param in enumerate(point_parameters[1:]):
                title += "%s: %s, " % (list(self.cube.cols.keys())[i], param)
            axes.set_title(title)

            plt.yscale('log')

            plt.savefig("output/%s" % output_graph_name)
            plt.close(axes.get_figure())

            cur_coords = iterator.coords

    def _add_log_data_to_parameter_cube(self):
        for log_file in self.logs_dir:
            if log_file.name.endswith("metafile.csv"):
                self.metafile = log_file
                continue
            log = log_file.name
            self.logs.append(log)

        self.cube.init_table_data_from_cols()
        [self.cube.add_point_from_log(l) for l in self.logs]

    @staticmethod
    def get_stats_of_nth_match(results_filepath, n, matchtype):
        max_time = mean = variance_helper_var = number_of_regexes_matched = \
            Decimal(0)
        quartiles = []
        min_time = Decimal('inf')

        with tempfile.NamedTemporaryFile("w+") as fp:
            for time in Analysis.nth_deltas(results_filepath, n, matchtype):
                min_time = min(time, min_time)
                max_time = max(time, max_time)
                number_of_regexes_matched += 1
                delta = time - mean
                mean += delta / number_of_regexes_matched
                variance_helper_var += delta * (time - mean)
                fp.write('{}\n'.format(time))

            if not number_of_regexes_matched:
                return

            fp.seek(0)
            subprocess.run("sort %s -o %s" % (fp.name, fp.name), shell=True)

            for quartile in [Decimal(n) for n in [0.25, 0.5, 0.75]]:
                fp.seek(0)
                cmd = "tail -n +%d %s | head -1" % (
                    number_of_regexes_matched * quartile, fp.name)
                raw_quartile = subprocess.check_output(cmd, shell=True) \
                                         .decode() \
                                         .strip()
                quartiles.append(raw_quartile)

        variance = variance_helper_var / max(number_of_regexes_matched - 1, 1)
        std = sqrt(variance)

        return [
            number_of_regexes_matched, mean, std, min_time, max_time, quartiles
        ]

    def _add_non_consecutive_match_stats_to_cube(self, matchtype):
        """TODO: Docstring for _add_non_consecutive_match_stats_to_cube.

        :returns: TODO

        """
        iterator = self.cube.data.flat
        cur_coords = iterator.coords
        for cell in iterator:
            stats = Analysis.get_stats_of_nth_match(cell['results'], None,
                                                    matchtype)
            if stats:
                avg = stats[1]
                self.cube.data[cur_coords].update({matchtype: {'avg': avg}})
                cur_coords = iterator.coords

    @staticmethod
    def nth_deltas(results_filepath, n, matchtype):
        """TODO: Docstring for nth_match.

        :arg1: TODO
        :returns: TODO

        """
        cur_pattern = None
        with open(results_filepath) as f:
            for row in csv.DictReader(f):
                if cur_pattern != row['regex']:
                    num_matches = 0
                    cur_pattern = row['regex']

                if row['matchtype'] == matchtype:
                    if matchtype == 'consecutive':
                        num_matches += 1
                        if num_matches == n:
                            yield Decimal(row['time(ms)'])
                    else:
                        yield Decimal(row['time(ms)'])

    def _add_consecutive_match_stats_to_cube(self):
        """TODO: Docstring for _add_consecutive_match_stats_to_cube.

        :returns: TODO

        """
        iterator = self.cube.data.flat
        cur_coords = iterator.coords
        for cell in iterator:
            matches = []
            for i in itertools.count(1):
                if i % 100 == 0:
                    logging.debug("analyzed %s matches for dot %s" %
                                  (i, str(cur_coords)))
                stats = Analysis.get_stats_of_nth_match(
                    cell['results'], i, 'consecutive')
                if not stats:
                    break
                count, avg, std, min_time, max_time, quartiles = stats
                max_boxes = NUMBER_OF_REGEXES_IN_TASK * \
                    config.BOXCHART_MATCH_LIMIT_PERCENTAGE
                if count > max_boxes:
                    break
                first_quartile, median, third_quartile = quartiles

                matches.append({
                    'count': count,
                    'avg': avg,
                    'std': std,
                    'min_time': min_time,
                    'max_time': max_time,
                    'first_quartile': first_quartile,
                    'median': median,
                    'third_quartile': third_quartile
                })
            self.cube.data[cur_coords].update({
                'consecutive_matches': {
                    'stats': matches
                }
            })
            cur_coords = iterator.coords

    def _add_statistical_information_to_parameter_cube(self):
        for test_type in OUTPUT_TYPES:
            if test_type == 'first_match':
                self._add_non_consecutive_match_stats_to_cube('first_match')
            elif test_type == 'consecutive_matches':
                self._add_consecutive_match_stats_to_cube()
            elif test_type == 'all_matches':
                self._add_non_consecutive_match_stats_to_cube('all_matches')
            else:
                raise UnknownTest(test_type)

    @staticmethod
    def fix_paths(text_dir, logs_dir):
        if text_dir and os.path.isdir(text_dir):
            return [
                open(os.path.join(text_dir, f)) for f in os.listdir(text_dir)
            ]
        else:
            return logs_dir


class Cut:
    """Represents a projection of the cube on 3-dim
    """

    def __init__(self, parameters, dep):
        """
        :parameters: a dict with n-1 keys that represent the n-1 fixed axes
        :dep: the free variable, which during analysis will be iterated on
        :data: a column of data from the cube, representing the cut
        Appears here instead of as a parameter, because its role is different

        """

        self.dep = dep
        self.parameters = parameters

        self.data = None

        if dep in self.parameters.keys():
            raise ValueError(
                "dependent variable can't also be a fixed parameter of the cut"
            )

    @staticmethod
    def all_cuts(cube):
        """
        :returns: a list of All possible cuts from the cube onto a single axis
        """
        cuts = []
        cut_variables = [
            var for var in cube.cols.keys() - set(config.SKIP_CUTS)
        ]

        cut_parameters = {k: v for k, v in cube.cols.items()}

        for dependant in cut_variables:
            cur_params = cut_parameters.keys() - [dependant]
            param_configurations = itertools.product(*(cut_parameters[k]
                                                       for k in cur_params))
            param_configurations_with_param_name = [
                dict(zip(cur_params, j)) for j in param_configurations
            ]
            for parameters in param_configurations_with_param_name:
                cuts.append(Cut(parameters, dependant))
        return cuts
