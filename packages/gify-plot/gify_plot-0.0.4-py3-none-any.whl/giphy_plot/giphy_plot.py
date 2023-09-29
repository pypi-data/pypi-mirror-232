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

def giphy_plot(X:list,Y:list,
               plot_type:str, plot_library:str, name:str,
               plot_title:str, xaxis_title:str, yaxis_title:str,
               legend_labels=[],
               colors=["blue","red","green","orange","violet","yellow","black","brown","cyan"],
              sort_by_x=True, sort_by_y=False
              ):
    """
    X = the set of all x 
    Y = the set of all y
    plot_type = line, bar,...
    plot_library = plt, sns...
    name = plot name
    colors = plot el colors
    """
    
    #check lens
    if(len(pd.Series([len(x) for x in X]).unique())!=1 and len(pd.Series([len(x) for x in X]).unique())!=1 ):
        print("All X and Y elements must have the same length!")
        return
    path=f"./{plot_library}/{plot_type}/{name}/"
    os.makedirs(path,exist_ok=True)
    print(plot_type, plot_library)
    #in case the user doesnt insert the equal numebrs of X and Y (Y is always the same)
    if len(Y)==1 and len(X)>1:
        temp_y=[]
        Y=[Y[0] for i in range(len(X))]
    #init df from data    
    df=pd.DataFrame(columns=["x","y","type"])
    df["x"]=[y for x in X for y in x]
    df["y"]=[y for x in Y for y in x]
    #set legend label if any
    if len(legend_labels)>0:
        df["type"]=[legend_labels[i] for i,x in enumerate(X) for y in x]
    else:
        df["type"]=[str(i) for i,x in enumerate(X) for y in x]
    if sort_by_x==True:
            df.sort_values(by="x",inplace=True)
    if sort_by_y==True:
            df.sort_values(by="y",inplace=True)
    filtered_df=[
        df[df["type"]==x] for x in df["type"].unique()
    ]
    #handle plt
    if plot_library=="plt":      
        for i,x in enumerate(tqdm(X[0])): #all x must have the same len
            for j,el in enumerate(X): #plot multiple lines in case len X|Y >1
                #set legend label if any
                if len(legend_labels)>0:
                    label_=legend_labels[j]
                else:
                    label_=str(j)
                    
                if plot_type=="line":
                    plt.plot(filtered_df[j]["x"][:i], filtered_df[j]["y"][:i], color=colors[j], label=label_)
                elif plot_type=="bar":
                    plt.bar(filtered_df[j]["x"][:i], filtered_df[j]["y"][:i], color=colors[j], label=label_)
                elif plot_type=="scatter":
                    plt.scatter(filtered_df[j]["x"][:i], filtered_df[j]["y"][:i], color=colors[j], label=label_)
                elif plot_type=="stackplot":
                    plt.stackplot(filtered_df[j]["x"][:i], filtered_df[j]["y"][:i], color=colors[j])
                plt.xlabel(xaxis_title)
                plt.ylabel(yaxis_title)
                plt.title(plot_title)
                if plot_type!="stackplot":
                    plt.legend()
                plt.xticks(rotation=45)
                plt.savefig(path+f"{i}_{plot_type}_{name}.png",  bbox_inches='tight', facecolor="white")           
            plt.close()
    #handle sns
    elif plot_library=="sns":
        #different plots
        for i,x in enumerate(tqdm(X[0])):
            if plot_type=="lineplot":
                fig=sns.lineplot(x=df["x"][:i], y=df["y"][:i], hue=df["type"][:i])
            elif plot_type=="scatterplot":
                fig=sns.scatterplot(x=df["x"][:i], y=df["y"][:i], hue=df["type"][:i])
            elif plot_type=="barplot":
                try:
                    fig=sns.barplot(x=df["x"][:i], y=df["y"][:i], hue=df["type"][:i])
                except:
                    fig=[]
                    continue
            elif plot_type=="swarmplot":
                fig=sns.swarmplot(x=df["x"][:i], y=df["y"][:i], hue=df["type"][:i])
            plt.xlabel(xaxis_title)
            plt.ylabel(yaxis_title)
            plt.title(plot_title)
            plt.legend()
            plt.xticks(rotation=45)
            fig.figure.savefig(path+f"{i}_{plot_type}_{name}.png",  bbox_inches='tight', facecolor="white")
            plt.close()

    elif plot_library=="px":
        #different plots
        for i,x in enumerate(tqdm(X[0])):
            try:
                if plot_type=="line":
                    fig=px.line(x=df["x"][:i], y=df["y"][:i], color=df["type"][:i])
                elif plot_type=="scatter":
                    fig=px.scatter(x=df["x"][:i], y=df["y"][:i], color=df["type"][:i])
                elif plot_type=="area":
                    fig=px.area(x=df["x"][:i], y=df["y"][:i], color=df["type"][:i])
                elif plot_type=="bar":
                    fig=px.bar(x=df["x"][:i], y=df["y"][:i], color=df["type"][:i])

            except:
                continue
            fig.update_layout(xaxis_title=xaxis_title, yaxis_title=yaxis_title, title=plot_title, legend_title_text='')
            fig.write_image(path+f"{i}_{plot_type}_{name}.png")
            #equivalent of plt.close in px
            fig.data=[]
            fig.layout={}
    
    
    #handle other libraries
    
    #create gif
    make_gif(path, name+".gif")



def make_gif(path, file_name,   duration=100, loop=0):
    frames = [Image.open(image) for image in glob.glob(f"{path}/*.PNG")]
    frame_one = frames[0]
    frame_one.save(path+"/"+file_name, format="GIF", append_images=frames,
               save_all=True, duration=duration, loop=loop)   
            