import re2
import sys
import json
import time
import re

MATCH_PREFIX = ">>>>"


def getResMatch(res):
    return str((str(res)).split("\'")[1])


def main(pattern, data_file, algo):
    with open(data_file) as f:
        data = f.read()
    # TODO - maybe uncomment and add this with verbose flag
    # print("Alg: %s" % algo)
    # print("search pattern: " + pattern)
    # print("in file: " + data_file)

    if algo == "python":
        cmd = re
    elif algo == "re2":
        cmd = re2
    else:
        raise ("unknown algorithm")

    results = cmd.finditer(pattern, data)

    while True:
        start_time = time.time()
        res = next(results, None)
        end_time = time.time()

        if res:
            pos_str = [res.span()[0], res.span()[1] - 1]
            print(MATCH_PREFIX +
                  json.dumps({
                      "match": getResMatch(res),
                      "span": pos_str,
                      "time": (end_time - start_time) * 1000
                  }))
        else:
            print(MATCH_PREFIX +
                  json.dumps({
                      "match": "EOF",
                      "span": [-1, -1],
                      "time": (end_time - start_time) * 1000
                  }))
            break


if __name__ == "__main__":
    main(*sys.argv[1:])
