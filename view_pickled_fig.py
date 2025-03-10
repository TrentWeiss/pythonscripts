#!/usr/bin/env python3
import matplotlib.pyplot as plt, matplotlib.figure
import pickle
import argparse, argcomplete

def view_pickled_fig(*args, filename : str):
    with open(filename, "rb") as f:
        fig : matplotlib.figure.Figure = pickle.load(f)
    plt.figure(fig.number)
    plt.show()
if __name__=="__main__":
    parser = argparse.ArgumentParser(description="View a pickled figure")
    parser.add_argument("filename", help="The pickled figure to view")
    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    view_pickled_fig(**vars(args))
