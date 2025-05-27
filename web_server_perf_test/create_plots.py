
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def main():
    plot_filters = [
         {"file_path": "plot_1day.jpg",
          "graph_filter": {"subgrid_size": 1024, "days": 1},
          "line_filters": [
              {"server": "gunicorn", "gunicorn_type": "gevent"},
              {"server": "k8_prod", "gunicorn_type": "gthread"},
              {"server": "k8_main", "gunicorn_type": "gthread"},
              {"server": "k8_develop", "gunicorn_type": "gevent"}
         ]},
         {"file_path": "plot_1024.jpg",
          "graph_filter": {"subgrid_size": 1024, "days": 10},
          "line_filters": [
              {"server": "gunicorn", "gunicorn_type": "gevent"},
              {"server": "k8_prod", "gunicorn_type": "gthread"},
              {"server": "k8_main", "gunicorn_type": "gthread"},
              {"server": "k8_develop", "gunicorn_type": "gevent"}
         ]},
         {"file_path": "plot_102400.jpg",
          "graph_filter": {"subgrid_size": 102400, "days": 10},
          "line_filters": [
              {"server": "gunicorn", "gunicorn_type": "gevent"},
              {"server": "k8_prod", "gunicorn_type": "gthread"},
              {"server": "k8_main", "gunicorn_type": "gthread"},
              {"server": "k8_develop", "gunicorn_type": "gevent"}
         ]},
         {"file_path": "plot_102400_prod.jpg",
          "max_y": 160,
          "graph_filter": {"subgrid_size": 102400, "days": 10, "server_worker": 15},
          "line_filters": [
              {"server": "k8_prod", "gunicorn_type": "gthread"},
         ]},
         {"file_path": "plot_102400_gunicorn_8.jpg",
          "max_y": 160,
          "graph_filter": {"subgrid_size": 102400, "days": 10, "server_worker": 8},
          "line_filters": [
              {"server": "gunicorn", "gunicorn_type": "gevent"},
         ]},
         {"file_path": "plot_102400_gunicorn_3.jpg",
          "max_y": 160,
          "graph_filter": {"subgrid_size": 102400, "days": 10, "server_worker": 3},
          "line_filters": [
              {"server": "gunicorn", "gunicorn_type": "gevent"},
         ]},
         {"file_path": "plot_102400_gunicorn_1.jpg",
          "max_y": 160,
          "graph_filter": {"subgrid_size": 102400, "days": 10, "server_worker": 1},
          "line_filters": [
              {"server": "gunicorn", "gunicorn_type": "gevent"},
         ]},
         {"file_path": "plot_1024_prod.jpg",
          "max_y": 7,
          "graph_filter": {"subgrid_size": 1024, "days": 10, "server_worker": 15},
          "line_filters": [
              {"server": "k8_prod", "gunicorn_type": "gthread"},
         ]},
         {"file_path": "plot_1024_gunicorn_3.jpg",
          "max_y": 7,
          "graph_filter": {"subgrid_size": 1024, "days": 10, "server_worker": 3},
          "line_filters": [
              {"server": "gunicorn", "gunicorn_type": "gevent"},
         ]},
         {"file_path": "plot_sleep_0_3.jpg",
          "graph_filter": {"scenario": "sleep", "server_worker": 3},
          "line_filters": [
              {"sleep_time": 0, "gunicorn_type": "gthread"},
              {"sleep_time": 0, "gunicorn_type": "gevent"},
         ]},

         {"file_path": "plot_sleep_0_3_thread.jpg",
          "max_y": 0.3,
          "graph_filter": {"scenario": "sleep", "server_worker": 3},
          "line_filters": [
              {"sleep_time": 0, "gunicorn_type": "gthread"},
         ]},

         {"file_path": "plot_sleep_0_3_gevent.jpg",
          "max_y": 0.3,
          "graph_filter": {"scenario": "sleep", "server_worker": 3},
          "line_filters": [
              {"sleep_time": 0, "gunicorn_type": "gevent"},
         ]},


         {"file_path": "plot_sleep_2_1.jpg",
          "max_y": 120,
          "graph_filter": {"scenario": "sleep", "server_worker": 1},
          "line_filters": [
              {"sleep_time": 2, "gunicorn_type": "gthread"},
         ]},
         {"file_path": "plot_sleep_2_1_gevent.jpg",
          "max_y": 120,
          "graph_filter": {"scenario": "sleep", "server_worker": 1},
          "line_filters": [
              {"sleep_time": 2, "gunicorn_type": "gthread"},
              {"sleep_time": 2, "gunicorn_type": "gevent"},
         ]},
         {"file_path": "plot_sleep_2_3.jpg",
          "max_y": 120,
          "graph_filter": {"scenario": "sleep", "server_worker": 3},
          "line_filters": [
              {"sleep_time": 2, "gunicorn_type": "gthread"},
              {"sleep_time": 2, "gunicorn_type": "gevent"},
         ]},     
         {"file_path": "plot_sleep_2_8.jpg",
          "max_y": 120,
          "graph_filter": {"scenario": "sleep", "server_worker": 8},
          "line_filters": [
              {"sleep_time": 2, "gunicorn_type": "gthread"},
         ]},     
         {"file_path": "plot_sleep_2_10.jpg",
          "max_y": 120,
          "graph_filter": {"scenario": "sleep", "server_worker": 10},
          "line_filters": [
              {"sleep_time": 2, "gunicorn_type": "gthread"},
         ]},     
         {"file_path": "plot_sleep_2_gt3.jpg",
          "max_y": 120,
          "graph_filter": {"scenario": "sleep", "server_thread": 3},
          "line_filters": [
              {"sleep_time": 2, "gunicorn_type": "gthread"},
         ]},     
         {"file_path": "plot_sleep_2_gt1.jpg",
          "max_y": 120,
          "graph_filter": {"scenario": "sleep", "server_thread": 1},
          "line_filters": [
              {"sleep_time": 2, "gunicorn_type": "gthread"},
         ]},     
         {"file_path": "plot_sleep_2_gt8.jpg",
          "max_y": 120,
          "graph_filter": {"scenario": "sleep", "server_thread": 8},
          "line_filters": [
              {"sleep_time": 2, "gunicorn_type": "gthread"},
         ]},     
         {"file_path": "plot_sleep_2_gt16.jpg",
          "max_y": 120,
          "graph_filter": {"scenario": "sleep", "server_thread": 16},
          "line_filters": [
              {"sleep_time": 2, "gunicorn_type": "gthread"},
         ]},     

    ]
    # Create all the plot files
    for plot_filter in plot_filters:
         file_path = plot_filter.get("file_path")
         graph_filter = plot_filter.get("graph_filter")
         line_filters = plot_filter.get("line_filters")
         max_y = plot_filter.get("max_y")
         plot_threads_vs_duration(file_path, graph_filter, line_filters, max_y)

def plot_threads_vs_duration(file_path, graph_filter, line_filters, max_y):
    colors = ["blue", "green", "red", "orange"]
    df = pd.read_csv("log_web_server.csv")

    # Apply graph_filter for combinations for this plot and construct plot title
    title_values = []
    for graph_filter_key in graph_filter:
        df = df[df[graph_filter_key]==graph_filter[graph_filter_key]]
        title_values.append(str(graph_filter_key.capitalize()) + ": " + str(graph_filter[graph_filter_key]))
    title = ", ".join(title_values)

    # Get number of entries on x and y axis for this plot and create matplotlib fig and ax1
    parallel_df = df["parallel"].unique()
    parallel_keys = parallel_df.tolist()
    number_of_bars = len(line_filters)
    parallel_keys_indexes = np.arange(len(parallel_keys))
    fig, ax1 = plt.subplots()
    bar_width = 1/(number_of_bars+1)

    # Compute maximum number of errors in all of the line filters of the graph
    # This is to see if we need to display error bars or not in this plot
    plot_n = 0
    max_num_error_values = 0
    for line_filter in line_filters:
        bar_df = df.copy()
        for line_filter_key in line_filter:
            bar_df = bar_df[bar_df[line_filter_key]==line_filter[line_filter_key]]
        if len(bar_df) > 0:
            num_errors = bar_df.groupby("parallel")["num_errors"].mean().to_dict()
            num_errors_values = [num_errors.get(k, int(k)) for k in parallel_keys]
            max_num_error_values = max(max_num_error_values, max(num_errors_values)) 

    # Plot the error bars first (so they display under the duration lines)
    plot_n = 0
    if max_num_error_values > 0:
        ax2 = ax1.twinx()
        for line_filter in line_filters:
            # Collect the bar_df of the entry for one line filter combination
            bar_df = df.copy()
            line_variable_value_list = []
            for line_filter_key in line_filter:
                bar_df = bar_df[bar_df[line_filter_key]==line_filter[line_filter_key]]
                line_variable_value_list.append(str(line_filter[line_filter_key]))
            line_variable_value = ",".join(line_variable_value_list)

            # Draw the bars for the line filter combination
            if len(bar_df) > 0:
                num_errors = bar_df.groupby("parallel")["num_errors"].mean().to_dict()
                num_errors_values = [num_errors.get(k, int(k)) for k in parallel_keys]

                # Draw bars
                offsets = parallel_keys_indexes + bar_width * (plot_n+1)
                color_index = int(plot_n)
                ax2.bar(offsets, num_errors_values, bar_width, edgecolor=colors[color_index], color=colors[color_index], label=line_variable_value+" (errors)")

            plot_n = plot_n + 1


    # Draw the duration values as line points
    have_plot = False
    plot_n = 0
    for line_filter in line_filters:
        bar_df = df.copy()
        line_variable_value_list = []
        for line_filter_key in line_filter:
            bar_df = bar_df[bar_df[line_filter_key]==line_filter[line_filter_key]]
            line_variable_value_list.append(str(line_filter[line_filter_key]))
        line_variable_value = ",".join(line_variable_value_list)

        if len(bar_df) > 0:
            max_duration = bar_df.groupby("parallel")["max_call_duration"].mean().to_dict()

            max_duration_values = [max_duration.get(k, 0) for k in parallel_keys]
            min_duration = bar_df.groupby("parallel")["min_call_duration"].mean().to_dict()
            min_duration_values = [min_duration.get(k, 0) for k in parallel_keys]

            # Create the line plot
            offsets = parallel_keys_indexes + 3/2 * 1/(len(line_filters)+1)
            color_index = int(plot_n)
            ax1.plot(offsets, max_duration_values, marker="o", color=colors[color_index], label=line_variable_value + " (max)")
            ax1.plot(offsets, min_duration_values, marker="o", color=colors[color_index], label=line_variable_value + " (min)")
            have_plot = True
        plot_n = plot_n + 1

    if have_plot:
        # Add labels and title
        ax1.set_zorder(1)
        ax1.patch.set_visible(False)
        ax1.set_xlim(0)
        if max_y:
            ax1.set_ylim(0, max_y)
        else:
            ax1.set_ylim(0)
        if max_num_error_values > 0:
            ax2.set_ylabel('# Errors')
            ax2.set_ylim(0, max(8, max_num_error_values))
        ax1.set_ylabel('Duration (s)')
        plt.title(title)
        plt.xlabel('# Parallel Calls')
        
        plt.xticks([r + bar_width * 1.5 for r in range(len(parallel_keys_indexes))], parallel_keys)

        fig.legend(loc=2, bbox_to_anchor=(0.12, .89))
        plt.tight_layout()
        plt.savefig(file_path, format="jpg")
        print(f"Created '{file_path}'")
        plt.close()


main()
