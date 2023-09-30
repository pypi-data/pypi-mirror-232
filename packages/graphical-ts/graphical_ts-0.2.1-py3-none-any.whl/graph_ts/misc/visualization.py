
import plotly.graph_objects as go
import plotly.figure_factory as ff
import plotly.colors as colors
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt

from yfiles_jupyter_graphs import GraphWidget
import networkx as nx
import numpy as np
from netgraph import Graph as vis_ng
from netgraph import InteractiveGraph as vis_ig
import plotly.tools as tls

from pathlib import Path
import skimage.io as sio
import plotly.express as px



def visualize_ts(df, fig_width=1200, fig_height=600, g=None, save_path='./temp.png', pos=None, g_ratio=0.2, **kwargs):

    n_var = len(df.columns)
    n_cols = 1 if g is None else 2
    specs = None if g is None else [[{'rowspan': n_var}, {}]] + [[None, {}]] * (n_var - 1)
    column_widths = None if g is None else [g_ratio, 1-g_ratio]
    fig = make_subplots(rows=len(df.columns), cols=n_cols, 
                        shared_xaxes=True, 
                        vertical_spacing=0.02, 
                        specs=specs, 
                        column_widths=column_widths)


    for i, column in enumerate(df.columns):
        col = 1 if g is None else 2
        fig.add_trace(go.Scatter(x=df.index, y=df[column], name=column, mode='lines'), row=i+1, col=col)
        fig.update_yaxes(title_text=column, row=i+1, col=1)
        
    if g:
        _, ax = plt.subplots()
        _, fig_path = visualize_ng(g, pos=pos, ax=ax, save_fig=save_path, **kwargs)
        img =sio.imread(fig_path);
        figm= px.imshow(img);
        fig.add_trace(figm.data[0], row=1, col=1)
        fig.update_xaxes(showticklabels=False, row=1, col=1)
        fig.update_yaxes(title=None, showticklabels=False, row=1, col=1)
        # fig.update_layout(title=None, margin=dict(l=0, r=0, t=0, b=0), row=1, col=1)

    fig.update_layout(
        width=fig_width, 
        height=fig_height, 
        margin=dict(l=40, r=10, t=10, b=10)  # Adjust these values as desired
    )
    fig.show()


def create_yf(graph):
    colorscale = 'Hot'  # Choose the colorscale
    color_vals = np.array(graph.lags)
    sampled_colors = colors.sample_colorscale(colorscale, color_vals/np.linalg.norm(color_vals))
    generated_colors = {lag: color for lag, color in zip(color_vals, sampled_colors)}
    

    nodes2id = {}
    yf_nodes = []
    for i, n in enumerate(graph.nodes):
        nodes2id[n] = i
        yf_nodes.append(dict(id=i, properties=dict(yf_label=n, data=graph.nodes[n])))
        
    yf_edges = []
    for i, (u, v, lag) in enumerate(graph.edges(keys=True)):
        yf_edges.append(dict(id=i, start=nodes2id[u], end=nodes2id[v], properties=dict(lag=lag)))
        
    def e_color_mapping(index, element):
        return generated_colors[element['properties']['lag']]
    
    def n_color_mapping(index, element):
        return '#AAAAAA'
    
    def n_scale_mapping(index, element):
        return 0.5
    
    w = GraphWidget()
    w.set_nodes(yf_nodes)
    w.set_edge_color_mapping(e_color_mapping)
    w.set_node_color_mapping(n_color_mapping)
    w.set_node_scale_factor_mapping(n_scale_mapping)
    w.set_edges(yf_edges)
    w.directed = True
    return w




def visualize_nx(pgv, pos=None, ax=None, color='red'):
    if pos is None:
        pos = nx.shell_layout(pgv) 
        
    if ax == None:
        ax=plt.gca()
        
    nx.draw(
        pgv, pos, ax=ax, edge_color='black', width=1, linewidths=1,
        node_size=800, node_color=color, alpha=0.6,
        labels={node: node for node in pgv.nodes()}
    )
    
    nx.draw_networkx_edge_labels(
        pgv, pos, 
        ax=ax,
        edge_labels={(u, v): k for (u, v, k) in pgv.edges(keys=True) if u!=v},
        font_color=color
    )
    nx.draw_networkx_edge_labels(
        pgv, pos, 
        ax=ax,
        edge_labels={(u, v): k for (u, v, k) in pgv.edges(keys=True) if u==v},
        label_pos=10,
        font_color=color
    )
    ax.set_axis_off()
    return pos


def visualize_ng(pgv, pos=None, ax=None, color='red', scl=0.6, save_fig=None):
    if pos is None:
        pos = {k: (x*scl, y*scl) for k, (x,y) in nx.shell_layout(pgv).items()}
        
    edge_labels = {(u, v): k for (u, v, k) in pgv.edges(keys=True)}
    
    vis_ng(list(edge_labels.keys()), 
           edge_labels=edge_labels, 
           edge_label_position=0.5, 
           arrows=True, 
           ax=ax, 
           node_labels=True,
           node_size=5,
           node_layout=pos,
           edge_color=color,
           edge_layout='straight',
           )

    if save_fig is not None:
        plt.savefig(save_fig, dpi=300, format='png', bbox_inches='tight')
        return pos, str(Path(save_fig).resolve())
    
    return pos
    
