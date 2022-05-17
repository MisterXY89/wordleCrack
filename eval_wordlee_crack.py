
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

eval_results = pd.read_csv("wordlee_run_results.csv", sep=";")
eval_results.columns = ["time_id", "correct_word", "attempts", "no_attempts", "length", "success"]

#define figure
fig = plt.figure()
ax1 = fig.add_subplot(311)
ax2 = fig.add_subplot(313)

attempts_df = eval_results.groupby("length")[["no_attempts"]].mean()
print(attempts_df)
attempts_df.plot(ax=ax2)

success_df = eval_results.groupby("length")[["success"]].mean()
print(success_df)
success_df.plot(ax=ax1)

plt.savefig(f'wordlee_first_results_plot.jpg')
plt.close()