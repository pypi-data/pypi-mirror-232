#!/usr/bin/env python
# coding: utf-8



import matplotlib.pyplot as plt
import pandas as pd
import os
from tqdm import tqdm
import seaborn as sns
import plotly.express as px

import glob
from PIL import Image


def gify_plot(original_df,
              plot_type: str, plot_library: str, name: str,
              plot_title: str, xaxis_title: str, yaxis_title: str,
              category: str,
              colors=["blue", "red", "green", "orange", "violet", "yellow", "black", "brown", "cyan"],
              duration=100, loop=0, save_frames=True
              ):
    """
    original_df= a df containg at least three columns: xaxis_title (i.e., x values), yaxis_title (i.e., y values), category(i.e., groups)
    plot_type = line, bar,...
    plot_library = plt, sns...
    name = plot name
    colors = plot el colors
    """

    group_list_dfs = [original_df[original_df[category] == x] for x in original_df[category].unique()]
    X = []
    Y = []
    legend_labels = []  # [0] gives error while [:1] works
    # cannot use spread operator in list comprehensions
    # use for
    for i, df_ in enumerate(group_list_dfs):
        X.append([*df_[xaxis_title].values])
        Y.append([*df_[yaxis_title].values])
        legend_labels.append([*df_[category].values][0])

    try:
        x_all = [x for x in range(min(original_df[xaxis_title]), max(original_df[xaxis_title]))]
    except:
        x_all = [*pd.Series([int(x.split(" ")[0].split("-")[0]) for x in original_df["date"]]).unique()]
        original_df[xaxis_title] = [int(x.split(" ")[0].split("-")[0]) for x in original_df["date"]]

    path = f"./gifs/{plot_library}/{plot_type}/{name}/"
    os.makedirs(path, exist_ok=True)
    print(plot_library, plot_type)
    # in case the user doesnt insert the equal numebrs of X and Y (Y is always the same)
    # if len(Y)==1 and len(X)>1:
    #    temp_y=[]
    #    Y=[Y[0] for i in range(len(X))]
    # init df from data

    try:
        if plot_library == "plt":  # WORKS
            for i, x_ in enumerate(tqdm(x_all)):
                curr_x = x_all[:x_all.index(x_) + 1]

                filt_df = original_df[(original_df[xaxis_title].isin(curr_x))]
                filt_df.sort_values(by=xaxis_title)
                for j, group in enumerate(legend_labels):
                    filt_df2 = filt_df[filt_df[category] == group]
                    if plot_type == "line":
                        plt.plot(filt_df2[xaxis_title], filt_df2[yaxis_title], color=colors[j], label=group)
                    elif plot_type == "bar":
                        plt.bar(filt_df2[xaxis_title], filt_df2[yaxis_title], color=colors[j], label=group)
                    elif plot_type == "scatter":
                        plt.scatter(filt_df2[xaxis_title], filt_df2[yaxis_title], color=colors[j], label=group)
                    elif plot_type == "stackplot":
                        plt.stackplot(filt_df2[xaxis_title], filt_df2[yaxis_title], color=colors[j], label=group)
                # save frame by frame
                plt.xlabel(xaxis_title)
                plt.ylabel(yaxis_title)
                plt.title(plot_title)
                if plot_type != "stackplot":
                    plt.legend()
                plt.xticks(rotation=45)
                plt.savefig(path + f"{i}_{plot_type}_{name}.png", bbox_inches='tight', facecolor="white")
                plt.close()

        elif plot_library == "sns":
            for i, x_ in enumerate(tqdm(x_all)):
                curr_x = x_all[:x_all.index(x_) + 1]

                filt_df = original_df[(original_df[xaxis_title].isin(curr_x))]
                filt_df.sort_values(by=xaxis_title)
                if plot_type == "lineplot":
                    fig = sns.lineplot(x=filt_df[xaxis_title], y=filt_df[yaxis_title], hue=filt_df[category])
                elif plot_type == "scatterplot":
                    fig = sns.scatterplot(x=filt_df[xaxis_title], y=filt_df[yaxis_title], hue=filt_df[category])
                elif plot_type == "barplot":
                    try:
                        fig = sns.barplot(x=filt_df[xaxis_title], y=filt_df[yaxis_title], hue=filt_df[category])
                    except:
                        fig = []
                        continue
                elif plot_type == "swarmplot":
                    fig = sns.swarmplot(x=filt_df[xaxis_title], y=filt_df[yaxis_title], hue=filt_df[category])
                plt.xlabel(xaxis_title)
                plt.ylabel(yaxis_title)
                plt.title(plot_title)
                plt.legend()
                plt.xticks(rotation=45)
                fig.figure.savefig(path + f"{i}_{plot_type}_{name}.png", bbox_inches='tight', facecolor="white")
                plt.close()

        elif plot_library == "px":
            for i, x_ in enumerate(tqdm(x_all)):
                curr_x = x_all[:x_all.index(x_) + 1]

                filt_df = original_df[(original_df[xaxis_title].isin(curr_x))]
                filt_df.sort_values(by=xaxis_title)
                try:
                    if plot_type == "line":
                        fig = px.line(x=filt_df[xaxis_title], y=filt_df[yaxis_title], color=filt_df[category])
                    elif plot_type == "scatter":
                        fig = px.scatter(x=filt_df[xaxis_title], y=filt_df[yaxis_title], color=filt_df[category])
                    elif plot_type == "area":
                        fig = px.area(x=filt_df[xaxis_title], y=filt_df[yaxis_title], color=filt_df[category])
                    elif plot_type == "bar":
                        fig = px.bar(x=filt_df[xaxis_title], y=filt_df[yaxis_title], color=filt_df[category])

                except:
                    continue
                fig.update_layout(xaxis_title=xaxis_title, yaxis_title=yaxis_title, title=plot_title,
                                  legend_title_text='')
                fig.write_image(path + f"{i}_{plot_type}_{name}.png")
                # equivalent of plt.close in px
                fig.data = []
                fig.layout = {}

        #####
        # create gif
        make_gif(path, name + ".gif", duration, loop)
        if not save_frames:
            for file in os.listdir(path):
                if file.endswith(".png"):
                    os.remove(path + "/" + file)
    except Exception as e:
        print("ERROR: ", e)


def make_gif(path, file_name,   duration=100, loop=0):
    frames = [Image.open(image) for image in glob.glob(f"{path}/*.PNG")]
    frame_one = frames[0]
    frame_one.save(path+"/"+file_name, format="GIF", append_images=frames,
               save_all=True, duration=duration, loop=loop)   
            