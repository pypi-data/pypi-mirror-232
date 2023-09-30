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
from datetimerange import DateTimeRange
import datetime

def gify_plot(original_df,
              plot_type: str, plot_library: str, name: str,
              plot_title: str, xaxis_title: str, yaxis_title: str,
              category: str,
              colors=["blue", "red", "green", "orange", "violet", "yellow", "black", "brown", "cyan"],
              duration=100, loop=0, save_frames=True,
              sort_on_x=True, tick_interval=7
              ):
    """
    original_df= a df containg at least three columns: xaxis_title (i.e., x values), yaxis_title (i.e., y values), category(i.e., groups)
    plot_type = line, bar,...
    plot_library = plt, sns...
    name = plot name
    colors = plot el colors
    """
    original_df = original_df.reset_index(drop=True)

    if sort_on_x:
        original_df.sort_values(by=xaxis_title, inplace=True)
    group_list_dfs = [original_df[original_df[category] == x] for x in original_df[category].unique()]
    for i, each in enumerate(group_list_dfs):
        group_list_dfs[i] = group_list_dfs[i].reset_index(drop=True)
    X = []
    Y = []
    legend_labels = []  # [0] gives error while [:1] works
    # cannot use spread operator in list comprehensions
    # use for
    for i, df_ in enumerate(group_list_dfs):
        X.append([*df_[xaxis_title].values])
        Y.append([*df_[yaxis_title].values])
        legend_labels.append([*df_[category].values][0])

    if type(original_df[xaxis_title][0]) != str:  # year in YYYY #if "-" not in original_df[xaxis_title][0]:
        x_all = [x for x in range(min(original_df[xaxis_title]), max(original_df[xaxis_title]))]
    elif "-" in original_df[xaxis_title][0]:
        # instead of using only year in case of yyyy-mm-dd
        # generate the date range!
        # x_all=[*pd.Series([int(x.split(" ")[0].split("-")[0]) for x in original_df["date"]]).unique()]
        # original_df[xaxis_title]=[int(x.split(" ")[0].split("-")[0]) for x in original_df["date"]]
        # if format is only YYYY-MM-DD
        original_df["date"] = [x.split(" ")[0] for x in original_df["date"]]
        raw_unique_dates = [*original_df["date"].sort_values().unique()]
        time_range = DateTimeRange(raw_unique_dates[0], raw_unique_dates[-1])
        x_all = [str(x).split(" ")[0] for x in time_range.range(datetime.timedelta(days=1))]

    path = f"./gifs/{plot_library}/{plot_type}/{name}/"
    os.makedirs(path, exist_ok=True)
    print(plot_library, plot_type)
    # in case the user doesnt insert the equal numebrs of X and Y (Y is always the same)
    # if len(Y)==1 and len(X)>1:
    #    temp_y=[]
    #    Y=[Y[0] for i in range(len(X))]
    # init df from data

    # try:
    if plot_library == "plt":  # WORKS
        for i, x_ in enumerate(tqdm(x_all)):
            curr_x = x_all[:x_all.index(x_) + 1]

            filt_df = original_df[(original_df[xaxis_title].isin(curr_x))]
            filt_df.sort_values(by=xaxis_title)
            old_df_2 = []
            for j, group in enumerate(legend_labels):
                filt_df2 = filt_df[filt_df[category] == group]
                if type(old_df_2) == list:  # empty el
                    margin_bottom = 0
                elif type(old_df_2) != list:
                    margin_bottom = 0  # try a way to implement optimal bottom for plt.bar (stacked)
                if plot_type == "line":
                    plt.plot(filt_df2[xaxis_title], filt_df2[yaxis_title], color=colors[j], label=group)
                elif plot_type == "bar":
                    plt.bar(filt_df2[xaxis_title], filt_df2[yaxis_title], color=colors[j], label=group,
                            bottom=margin_bottom
                            )
                elif plot_type == "scatter":
                    plt.scatter(filt_df2[xaxis_title], filt_df2[yaxis_title], color=colors[j], label=group)
                elif plot_type == "stackplot":
                    plt.stackplot(filt_df2[xaxis_title], filt_df2[yaxis_title], color=colors[j], label=group)
                old_df_2 = filt_df2
            # save frame by frame
            plt.xlabel(xaxis_title)
            plt.ylabel(yaxis_title)
            plt.title(plot_title)
            if plot_type != "stackplot":
                plt.legend()
            plt.xticks(
                rotation=45)  # ticks=[i for i,x in enumerate([*filt_df2[xaxis_title].unique()]) if i%tick_interval==0],
            # labels=[x for i,x in enumerate([*filt_df2[xaxis_title].unique()]) if i%tick_interval==0],

            try:
                if "-" in original_df[xaxis_title][0]:
                    if len(curr_x) <= 100:
                        tick_interval_ = tick_interval
                    elif len(curr_x) > 100 and len(curr_x) <= 300:  # 365/2 = 182.5 (half month)
                        tick_interval_ = tick_interval * 2  # doubles the original tick val in case of too many ticks
                    elif len(curr_x) > 300 and len(curr_x) <= 2000:
                        tick_interval_ = tick_interval * 10  # with tick_interval=7 it equals to 26
                    elif len(curr_x) > 2000:
                        tick_interval_ = tick_interval * 20  # with tick_interval=7 it equals to 26

                    plt.xticks(
                        ticks=[i for i, x in enumerate([*filt_df2[xaxis_title].unique()]) if i % tick_interval_ == 0],
                        labels=[x for i, x in enumerate([*filt_df2[xaxis_title].unique()]) if i % tick_interval_ == 0])
            except:
                pass
            plt.savefig(path + f"{i}_{plot_type}_{name}.png", bbox_inches='tight', facecolor="white")
            plt.close()


    elif plot_library == "sns":
        for i, x_ in enumerate(tqdm(x_all)):
            curr_x = x_all[:x_all.index(x_)]  # +1]

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
            try:
                if "-" in original_df[xaxis_title][0]:
                    if len(curr_x) <= 100:
                        tick_interval_ = tick_interval
                    elif len(curr_x) > 100 and len(curr_x) <= 300:  # 365/2 = 182.5 (half month)
                        tick_interval_ = tick_interval * 2  # doubles the original tick val in case of too many ticks
                    elif len(curr_x) > 300 and len(curr_x) <= 2000:
                        tick_interval_ = tick_interval * 10  # with tick_interval=7 it equals to 26
                    elif len(curr_x) > 2000:
                        tick_interval_ = tick_interval * 20  # with tick_interval=7 it equals to 26

                    fig.set(
                        xticks=[i for i, x in enumerate([*filt_df[xaxis_title].unique()]) if i % tick_interval_ == 0])
            except:
                pass

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
                    fig.update_layout(barmode='stack')


            except:
                continue
            fig.update_layout(xaxis_title=xaxis_title, yaxis_title=yaxis_title, title=plot_title, legend_title_text='')

            fig.write_image(path + f"{i}_{plot_type}_{name}.png")
            # equivalent of plt.close in px
            fig.data = []
            fig.layout = {}

    #####
    # create gif
    try:
        make_gif(path, name + ".gif", duration, loop)
        if not save_frames:
            for file in os.listdir(path):
                if file.endswith(".png"):
                    os.remove(path + "/" + file)
        # except Exception as e:
        #    print("ERROR: ",e)
    except Exception as e:
        print(
            "Impossible to create gif.\n If you have the folder o some files of that folder opened, then close them and retry.")


def make_gif(path, file_name,   duration=100, loop=0):
    frames = [Image.open(image) for image in glob.glob(f"{path}/*.PNG")]
    frame_one = frames[0]
    frame_one.save(path+"/"+file_name, format="GIF", append_images=frames,
               save_all=True, duration=duration, loop=loop)   
            