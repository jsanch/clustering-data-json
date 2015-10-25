#!/usr/bin/env python

# General
from __future__ import print_function
from argparse import ArgumentParser
import re
import json
import sys
import os
import logging
import random

# Natural Language 
import nltk
from nltk.stem.snowball import SnowballStemmer

# Data and K-Means
import numpy as np
import pandas as pd
from sklearn import feature_extraction
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from sklearn.manifold import MDS


# Viz
import matplotlib.pyplot as plt
import matplotlib as mpl
import mpld3



def main():
    parser = ArgumentParser('Cluster Data.json Datasets')

    parser.add_argument('filename')
    parser.add_argument('-c','--num-clusters', default=10, type=int, 
                        help = "Specify number of clusters in result")
    parser.add_argument('-f','--num-fits', default=20, type=int, 
                        help = "Specify number of k-mean fits")
    parser.add_argument('--csv', action='store_true',
                        help = "Use if you want output in csv")
    parser.add_argument('--viz', action='store_true',
                        help = "Use if you want a viz output")
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Verbose logging of debug msgs')
    parser.add_argument('--url', type=str,
                       help='data.json endpoint') #to be implemented. 


    args = parser.parse_args()

    # Logging
    
    if args.verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO
    logging.basicConfig(format='%(asctime)s: [%(levelname)s]: %(message)s',
                        level=level)
    logging.getLogger("requests").setLevel(logging.WARNING)

    if args.num_clusters:
        num_clusters = args.num_clusters
    else:
        num_clusters = 10

    if args.num_fits:
        num_fits = args.num_fits
    else:
        num_fits = 20

    # Munching and Crunshing :) 
    
    dataLists = json_to_lists(args.filename)

    vocab_frame = tokenize_corpus(dataLists)

    results = get_tfidf_matrix_and_terms(dataLists['descriptions']) 
    tfidf_matrix = results['tfidf_matrix']
    terms = results['terms']


    dist = 1 - cosine_similarity(tfidf_matrix)

    kresults  = k_means_cluster(tfidf_matrix,dataLists,vocab_frame,terms,dist,num_clusters,num_fits)
    order_centroids = kresults['order_centroids']
    k_clusters_dataframe = kresults['k_clusters_dataframe']
    k_clusters = kresults['k_clusters']


    make_a_d3_plot(dist,vocab_frame,order_centroids,terms,k_clusters,dataLists,num_clusters)




###############################################################################
# Data Parsing
###############################################################################
def json_to_lists(data_json_file):
    with open(data_json_file, 'r') as data_file:
        data = json.load(data_file)

    datasets = data['dataset']

    titles = []
    descriptions =[]
    bureauCodes = [] 
    keywords = [] 
    programCodes  = [] 
    for dataset in datasets:
        titles.append(dataset['title'])
        descriptions.append(dataset['description'])
        try:
            bureauCodes.append(dataset['bureauCode'])
        except:
            bureauCodes.append("")
        try:
            keywords.append(dataset['keyword'])
        except:
            keywords.append("")
        try:
            programCodes.append(dataset['programCode'])
        except:
            programCodes.append("")

    return {'titles':titles,'descriptions':descriptions}


###############################################################################
# Stopwords, stemming, and tokenizing
###############################################################################
stopwords = nltk.corpus.stopwords.words('english') #not really using this

def tokenize_and_stem(text):
    stemmer = SnowballStemmer("english")
    # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
    tokens = [word for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
    filtered_tokens = []
    # filter out any tokens not containing letters (e.g., numeric tokens, raw punctuation)
    for token in tokens:
        if re.search('[a-zA-Z]', token):
            filtered_tokens.append(token)
    stems = [stemmer.stem(t) for t in filtered_tokens]
    return stems

def tokenize_only(text):
    # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
    tokens = [word.lower() for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
    filtered_tokens = []
    # filter out any tokens not containing letters (e.g., numeric tokens, raw punctuation)
    for token in tokens:
        if re.search('[a-zA-Z]', token):
            filtered_tokens.append(token)
    return filtered_tokens



def tokenize_corpus(dataLists):
    totalvocab_stemmed = []
    totalvocab_tokenized = [] 
    for i in dataLists['descriptions']:
        allwords_stemmed = tokenize_and_stem(i) #for each item in 'synopses', tokenize/stem
        totalvocab_stemmed.extend(allwords_stemmed) #extend the 'totalvocab_stemmed' list
        
        allwords_tokenized = tokenize_only(i)
        totalvocab_tokenized.extend(allwords_tokenized)

    vocab_frame = pd.DataFrame({'words': totalvocab_tokenized}, index = totalvocab_stemmed)
    logging.debug('there are ' + str(vocab_frame.shape[0]) + ' items in vocab_frame')
    
    return vocab_frame


################################################################################
# Tf-idf and document similarity
################################################################################
def get_tfidf_matrix_and_terms(text_list):

    # Define vectorizer parameters
    tfidf_vectorizer = TfidfVectorizer(max_df=0.5, max_features=200000,
                                     min_df=0.01, stop_words='english',
                                     use_idf=True, tokenizer=tokenize_and_stem, ngram_range=(1,3))

    tfidf_matrix = tfidf_vectorizer.fit_transform(text_list)


    # Terms is just a list of the features used in the tf-idf matrix. This is a vocabulary
    terms = tfidf_vectorizer.get_feature_names()

    return {'tfidf_matrix':tfidf_matrix,'terms':terms}


###############################################################################
# K-means clustering  
###############################################################################
def k_means_cluster(tfidf_matrix,dataLists,vocab_frame, terms,dist, num_clusters=10, num_fits=20):

    km = KMeans(n_clusters=num_clusters)
    km.fit(tfidf_matrix)
    # fit it several times so that it converges to
    # a global optimum, as k-means is susceptible 
    # to reaching local optima.
    for x in xrange(1,num_fits):
        km.fit(tfidf_matrix) 

    clusters = km.labels_.tolist()

    dsets = { "title" : dataLists['titles'], "description": dataLists['descriptions'], "cluster": clusters}
    frame = pd.DataFrame(dsets, index = [clusters] , columns = ['title', 'cluster', 'description'])


    order_centroids = km.cluster_centers_.argsort()[:, ::-1] 

    for i in range(num_clusters):
        print("Cluster %d words:" % i, end='')
        
        # keywords
        for ind in order_centroids[i, :6]: #replace 6 with n words per cluster
            print(vocab_frame.ix[terms[ind].split(' ')].values.tolist()[0][0].encode('utf-8', 'ignore'), end=',')
        print() #add whitespace
        print() #add whitespace
        
        print("Cluster %d titles:" % i, end='')
        for title in frame.ix[i]['title'].values.tolist():
            print(' %s,' % title, end='\n')
        print() #add whitespace
        print() #add whitespace

    return { 'order_centroids': order_centroids, 'k_clusters_dataframe': frame, 'k_clusters': clusters} 

# def temp(dist,num_clusters=10):

###############################################################################
# Viz
###############################################################################

def generate_colors(n):
    color_list = []
    for c in range(0,n):      
        r = lambda: random.randint(0,255)
        color_list.append( '#%02X%02X%02X' % (r(),r(),r()) )
    return color_list



def make_a_d3_plot(dist,vocab_frame,order_centroids,terms,clusters,dataLists,num_clusters=10):
    MDS()

    # convert two components as we're plotting points in a two-dimensional plane
    # "precomputed" because we provide a distance matrix
    # we will also specify `random_state` so the plot is reproducible.
    mds = MDS(n_components=2, dissimilarity="precomputed", random_state=1)

    pos = mds.fit_transform(dist)  # shape (n_components, n_samples)

    xs, ys = pos[:, 0], pos[:, 1]
    
    color_list = generate_colors(num_clusters)              
    cluster_colors = {}
    for i in range(0,num_clusters):
        cluster_colors[i] = color_list[i]

    # set up cluster names using a dict
    cluster_names = {}
    for i in range(num_clusters):
        for ind in order_centroids[i, :6]:
            if i not in cluster_names:
                cluster_names[i] = vocab_frame.ix[terms[ind].split(' ')].values.tolist()[0][0].encode('utf-8', 'ignore') +','
            else:
                cluster_names[i] = cluster_names[i] + vocab_frame.ix[terms[ind].split(' ')].values.tolist()[0][0].encode('utf-8', 'ignore') +','






    ###############################################################################
    # mpldd3 plot
    ###############################################################################

    # define custom toolbar location
    class TopToolbar(mpld3.plugins.PluginBase):
        """Plugin for moving toolbar to top of figure"""
        dict_ = {"type": "toptoolbar"}
        JAVASCRIPT = """
        mpld3.register_plugin("toptoolbar", TopToolbar);
        TopToolbar.prototype = Object.create(mpld3.Plugin.prototype);
        TopToolbar.prototype.constructor = TopToolbar;
        function TopToolbar(fig, props){
            mpld3.Plugin.call(this, fig, props);
        };

        TopToolbar.prototype.draw = function(){
          // the toolbar svg doesn't exist
          // yet, so first draw it
          this.fig.toolbar.draw();

          // then change the y position to be
          // at the top of the figure
          this.fig.toolbar.toolbar.attr("x", 150);
          this.fig.toolbar.toolbar.attr("y", 400);

          // then remove the draw function,
          // so that it is not called again
          this.fig.toolbar.draw = function() {}
        }
        """
        def __init__(self):
            self.dict_ = {"type": "toptoolbar"}


    #create data frame that has the result of the MDS plus the cluster numbers and titles
    df = pd.DataFrame(dict(x=xs, y=ys, label=clusters, title=dataLists['titles'])) 
    #group by cluster
    groups = df.groupby('label')

    css = """
    text.mpld3-text, div.mpld3-tooltip {
      font-family:Arial, Helvetica, sans-serif;
    }

    g.mpld3-xaxis, g.mpld3-yaxis {
    display: none; }

    svg.mpld3-figure {
    margin-left: -100px;}
    """


    # Plot 
    fig, ax = plt.subplots(figsize=(16,10)) #set plot size
    ax.margins(0.03)

    for name, group in groups:
        points = ax.plot(group.x, group.y, marker='o', linestyle='', ms=18, 
                         label=cluster_names[name], mec='none', 
                         color=cluster_colors[name])
        ax.set_aspect('auto')
        labels = [i for i in group.title]

        #set tooltip using points, labels and the already defined 'css'
        tooltip = mpld3.plugins.PointHTMLTooltip(points[0], labels,
                                           voffset=10, hoffset=10, css=css)
        #connect tooltip to fig
        mpld3.plugins.connect(fig, tooltip, TopToolbar())    
        
        #set tick marks as blank
        ax.axes.get_xaxis().set_ticks([])
        ax.axes.get_yaxis().set_ticks([])
        
        #set axis as blank
        ax.axes.get_xaxis().set_visible(False)
        ax.axes.get_yaxis().set_visible(False)

        
    ax.legend(numpoints=1) #show legend with only one dot

    # mpld3.display() #show the plot

    html = mpld3.fig_to_html(fig)


    with open("index.html", "w") as text_file:
        text_file.write(html)

    #######
    ### plt 
    ########

    from scipy.cluster.hierarchy import ward, dendrogram

    linkage_matrix = ward(dist) #define the linkage_matrix using ward clustering pre-computed distances

    fig, ax = plt.subplots(figsize=(15, 60)) # set size
    ax = dendrogram(linkage_matrix, orientation="right", labels=dataLists['titles']);

    plt.tick_params(\
        axis= 'x',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom='off',      # ticks along the bottom edge are off
        top='off',         # ticks along the top edge are off
        labelbottom='off')

    # plt.tight_layout() #show plot with tight layout

    #uncomment below to save figure
    plt.savefig('ward_clusters.png', dpi=200)



if __name__ == "__main__":
    main()




