# TODO add credit to RE2
import subprocess  # for Popen
import tempfile  # for NamedTemporaryFile
import os  # for remove


class Gnuplot:
    def __init__(self):
        self.output = "result.png"
        self.script = """
                      set terminal png size 1024, 768
                      set output "{}.png"
                      set title "{}"
                      set datafile separator ";"
                      set logscale y 10
                      set grid x y
                      set ylabel "time"
                      set xlabel "{}"
                      set key noenhanced
                      set title noenhanced
                      set xlabel noenhanced
                      set autoscale
                      plot """
        self.template = """'{}' using 1:5:xticlabels(2) with linespoints linewidth 3 title "{}",\\\n"""
        self.benchdata = dict()
        self.tempfiles = []

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        """
        remove all temporary files
        """

        for filename in self.tempfiles:
            os.remove(filename)

    def gen_csv(self):
        """
        generate temporary csv files
        """

        for name, data in self.benchdata.items():

            with tempfile.NamedTemporaryFile(delete=False) as f:

                for index, line in enumerate(data):
                    # idx;easy;10000000 (?);142 ns/op (?);56.02 MB/s
                    f.write('{};{}\n'.format(
                        str(index),
                        ';'.join([str(line[0]), "0", "0",
                                  str(line[1]['avg'])])).encode())

                self.tempfiles.append(f.name)
                self.script = self.script + self.template.format(f.name, name)

    def run(self):
        self.gen_csv()
        script = self.script[:-3].format(self.output, self.output, self.xlabel)
        command = subprocess.Popen(
            ['gnuplot'], stdin=subprocess.PIPE, cwd="output")
        command.communicate(script.encode())
