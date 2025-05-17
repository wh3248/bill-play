
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def main():
    graph_filters = [
        {"subgrid_size": 1024, "days": 10}
    ]
    line_variables = "server"
    for graph_filter in graph_filters:
        plot_threads_vs_duration(graph_filter, line_variables)

def plot_threads_vs_duration(graph_filter, line_variable_name):

    colors = ["blue", "green", "red"]
    df = pd.read_csv("log_web_server.csv")
    title_values = []
    for graph_filter_key in graph_filter:
        df = df[df[graph_filter_key]==graph_filter[graph_filter_key]]
        title_values.append(str(graph_filter_key.capitalize()) + ": " + str(graph_filter[graph_filter_key]))
    title = ", ".join(title_values)
    parallel_df = df["parallel"].unique()
    parallel_keys = parallel_df.tolist()
    line_variable_keys = df[line_variable_name].unique().tolist()
    number_of_bars = len(line_variable_keys)
    parallel_keys_indexes = np.arange(len(parallel_keys))
    fig, ax1 = plt.subplots()
    bar_width = 1/(number_of_bars+1)
    plot_n = 0
    max_num_error_values = 0
    for line_variable_value in line_variable_keys:
            bar_df = df[df[line_variable_name]==line_variable_value]
            num_errors = bar_df.groupby("parallel")["num_errors"].mean().to_dict()
            num_errors_values = [num_errors[k] for k in parallel_keys]
            max_num_error_values = max(max_num_error_values, max(num_errors_values)) 

    if max_num_error_values > 0:
        ax2 = ax1.twinx()
        for line_variable_value in line_variable_keys:


                bar_df = df[df[line_variable_name]==line_variable_value]

                num_errors = bar_df.groupby("parallel")["num_errors"].mean().to_dict()
                num_errors_values = [num_errors[k] for k in parallel_keys]

                # Draw bars
                offsets = parallel_keys_indexes + bar_width * plot_n
                color_index = int(plot_n)
                ax2.bar(offsets, num_errors_values, bar_width, edgecolor=colors[color_index], color=colors[color_index], label=line_variable_value+" (errors)")


                plot_n = plot_n + 1

    plot_n = 0
    for line_variable_value in line_variable_keys:

            bar_df = df[df[line_variable_name]==line_variable_value]

            max_duration = bar_df.groupby("parallel")["max_call_duration"].mean().to_dict()

            max_duration_values = [max_duration[k] for k in parallel_keys]
            min_duration = bar_df.groupby("parallel")["min_call_duration"].mean().to_dict()
            min_duration_values = [min_duration[k] for k in parallel_keys]

            # Create the line plot
            offsets = parallel_keys_indexes + bar_width*len(line_variable_keys)/2
            color_index = int(plot_n)
            ax1.plot(offsets, max_duration_values, marker="o", color=colors[color_index], label=line_variable_value + " (max)")
            ax1.plot(offsets, min_duration_values, marker="o", color=colors[color_index], label=line_variable_value + " (min)")

            plot_n = plot_n + 1

    # Add labels and title
    ax1.set_zorder(1)
    ax1.patch.set_visible(False)
    if max_num_error_values > 0:
        ax2.set_ylabel('# Errors')
    ax1.set_ylabel('Duration')
    plt.title(title)
    plt.xlabel('# Parallel Calls')
    
    plt.xticks([r + bar_width * 1.5 for r in range(len(parallel_keys_indexes))], parallel_keys)

    graph_file_name = "duration_line_graph.jpg"
    fig.legend(loc=2, bbox_to_anchor=(0.12, .89))
    plt.tight_layout()
    plt.savefig(graph_file_name, format="jpg")
    print(f"Created '{graph_file_name}'")



main()
